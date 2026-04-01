"""
EntraID plugin for DeepHunter

Requirements
------------
pip install Authlib

Description
-----------
This plugin integrates EntraID.
"""

from django.conf import settings
from connectors.utils import get_connector_conf
import ast


def get_connector_metadata():
    return {
        'description': (
            "Entra ID is the new name for Microsoft's cloud-based identity and access "
            "management service, formerly known as Azure Active Directory. It helps "
            "organizations manage and secure user identities to control access to "
            "applications, data, and resources across multicloud and on-premises "
            "environments. Entra ID uses Zero Trust principles to ensure that only "
            "authenticated and authorized users can access what they need."
        ),
        'domain': 'authentication',
        'connector_conf': [
            {
                'key': 'CLIENT_ID',
                'value': 'thisisclientid',
                'fieldtype': 'char',
                'description': 'The Client ID provided by Entra ID for OAuth2 authentication.',
            },
            {
                'key': 'CLIENT_SECRET',
                'value': '**************',
                'fieldtype': 'password',
                'description': 'The Client Secret provided by Entra ID for OAuth2 authentication.',
            },
            {
                'key': 'SERVER_METADATA_URL',
                'value': 'https://login.microsoftonline.com/foo-blah-replace-content/.well-known/openid-configuration',
                'fieldtype': 'char',
                'description': 'The Server Metadata URL for Entra ID.',
            },
            {
                'key': 'SCOPE',
                'value': 'openid profile email',
                'fieldtype': 'char',
                'description': 'Additional parameters for the client.',
            },
            {
                'key': 'AUTH_TOKEN_MAPPING_USERNAME',
                'value': 'unique_name',
                'fieldtype': 'char',
                'description': 'Authentication token mapping for username.',
            },
            {
                'key': 'AUTH_TOKEN_MAPPING_FIRST_NAME',
                'value': 'given_name',
                'fieldtype': 'char',
                'description': 'Authentication token mapping for first name.',
            },
            {
                'key': 'AUTH_TOKEN_MAPPING_LAST_NAME',
                'value': 'family_name',
                'fieldtype': 'char',
                'description': 'Authentication token mapping for last name.',
            },
            {
                'key': 'AUTH_TOKEN_MAPPING_EMAIL',
                'value': 'upn',
                'fieldtype': 'char',
                'description': 'Authentication token mapping for email.',
            },
            {
                'key': 'AUTH_TOKEN_MAPPING_GROUPS',
                'value': 'roles',
                'fieldtype': 'char',
                'description': 'Authentication token mapping for groups.',
            },
            {
                'key': 'USER_GROUPS_MEMBERSHIP',
                'value': "{'viewer': 'AD_deephunter_usr', 'manager': 'AD_deephunter_pr'}",
                'fieldtype': 'char',
                'description': 'User groups membership mapping.',
            },
        ],
    }

_globals_initialized = False
def init_globals():
    global DEBUG, PROXY, CLIENT_ID, CLIENT_SECRET, SERVER_METADATA_URL, SCOPE, AUTH_TOKEN_MAPPING
    global AUTHLIB_OAUTH_CLIENTS, oauth, AUTH_TOKEN_MAPPING_USERNAME, AUTH_TOKEN_MAPPING_FIRST_NAME
    global AUTH_TOKEN_MAPPING_LAST_NAME, AUTH_TOKEN_MAPPING_EMAIL, AUTH_TOKEN_MAPPING_GROUPS, USER_GROUPS_MEMBERSHIP
    global _globals_initialized
    if not _globals_initialized:
        from authlib.integrations.django_client import OAuth
        DEBUG = False
        PROXY = settings.PROXY
        CLIENT_ID = get_connector_conf('entraid', 'CLIENT_ID')
        CLIENT_SECRET = get_connector_conf('entraid', 'CLIENT_SECRET')
        SERVER_METADATA_URL = get_connector_conf('entraid', 'SERVER_METADATA_URL')
        SCOPE = get_connector_conf('entraid', 'SCOPE')
        AUTH_TOKEN_MAPPING_USERNAME = get_connector_conf('entraid', 'AUTH_TOKEN_MAPPING_USERNAME')
        AUTH_TOKEN_MAPPING_FIRST_NAME = get_connector_conf('entraid', 'AUTH_TOKEN_MAPPING_FIRST_NAME')
        AUTH_TOKEN_MAPPING_LAST_NAME = get_connector_conf('entraid', 'AUTH_TOKEN_MAPPING_LAST_NAME')
        AUTH_TOKEN_MAPPING_EMAIL = get_connector_conf('entraid', 'AUTH_TOKEN_MAPPING_EMAIL')
        AUTH_TOKEN_MAPPING_GROUPS = get_connector_conf('entraid', 'AUTH_TOKEN_MAPPING_GROUPS')
        USER_GROUPS_MEMBERSHIP = get_connector_conf('entraid', 'USER_GROUPS_MEMBERSHIP')
        oauth = OAuth()
        oauth.register(
            name='entra_id',
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            server_metadata_url=SERVER_METADATA_URL,
            client_kwargs={'scope': SCOPE}
        )
        _globals_initialized = True

def get_requirements():
    return ['Authlib']

def sso(request, redirect_uri):
    init_globals()
    return oauth.entra_id.authorize_redirect(request, redirect_uri)

def get_token(request):
    init_globals()
    token = oauth.entra_id.authorize_access_token(request)
    return token

def get_token_mapping():
    init_globals()
    return {
        'username': AUTH_TOKEN_MAPPING_USERNAME,
        'first_name': AUTH_TOKEN_MAPPING_FIRST_NAME,
        'last_name': AUTH_TOKEN_MAPPING_LAST_NAME,
        'email': AUTH_TOKEN_MAPPING_EMAIL,
        'groups': AUTH_TOKEN_MAPPING_GROUPS
    }

def get_user_groups_membership():
    init_globals()
    # Convert the string containing a dictionary into an actual Python dictionary object
    # Input must use single quotes
    return ast.literal_eval(USER_GROUPS_MEMBERSHIP)
