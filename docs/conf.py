import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Sphinx Extension - Filter Tabs'
copyright = '2025, Aputsiak Niels Janussen'
author = 'Aputsiak Niels Janussen'
release = '0.9.2'

# -- General configuration ---------------------------------------------------
extensions = [
    'filter_tabs.extension',
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------
# LaTeX settings - Adding 'oneside' and 'a4paper' options
latex_elements = {
    'papersize': 'a4paper',
    'classoptions': ',oneside',
}

# LaTeX document settings
latex_documents = [
    ('index', 'sphinxextension-filtertabs.tex',
     'Sphinx Extension - Filter Tabs Documentation',
     'Aputsiak Niels Janussen', 'manual'),
]

# LaTeX document settings
latex_documents = [
    ('index', 'sphinxextension-filtertabs.tex', 
     'Sphinx Extension - Filter Tabs Documentation',
     'Aputsiak Niels Janussen', 'manual'),
]

# -- Options for filter-tabs extension ---------------------------------------
filter_tabs_tab_highlight_color = "#d45234"
filter_tabs_border_radius = "4px"
filter_tabs_debug_mode = True
filter_tabs_keyboard_navigation = True
filter_tabs_announce_changes = True
