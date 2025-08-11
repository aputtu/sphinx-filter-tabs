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

    .. tab:: Go

        This is Go content.
"""

@pytest.mark.sphinx('html')
def test_html_structure_and_styles(app: SphinxTestApp, test_rst_content):
    """Checks the generated HTML structure and inline CSS variables."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()

    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert container, "Main container .sft-container not found"

    # 1. Test for correct inline style attribute
    style = container['style']
    assert "--sft-border-radius: 8px" in style
    assert "--sft-tab-highlight-color: #007bff" in style

    # 2. Test for correct structure (fieldset, legend, inputs, etc.)
    fieldset = container.select_one('.sft-fieldset')
    assert fieldset
    assert "Filter by: Python, Rust, Go" in fieldset.select_one('legend').text

    inputs = fieldset.select('input[type="radio"]')
    assert len(inputs) == 3

    # 3. Test that the default tab is correctly checked
    checked_input = fieldset.select_one('input[checked]')
    assert checked_input and checked_input['id'].endswith(str(checked_input.find_next_sibling('div').select_one('label[for*="-rust"]')['for']))

    # 4. Test for correct tab and panel roles for accessibility
    assert fieldset.select_one('[role="tablist"]')
    labels = fieldset.select('[role="tab"]')
    assert len(labels) == 3 and [t.text for t in labels] == ["Python", "Rust", "Go"]
    panels = fieldset.select('[role="tabpanel"]')
    assert len(panels) == 4 # (Python, Rust, Go + General)

@pytest.mark.sphinx('html', confoverrides={'filter_tabs_border_radius': '20px'})
def test_config_overrides_work(app: SphinxTestApp, test_rst_content):
    """Ensures that conf.py overrides are reflected in the style attribute."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert "--sft-border-radius: 20px" in container['style']

@pytest.mark.sphinx('latex')
def test_latex_fallback_renders_admonitions(app: SphinxTestApp, test_rst_content):
    """Checks that the LaTeX builder creates simple admonitions as a fallback."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    result = (app.outdir / 'project.tex').read_text()

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
    """Tests that a `tab` directive outside `filter-tabs` raises an error."""
    app.srcdir.joinpath('index.rst').write_text(".. tab:: Orphan")
    with pytest.raises(Exception):
        app.build()
    assert "`tab` can only be used inside a `filter-tabs` directive" in warning.getvalue()
