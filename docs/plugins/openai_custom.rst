OpenAI Custom
#############

Description
***********
This plugin integrates any OpenAI-compatible server (e.g. Ollama, vLLM, LM Studio, llama.cpp, LocalAI) to suggest MITRE techniques based on a given query.

Unlike the standard OpenAI plugin, this one lets you configure a custom BASE_URL so requests are sent to your own server instead of the OpenAI cloud.

Settings
********

BASE_URL
========

- **Type**: url
- **Description**: Base URL of your OpenAI-compatible server.
- **Example**: 

.. code-block:: python

	BASE_URL = 'http://localhost:11434/v1'

.. note::

  Common values: ``http://localhost:11434/v1`` for Ollama, ``http://localhost:8000/v1`` for vLLM.

API_KEY
=======

- **Type**: password
- **Description**: API key for the custom server. Use ``not-needed`` if the server does not require authentication.
- **Example**: 

.. code-block:: python

	API_KEY = 'not-needed'

MODEL
=====

- **Type**: string
- **Description**: Model name served by your custom server (e.g. ``llama3``, ``mistral``, ``codellama``).
- **Example**: 

.. code-block:: python

	MODEL = 'llama3'
