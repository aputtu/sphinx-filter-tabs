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
def test_aria_attributes_present(app: SphinxTestApp, test_rst_content):
    """Verify ARIA attributes are correctly applied for accessibility compliance."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check tablist has correct role and attributes
    tablist = soup.select_one('[role="tablist"]')
    assert tablist, "Tablist role not found"
    assert tablist.get('aria-orientation') == 'horizontal', "Tablist missing aria-orientation"
    
    # Check tabs have correct ARIA attributes
    tabs = soup.select('[role="tab"]')
    assert len(tabs) == 3, f"Expected 3 tabs, found {len(tabs)}"  # Python, Rust, Go
    
    # Verify exactly one tab is marked as selected (the default)
    active_tabs = [t for t in tabs if t.get('aria-selected') == 'true']
    assert len(active_tabs) == 1, f"Should have exactly one active tab, found {len(active_tabs)}"
    
    # Verify the default tab (Rust) is the one selected
    default_tab = active_tabs[0]
    assert 'Rust' in default_tab.get_text(), "Default tab should be 'Rust'"
    
    # Check that non-active tabs are marked as not selected
    inactive_tabs = [t for t in tabs if t.get('aria-selected') == 'false']
    assert len(inactive_tabs) == 2, f"Should have 2 inactive tabs, found {len(inactive_tabs)}"
    
    # Check each tab has required attributes
    for tab in tabs:
        assert tab.get('aria-controls'), "Tab missing aria-controls attribute"
        assert tab.get('role') == 'tab', "Tab missing role=tab"
        assert tab.get('tabindex') is not None, "Tab missing tabindex attribute"
    
    # Check panels have correct ARIA attributes
    panels = soup.select('[role="tabpanel"]')
    assert len(panels) == 3, f"Expected 3 panels, found {len(panels)}"  # Python, Rust, Go panels
    
    # Check each panel has required attributes
    for panel in panels:
        assert panel.get('aria-labelledby'), "Panel missing aria-labelledby attribute"
        assert panel.get('role') == 'tabpanel', "Panel missing role=tabpanel"
        assert panel.get('tabindex') == '0', "Panel should have tabindex=0 for screen readers"
    
    # Verify tab-panel relationships (aria-controls matches panel IDs)
    for tab in tabs:
        panel_id = tab.get('aria-controls')
        matching_panel = soup.select_one(f'#{panel_id}')
        assert matching_panel, f"Tab aria-controls='{panel_id}' doesn't match any panel ID"
        assert matching_panel.get('aria-labelledby') == tab.get('id'), "Panel aria-labelledby doesn't match tab ID"

@pytest.mark.sphinx('html')
def test_keyboard_navigation_attributes(app: SphinxTestApp, test_rst_content):
    """Test that keyboard navigation attributes are properly set."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    tabs = soup.select('[role="tab"]')
    
    # Check that only one tab has tabindex="0" (the active one)
    focusable_tabs = [t for t in tabs if t.get('tabindex') == '0']
    assert len(focusable_tabs) == 1, "Only one tab should be focusable (tabindex=0)"
    
    # Check that other tabs have tabindex="-1"
    non_focusable_tabs = [t for t in tabs if t.get('tabindex') == '-1']
    assert len(non_focusable_tabs) == 2, "Non-active tabs should have tabindex=-1"
    
    # Verify the focusable tab is the one marked as selected
    focusable_tab = focusable_tabs[0]
    assert focusable_tab.get('aria-selected') == 'true', "Focusable tab should be the selected one"
