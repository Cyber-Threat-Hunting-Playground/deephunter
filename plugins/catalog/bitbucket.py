"""
Bitbucket connector
Used for repo sync with Bitbucket

This module is intentionally free of Django / DeepHunter imports so it can be
used (and tested) as a standalone library.  Call ``init_globals()`` once before
use to inject runtime configuration; sensible defaults are applied otherwise.
"""

from urllib.parse import urlparse
from pathlib import Path
import logging
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


def get_connector_metadata():
    return {
        'description': 'Bitbucket repo sync',
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

def parse_bitbucket_url(url):
    init_globals()

    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    # Expected:
    #   https://bitbucket.org/<owner>/<repo>/src/<branch>/<optional path...>
    if len(parts) < 4 or parts[2] != 'src':
        raise ValueError(
            "Invalid Bitbucket URL. Expected: https://bitbucket.org/<owner>/<repo>/src/<branch>/<path>"
        )
    repo_owner = parts[0]
    repo_slug = parts[1]
    branch = parts[3]
    path = '/'.join(parts[4:]) if len(parts) > 4 else ''
    return repo_owner, repo_slug, branch, path

def get_bitbucket_contents(repo):
    """
    Returns a list of JSON files in a Bitbucket repo
    :param repo: The repo object
    :return: A list of JSON files or empty list if error
    """
    init_globals()

    full = []
    try:
        repo_owner, repo_slug, branch, path = parse_bitbucket_url(repo.url)
    except Exception as e:
        _on_error(f"Bitbucket connector: invalid repo URL {repo.url}: {e}")
        return []
    if path:
        api_url = f"https://api.bitbucket.org/2.0/repositories/{repo_owner}/{repo_slug}/src/{branch}/{path}"
    else:
        api_url = f"https://api.bitbucket.org/2.0/repositories/{repo_owner}/{repo_slug}/src/{branch}/"

    auth = HTTPBasicAuth(repo_owner, repo.token) if repo.token else None
    try:
        response = requests.get(
            api_url,
            auth=auth,
            proxies=PROXY,
            timeout=HTTP_TIMEOUT,
        )
    except requests.Timeout as e:
        _on_error(
            f"Bitbucket connector: timeout calling Bitbucket API: {api_url} "
            f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
        )
        return []
    except requests.RequestException as e:
        _on_error(
            f"Bitbucket connector: failed to call Bitbucket API: {api_url} "
            f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
        )
        return []
    
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError as e:
            _on_error(
                f"Bitbucket connector: invalid JSON response from {api_url} (repo: {repo.url}): {e}"
            )
            return []

        for item in data.get('values', []):
            if item['type'] == 'commit_file' and Path(item['path']).suffix == ".json":
                full.append({
                    "name": item['path'],
                    "download_url": item['links']['self']['href']
                })

        # Bitbucket is paginating results. The "next" key returns the URL of the next page results
        while data.get("next"):
            api_url = data["next"]
            try:
                response = requests.get(
                    api_url,
                    auth=auth,
                    proxies=PROXY,
                    timeout=HTTP_TIMEOUT,
                )
            except requests.Timeout as e:
                _on_error(
                    f"Bitbucket connector: timeout calling Bitbucket API: {api_url} "
                    f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
                )
                break
            except requests.RequestException as e:
                _on_error(
                    f"Bitbucket connector: failed to call Bitbucket API: {api_url} "
                    f"(repo: {repo.url}, timeout={HTTP_TIMEOUT}): {e}"
                )
                break

            if response.status_code != 200:
                details = (response.text or "").strip().replace("\n", " ")
                if len(details) > 300:
                    details = details[:300] + "..."
                _on_error(
                    f"Bitbucket connector: error (status code {response.status_code}) calling {api_url} "
                    f"(repo: {repo.url}). Response: {details}"
                )
                break

            try:
                data = response.json()
            except ValueError as e:
                _on_error(
                    f"Bitbucket connector: invalid JSON response from {api_url} (repo: {repo.url}): {e}"
                )
                break

            for item in data.get('values', []):
                if item['type'] == 'commit_file' and Path(item['path']).suffix == ".json":
                    full.append({
                        "name": item['path'],
                        "download_url": item['links']['self']['href']
                    })

        return full

    # In case of an error
    details = (response.text or "").strip().replace("\n", " ")
    if len(details) > 300:
        details = details[:300] + "..."
    _on_error(
        f"Bitbucket connector: error (status code {response.status_code}) calling {api_url} "
        f"(repo: {repo.url}). Response: {details}"
    )
    return []
