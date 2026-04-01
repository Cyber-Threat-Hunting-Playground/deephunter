from rest_framework import authentication, permissions
from rest_framework.exceptions import AuthenticationFailed
from config.models import ApiKey


class ApiKeyUser:
    """Lightweight user-like object for API key authenticated requests."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.pk = f"apikey-{api_key.pk}"
        self.is_authenticated = True
        self.is_active = True
        self.username = f"apikey:{api_key.name}"

    def __str__(self):
        return self.username


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using the existing DeepHunter ApiKey model.
    Supports both ``Authorization: Bearer <key>`` and ``X-API-Key: <key>`` headers.
    """

    def authenticate(self, request):
        api_key = None

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ', 1)[1].strip()

        if not api_key:
            api_key = request.headers.get('X-API-Key', '')

        if not api_key:
            return None

        try:
            key_obj = ApiKey.objects.get(key=api_key)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        return (ApiKeyUser(key_obj), key_obj)

    def authenticate_header(self, request):
        return 'Bearer'


class ApiKeyPermission(permissions.BasePermission):
    """
    Permission check based on ApiKey type.
    - READ keys may only use safe HTTP methods (GET, HEAD, OPTIONS).
    - WRITE keys may use any method.
    - Session-authenticated Django users with ``is_staff`` have full access.
    - Regular session-authenticated users get read-only access.
    """

    def has_permission(self, request, view):
        # Session-authenticated Django users
        user = request.user
        if hasattr(user, 'is_staff'):
            if user.is_authenticated:
                if request.method in permissions.SAFE_METHODS:
                    return True
                return user.is_staff
            return False

        # API key authentication
        auth = request.auth
        if isinstance(auth, ApiKey):
            if request.method in permissions.SAFE_METHODS:
                return True
            return auth.key_type == 'WRITE'

        return False
