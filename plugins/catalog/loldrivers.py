"""
LOLDrivers connector
"""

from connectors.utils import get_connector_conf
import requests
from django.conf import settings


def get_connector_metadata():
    return {
        'description': 'Living Off The Land Drivers is a curated list of Windows drivers used by adversaries to bypass security controls and carry out attacks. The project helps security professionals stay informed and mitigate potential threats.',
        'domain': 'extensions',
        'connector_conf': [],
    }

_globals_initialized = False
def init_globals():
    global DEBUG, PROXY
    global _globals_initialized
    if not _globals_initialized:
        DEBUG = False
        PROXY = settings.PROXY
        _globals_initialized = True

def get_requirements():
    return ['requests', 'beautifulsoup4']

def get_sha256_hashes():
    """
    Fetches SHA256 hashes of LOLDrivers from the website.
    :return: A list of SHA256 hashes found on the LOLDrivers website.
    """
    from bs4 import BeautifulSoup
    init_globals()
    lol_hashes = []
    response = requests.get(
        'https://www.loldrivers.io/',
        proxies=PROXY
        )
    soup = BeautifulSoup(response.text, "lxml")
    #Created a list of lol driver SHA256 hashes
    for link in soup.find_all("a", href=True):
        if len(link.text) == 64:
            lol_hashes.append(str(link.text))
    return lol_hashes
