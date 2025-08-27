import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp
from sphinx.errors import SphinxError

@pytest.mark.sphinx('html')
def test_simplified_syntax_no_arguments(app: SphinxTestApp):
    """Test the new simplified syntax where filter-tabs has no arguments."""
    content = """
Test Document
=============

.. filter-tabs::

    This is general content that appears regardless of selection.
    
    .. tab:: Python
    
        Python specific content.
        
    .. tab:: JavaScript (default)
    
        JavaScript specific content.
        
    .. tab:: Rust
    
        Rust specific content.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check that tabs were created
    radios = soup.select('.sft-tab-bar input[type="radio"]')
    assert len(radios) == 3, f"Expected 3 tabs, found {len(radios)}"
    
    # Check tab names from labels
    labels = soup.select('.sft-tab-bar label')
    tab_names = [label.text.strip() for label in labels]
    assert tab_names == ['Python', 'JavaScript', 'Rust']
    
    # Check JavaScript is default (second radio should be checked)
    assert radios[1].get('checked') is not None, "JavaScript tab should be default"
    
    # Check general content exists
    general_panel = soup.select_one('.sft-panel[data-filter="General"]')
    assert general_panel, "General panel not found"
    assert "general content that appears" in general_panel.text


@pytest.mark.sphinx('html')
def test_aria_label_option(app: SphinxTestApp):
    """Test that the :aria-label: option adds proper ARIA attributes."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: CLI
       :aria-label: Command Line Interface installation instructions
       
        Install via command line.
        
    .. tab:: GUI (default)
       :aria-label: Graphical User Interface installation instructions
       
        Install via graphical interface.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Find the radio inputs
    radios = soup.select('.sft-tab-bar input[type="radio"]')
    
    # Check that aria-labels were added
    assert radios[0].get('aria-label') == "Command Line Interface installation instructions"
    assert radios[1].get('aria-label') == "Graphical User Interface installation instructions"
    
    # Verify the visual labels are still short
    labels = soup.select('.sft-tab-bar label')
    assert labels[0].text.strip() == 'CLI'
    assert labels[1].text.strip() == 'GUI'


@pytest.mark.sphinx('html')
def test_mixed_general_and_tab_content(app: SphinxTestApp):
    """Test that content outside tab directives becomes general content."""
    content = """
Test Document
=============

.. filter-tabs::

    This paragraph is general content.
    
    It can span multiple paragraphs.
    
    .. note::
    
        Even admonitions outside tabs are general.
    
    .. tab:: Option A
    
        Content for option A.
        
    Some more general content between tabs.
    
    .. tab:: Option B (default)
    
        Content for option B.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    general_panel = soup.select_one('.sft-panel[data-filter="General"]')
    assert general_panel, "General panel not found"
    
    general_text = general_panel.text
    assert "This paragraph is general content" in general_text
    assert "It can span multiple paragraphs" in general_text
    assert "Even admonitions outside tabs are general" in general_text
    assert "Some more general content between tabs" in general_text
    
    # Ensure tab content is NOT in general panel
    assert "Content for option A" not in general_text
    assert "Content for option B" not in general_text
