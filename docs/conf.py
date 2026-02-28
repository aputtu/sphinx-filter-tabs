import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version
from pathlib import Path

# Make the package importable when building docs without installing it first.
sys.path.insert(0, str(Path(__file__).parent.parent))

project = "Sphinx Extension - Filter Tabs"
copyright = "2025-2026, Aputsiak Niels Janussen"
author = "Aputsiak Niels Janussen"

try:
    release = _get_version("sphinx-filter-tabs")
except PackageNotFoundError:
    release = "unknown"

# -- General configuration ---------------------------------------------------
extensions = [
    "filter_tabs",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# -- HTML output -------------------------------------------------------------
html_theme = "sphinx_rtd_theme"

# -- LaTeX output ------------------------------------------------------------
latex_elements = {
    "papersize": "a4paper",
    "classoptions": ",oneside",
    "preamble": r"""
        \setcounter{secnumdepth}{0}  % Disable section numbering
    """,
}

latex_documents = [
    (
        "index",
        "sphinxextension-filtertabs.tex",
        "Sphinx Extension - Filter Tabs Documentation",
        "Aputsiak Niels Janussen",
        "manual",
    ),
]

# -- Options for filter-tabs extension ---------------------------------------
filter_tabs_highlight_color = "#d45234"
filter_tabs_debug_mode = False
