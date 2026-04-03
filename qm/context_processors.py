from django.conf import settings


def github_settings(request):
    return {
        'github_repo': getattr(settings, 'GITHUB_REPO', ''),
    }
