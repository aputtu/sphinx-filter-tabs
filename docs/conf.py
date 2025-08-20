import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Sphinx Extension - Filter Tabs'
copyright = '2025, Aputsiak Niels Janussen'
author = 'Aputsiak Niels Janussen'
release = '0.9.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'filter_tabs.extension',
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- LaTeX output ------------------------------------------------
# Uses your existing index.rst source file
latex_documents = [
    ('index', 'sphinxextension-filtertabs.tex', 'Sphinx Extension - Filter Tabs Documentation',
     'Aputsiak Niels Janussen', 'manual'),
]

# LaTeX settings optimized for A4 single-page output without blank pages
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '9pt',
    'geometry': r'\usepackage[a4paper,margin=1.5cm]{geometry}',
    'fncychap': r'\usepackage[Bjarne]{fncychap}',
    'classoptions': ',oneside',  # Force single-sided layout - this prevents blank pages
    'preamble': r'''
        \usepackage{charter}
        \usepackage[defaultsans]{lato}
        \usepackage{inconsolata}
        \setcounter{tocdepth}{2}
        \setcounter{secnumdepth}{2}
        % Reduce spacing
        \usepackage{titlesec}
        \titlespacing*{\section}{0pt}{10pt plus 2pt minus 2pt}{5pt plus 2pt minus 2pt}
        \titlespacing*{\subsection}{0pt}{8pt plus 2pt minus 2pt}{4pt plus 2pt minus 2pt}
        \titlespacing*{\subsubsection}{0pt}{6pt plus 2pt minus 2pt}{3pt plus 2pt minus 2pt}
        % Reduce paragraph spacing
        \setlength{\parskip}{3pt}
        \setlength{\parsep}{0pt}
        \setlength{\headsep}{10pt}
        \setlength{\topskip}{0pt}
        % Prevent blank pages - these are the key commands
        \raggedbottom
        \let\cleardoublepage\clearpage
    ''',
    'maketitle': r'''
        \begin{titlepage}
        \centering
        {\Large\bfseries Sphinx Extension - Filter Tabs Documentation\par}
        \vspace{0.5cm}
        {\large Aputsiak Niels Janussen\par}
        \vspace{0.5cm}
        {\normalsize Version 0.9.0\par}
        \vspace{0.5cm}
        {\small\today\par}
        \end{titlepage}
    ''',
}

# -- Options for filter-tabs extension ---------------------------------------
filter_tabs_tab_highlight_color = "#d45234"
filter_tabs_border_radius = "4px"
filter_tabs_debug_mode = True
filter_tabs_keyboard_navigation = True
filter_tabs_announce_changes = True
