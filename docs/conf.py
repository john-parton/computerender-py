"""Sphinx configuration."""
project = "Computerender"
author = "John Parton"
copyright = "2022, John Parton"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
