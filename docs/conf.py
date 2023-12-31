import os
import sys

print(os.path.abspath("../flask_taskx"))

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../flask_taskx"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Flask-TaskWorker"
copyright = "2023, Nelson Carrasquel"
author = "Nelson Carrasquel"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

root_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    # Disable showing the sidebar. Defaults to 'false'
    'nosidebar': True,
}