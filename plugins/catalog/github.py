"""
GitHub connector
Used for repo sync with GitHub
"""

from urllib.parse import urlparse
import requests
from django.conf import settings
from pathlib import Path
from notifications.utils import add_error_notification


def get_connector_metadata():
    return {
        'description': 'Github repo sync',
        'domain': 'repos',
        'connector_conf': [],
    }

_globals_initialized = False
def init_globals():
    global DEBUG, PROXY, HTTP_TIMEOUT
    global _globals_initialized
    if not _globals_initialized:
        DEBUG = False
        PROXY = settings.PROXY
        # Prevent connector calls from hanging indefinitely on network issues.
        # Tuple form is (connect timeout seconds, read timeout seconds).
        HTTP_TIMEOUT = getattr(settings, "REPO_CONNECTOR_HTTP_TIMEOUT", (5, 30))
        _globals_initialized = True

def get_requirements():
    return ['requests']

def parse_github_url(url):
    init_globals()

    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    owner = parts[0]
    repo = parts[1]
    # Find if 'tree' is present and get the path after branch name
    if 'tree' in parts:
        tree_index = parts.index('tree')
        branch = parts[tree_index + 1]
        path = '/'.join(parts[tree_index + 2:])
    else:
        branch = None
        path = ''
    return owner, repo, branch, path

def get_github_contents(repo):
    """
    Returns a list of JSON files in a GitHub repo
    :param repo: The repo object
    :return: A list of JSON files or empty list if error
    """
    init_globals()

    owner, repo_name, branch, path = parse_github_url(repo.url)
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    
    if repo.token:
        headers = {
            "Authorization": f"token {repo.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    else:
        headers = {}
    
    try:
        response = requests.get(
            api_url,
            headers=headers,
            proxies=PROXY,
            timeout=HTTP_TIMEOUT,
        )
    except requests.Timeout as e:
        add_error_notification(
            f"GitHub connector: timeout calling GitHub API: {api_url} "
            f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
        )
        return []
    except requests.RequestException as e:
        add_error_notification(
            f"GitHub connector: failed to call GitHub API: {api_url} "
            f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
        )
        return []
    
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "name": item['name'],
                "download_url": item['download_url']
            }
            for item in data
            if item['type'] == 'file' and Path(item['name']).suffix == ".json"
        ]

    # In case of an error
    details = (response.text or "").strip().replace("\n", " ")
    if len(details) > 300:
        details = details[:300] + "..."
    add_error_notification(
        f"GitHub connector: error (status code {response.status_code}) calling {api_url} "
        f"(repo: {repo.url}). Response: {details}"
    )
    return []
