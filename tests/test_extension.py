import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp
from sphinx.errors import SphinxError

# A standard RST content fixture for tests
@pytest.fixture()
def test_rst_content():
    return """
A Test Document
===============

.. filter-tabs:: Python, Rust (default), Go

    .. tab:: General

        This is general content.

    .. tab:: Python

        This is Python content.

    .. tab:: Rust

        This is Rust content.
"""

@pytest.mark.sphinx('html')
def test_html_structure_and_styles(app: SphinxTestApp, test_rst_content):
    """Checks the generated HTML structure and inline CSS variables."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()

    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert container, "Main container .sft-container not found"

    # Test that the inline style attribute exists
    assert container.has_attr('style'), "Container is missing the style attribute"
    assert "--sft-border-radius: 8px" in container['style']

@pytest.mark.sphinx('html', confoverrides={'filter_tabs_border_radius': '20px'})
def test_config_overrides_work(app: SphinxTestApp, test_rst_content):
    """Ensures that conf.py overrides are reflected in the style attribute."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert container.has_attr('style'), "Container is missing the style attribute"
    assert "--sft-border-radius: 20px" in container['style']

@pytest.mark.sphinx('latex')
def test_latex_fallback_renders_admonitions(app: SphinxTestApp, test_rst_content):
    """Checks that the LaTeX builder creates simple admonitions as a fallback."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    # Look for the correct TeX filename based on the test project's name
    result = (app.outdir / 'sphinxtestproject.tex').read_text()

    # General content should appear directly
    assert 'This is general content.' in result
    assert r'\begin{sphinxadmonition}{note}{General}' not in result

    # Specific tabs should be titled admonitions
    assert r'\begin{sphinxadmonition}{note}{Python}' in result
    assert 'This is Python content.' in result
    assert r'\begin{sphinxadmonition}{note}{Rust}' in result
    assert 'This is Rust content.' in result

@pytest.mark.sphinx('html')
def test_error_on_orphan_tab(app: SphinxTestApp, status, warning):
    """Tests that a `tab` directive outside `filter-tabs` logs an error."""
    app.srcdir.joinpath('index.rst').write_text(".. tab:: Orphan")
    app.build()

    # Check for the error message in the warning stream instead of expecting a crash.
    warnings = warning.getvalue()
    assert "`tab` can only be used inside a `filter-tabs` directive" in warnings

@pytest.mark.sphinx('html')
def test_valid_html_structure(app: SphinxTestApp, test_rst_content):
    """Verify HTML structure is valid and doesn't have duplicate IDs."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check that we have radio buttons and labels
    tab_bar = soup.select_one('.sft-tab-bar')
    assert tab_bar, "Tab bar not found"
    
    radios = tab_bar.select('input[type="radio"]')
    labels = tab_bar.select('label')
    
    assert len(radios) == 3, f"Expected 3 radio buttons, found {len(radios)}"
    assert len(labels) == 3, f"Expected 3 labels, found {len(labels)}"
    
    # Check radio buttons have unique IDs
    radio_ids = [r.get('id') for r in radios if r.get('id')]
    assert len(radio_ids) == len(set(radio_ids)), "Radio buttons have duplicate IDs"
    
    # Check labels have proper 'for' attributes
    for label in labels:
        assert label.get('for'), "Label missing 'for' attribute"
        # Verify the 'for' points to an existing radio
        target_id = label.get('for')
        matching_radio = soup.select_one(f'#{target_id}')
        assert matching_radio, f"Label 'for' attribute points to non-existent ID: {target_id}"
    
    # Check panels exist and have unique IDs
    panels = soup.select('.sft-panel[role="tabpanel"]')
    assert len(panels) == 3, f"Expected 3 panels with role=tabpanel, found {len(panels)}"
    
    panel_ids = [p.get('id') for p in panels if p.get('id')]
    assert len(panel_ids) == len(set(panel_ids)), "Panels have duplicate IDs"
    
    # Verify all IDs in the document are unique
    all_elements_with_ids = soup.select('[id]')
    all_ids = [elem.get('id') for elem in all_elements_with_ids]
    assert len(all_ids) == len(set(all_ids)), f"Duplicate IDs found in HTML: {[id for id in all_ids if all_ids.count(id) > 1]}"

@pytest.mark.sphinx('html')
def test_no_aria_on_labels(app: SphinxTestApp, test_rst_content):
    """Verify labels don't have invalid ARIA attributes."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    labels = soup.select('.sft-tab-bar label')
    
    # Check that labels DON'T have ARIA role or aria-selected
    for label in labels:
        assert not label.get('role'), "Label should not have 'role' attribute"
        assert not label.get('aria-selected'), "Label should not have 'aria-selected' attribute"
        assert not label.get('aria-controls'), "Label should not have 'aria-controls' attribute"
        # Labels should only have 'for' attribute for accessibility
        assert label.get('for'), "Label should have 'for' attribute"

@pytest.mark.sphinx('html')
def test_panels_have_proper_aria(app: SphinxTestApp, test_rst_content):
    """Test that panels have proper ARIA attributes for screen readers."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check panels have correct ARIA attributes
    panels = soup.select('[role="tabpanel"]')
    assert len(panels) == 3, f"Expected 3 panels, found {len(panels)}"
    
    # Check each panel has required attributes
    for panel in panels:
        assert panel.get('aria-labelledby'), "Panel missing aria-labelledby attribute"
        assert panel.get('role') == 'tabpanel', "Panel missing role=tabpanel"
        assert panel.get('tabindex') == '0', "Panel should have tabindex=0 for screen readers"
        
        # Verify aria-labelledby points to an existing element
        labelledby_id = panel.get('aria-labelledby')
        matching_element = soup.select_one(f'#{labelledby_id}')
        assert matching_element, f"Panel aria-labelledby='{labelledby_id}' doesn't match any element ID"
