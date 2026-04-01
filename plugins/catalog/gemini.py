"""
Gemini AI plugin for DeepHunter

Requirements
------------
- pip install google-genai
- Get an API key: https://aistudio.google.com/app/apikey

Description
-----------
This plugin integrates Google's Gemini AI to suggest MITRE techniques based on a given query.
"""

from django.conf import settings
from connectors.utils import get_connector_conf
import re


def get_connector_metadata():
    return {
        'description': (
            "google-genai (https://github.com/googleapis/python-genai) is an initial "
            "Python client library for interacting with Google's Generative AI APIs.\n\n"
            "Google Gen AI Python SDK provides an interface for developers to integrate "
            "Google's generative models into their Python applications. It supports the "
            "Gemini Developer API and Vertex AI APIs."
        ),
        'domain': 'ai',
        'connector_conf': [
            {
                'key': 'API_KEY',
                'value': 'xxxxxxxxxx',
                'fieldtype': 'password',
                'description': 'Get an API key: https://aistudio.google.com/app/apikey',
            },
            {
                'key': 'MODEL',
                'value': 'gemini-2.0-flash',
                'fieldtype': 'char',
                'description': '"gemini-1.5-flash" (~128K tokens, good for basic tasks) or "gemini-2.5-flash" (1M+ tokens, Higher quality, better reasoning)',
            },
            {
                'key': 'TEMPERATURE',
                'value': '0.0',
                'fieldtype': 'float',
                'description': 'Controls randomness / creativity of the model.\n0.0 = deterministic \u2192 same input always gives same output.\nHigher values (e.g. 0.7) allow more variety or creative phrasing.\nBest for: consistent, factual, extractive outputs.',
            },
            {
                'key': 'TOP_P',
                'value': '1.0',
                'fieldtype': 'float',
                'description': 'Also known as nucleus sampling.\nThe model picks from the smallest set of words whose total probability adds up to top_p.\n1.0 means use the entire probability distribution (no filtering).\nLower values (e.g. 0.8) force more focused outputs but can reduce variety.',
            },
            {
                'key': 'TOP_K',
                'value': '0',
                'fieldtype': 'int',
                'description': 'Limits the model to selecting from the top K most likely next tokens.\n0 means no limit \u2014 let top_p fully control the sampling.\nIf set to e.g. top_k=40, the model only chooses from the top 40 likely options.\nBest left at 0 when using top_p=1.0.',
            },
            {
                'key': 'MAX_OUTPUT_TOKENS',
                'value': '128',
                'fieldtype': 'int',
                'description': 'Caps the length of the model\'s response (number of tokens).\n128 tokens \u2248 ~90\u2013100 words (depending on the language and structure).\nSet higher if you expect longer responses.',
            },
        ],
    }

_globals_initialized = False
def init_globals():
    global DEBUG, PROXY, API_KEY, TEMPERATURE, TOP_P, TOP_K, MAX_OUTPUT_TOKENS, MODEL
    global _globals_initialized
    if not _globals_initialized:
        DEBUG = False
        PROXY = settings.PROXY
        API_KEY = get_connector_conf('gemini', 'API_KEY')
        MODEL = get_connector_conf('gemini', 'MODEL')
        TEMPERATURE = float(get_connector_conf('gemini', 'TEMPERATURE'))
        TOP_P = float(get_connector_conf('gemini', 'TOP_P'))
        TOP_K = int(get_connector_conf('gemini', 'TOP_K'))
        MAX_OUTPUT_TOKENS = int(get_connector_conf('gemini', 'MAX_OUTPUT_TOKENS'))
        _globals_initialized = True

def get_requirements():
    return ['google-genai']

def get_mitre_techniques_from_query(query):
    from google import genai
    from google.genai.types import GenerateContentConfig
    init_globals()

    client = genai.Client(api_key=API_KEY)

    prompt = f"""
    List only the MITRE ATT&CK TTP IDs (e.g., T1059, T1021.002) that match this query. No descriptions, no explanation.

    Query:
    {query}
    """

    config = GenerateContentConfig(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config
    )

    mitre_ttps = re.findall(r'T\d{4}(?:\.\d{3})?', response.text)

    return list(set(mitre_ttps))

def write_query_with_ai(prompt):
    from google import genai
    from google.genai.types import GenerateContentConfig
    init_globals()

    client = genai.Client(api_key=API_KEY)

    config = GenerateContentConfig(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config
    )

    return response.text
