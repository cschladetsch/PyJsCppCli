Ask CLI Documentation
=====================

Welcome to Ask CLI's documentation! Ask CLI is a powerful command-line interface 
for interacting with Claude AI models, providing both interactive and non-interactive 
modes for seamless AI assistance.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   configuration
   api_reference
   development
   contributing

Features
--------

* **Interactive Mode**: Engage in continuous conversations with Claude
* **Command-Line Mode**: Quick one-off queries without entering interactive mode
* **File Upload Support**: Share files with Claude for analysis
* **Rich Terminal UI**: Color-coded output and animated progress indicators
* **Conversation Management**: Save, view, and clear conversation history
* **Async Architecture**: Multi-threaded design for better performance
* **Extensible Configuration**: YAML/JSON configuration with environment variable support

Quick Start
-----------

Install dependencies::

    pip install -r requirements.txt

Set up your API key::

    export CLAUDE_API_KEY="your-api-key-here"

Run interactively::

    python main.py

Or make quick queries::

    python main.py "What is the capital of France?"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`