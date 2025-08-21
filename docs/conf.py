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
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# LaTeX settings with standard, widely available fonts
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    
    # Use a simple, standard chapter style
    'fncychap': r'\usepackage[Sonny]{fncychap}',
    
    # Fix hyperref issues
    'passoptionstopackages': r'\PassOptionsToPackage{hypertexnames=false}{hyperref}',
    
    # Single-sided document
    'classoptions': ',oneside',
    
    # Minimal, robust preamble using only standard LaTeX fonts
    'preamble': r'''
        % Use standard Computer Modern fonts (always available)
        % No custom font packages to avoid compatibility issues
        
        % Clean section formatting
        \usepackage{titlesec}
        \titleformat{\chapter}[display]
            {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}
        \titleformat{\section}
            {\normalfont\Large\bfseries}{\thesection}{1em}{}
        \titleformat{\subsection}
            {\normalfont\large\bfseries}{\thesubsection}{1em}{}
        \titleformat{\subsubsection}
            {\normalfont\normalsize\bfseries}{\thesubsubsection}{1em}{}
        
        % Remove forced page breaks
        \let\cleardoublepage\clearpage
        
        % Better spacing
        \usepackage{setspace}
        \onehalfspacing
    ''',
    
    # Simple, clean title page
    'maketitle': f'''
        \\begin{{titlepage}}
        \\centering
        \\vspace*{{2cm}}
        {{ \\huge\\bfseries Sphinx Extension - Filter Tabs Documentation\\par}}
  
       \\vspace{{1cm}}
        {{ \\Large Aputsiak Niels Janussen\\par}}
        \\vspace{{0.5cm}}
        {{\\large Version {release}\\par}}
        \\vspace{{0.5cm}}
        {{\\normalsize\\today\\par}}
        \\vfill
        \\end{{titlepage}}
        \\cleardoublepage
    ''',
}

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
