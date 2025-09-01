import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Sphinx Extension - Filter Tabs'
copyright = '2025, Aputsiak Niels Janussen'
author = 'Aputsiak Niels Janussen'
release = '1.2.2'

# -- General configuration ---------------------------------------------------
extensions = [
    'filter_tabs.extension',
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- LaTeX output -------------------------------------------------
# These settings ensure basic compatibility.
latex_elements = {
    'papersize': 'a4paper',
    'classoptions': ',oneside',
    'preamble': r'''
        \setcounter{secnumdepth}{0}  % Disable section numbering
    ''',
}

# Define the LaTeX document structure.
latex_documents = [
    ('index', 'sphinxextension-filtertabs.tex',
     'Sphinx Extension - Filter Tabs Documentation',
     'Aputsiak Niels Janussen', 'manual'),
]

# -- Options for filter-tabs extension ---------------------------------------
filter_tabs_highlight_color = "#d45234"
filter_tabs_debug_mode = True
