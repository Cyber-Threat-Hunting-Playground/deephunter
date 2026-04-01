"""
GitHub connector
Used for repo sync with GitHub

This module is intentionally free of Django / DeepHunter imports so it can be
used (and tested) as a standalone library.  Call ``init_globals()`` once before
use to inject runtime configuration; sensible defaults are applied otherwise.
"""

from urllib.parse import urlparse
from pathlib import Path
import logging
import requests

logger = logging.getLogger(__name__)


def get_connector_metadata():
    return {
        'description': 'Github repo sync',
        'domain': 'repos',
        'connector_conf': [],
    }

_globals_initialized = False
_on_error = logger.error

def init_globals(proxy=None, timeout=(5, 30), on_error=None):
    """Inject runtime configuration.

    Parameters
    ----------
    proxy : dict | None
        ``requests``-compatible proxy mapping.  Defaults to ``{}``.
    timeout : tuple | int
        ``requests`` timeout (connect, read).  Defaults to ``(5, 30)``.
    on_error : callable | None
        Single-argument callable invoked with an error message string.
        Defaults to ``logger.error``.
    """
    global DEBUG, PROXY, HTTP_TIMEOUT, _on_error
    global _globals_initialized
    if on_error is not None:
        _on_error = on_error
    if not _globals_initialized:
        DEBUG = False
        PROXY = proxy if proxy is not None else {}
        HTTP_TIMEOUT = timeout
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
        _on_error(
            f"GitHub connector: timeout calling GitHub API: {api_url} "
            f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
        )
        return []
    except requests.RequestException as e:
        _on_error(
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
    _on_error(
        f"GitHub connector: error (status code {response.status_code}) calling {api_url} "
        f"(repo: {repo.url}). Response: {details}"
    )
    return []
    