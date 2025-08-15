import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Sphinx Extension - Filter Tabs'
copyright = '2025, Aputsiak Niels Janussen'
author = 'Aputsiak Niels Janussen'
release = '0.8.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'filter_tabs.extension',
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'

# THE FIX: Tell Sphinx to look for a '_static' directory for custom files.
# This enables Sphinx to correctly find and copy the CSS from the extension.
html_static_path = ['_static']

# -- Options for filter-tabs extension ---------------------------------------
filter_tabs_tab_highlight_color = "#d45234"
filter_tabs_border_radius = "4px"
filter_tabs_debug_mode = True
