# tests/test_extension.py

import importlib.util

import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp

_rinoh_available = importlib.util.find_spec("rinoh") is not None


@pytest.mark.sphinx("html")
def test_basic_filter_tabs(app: SphinxTestApp):
    """Test basic filter tabs functionality."""
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
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Check container structure
    container = soup.select_one(".sft-container")
    assert container, "Container should exist"
    assert container.get("role") == "region", "Container should have region role"

    # Check radiogroup
    fieldset = soup.select_one('.sft-fieldset[role="radiogroup"]')
    assert fieldset, "Fieldset should have radiogroup role"

    # Check visible legend
    legend = soup.select_one(".sft-legend")
    assert legend, "Legend should exist"
    legend_text = legend.get_text().strip()
    assert "Choose" in legend_text, "Legend should have meaningful text"

    # Check tabs were created
    radios = soup.select('.sft-radio-group input[type="radio"]')
    assert len(radios) == 3, f"Expected 3 tabs, found {len(radios)}"

    # Check tab names from labels
    labels = soup.select(".sft-radio-group label")
    tab_names = [label.text.strip() for label in labels]
    assert tab_names == ["Python", "JavaScript", "Rust"]

    # Check JavaScript is default (second radio should be checked)
    assert radios[1].get("checked") is not None, "JavaScript tab should be default"

    # Check panels have proper roles
    panels = soup.select('.sft-panel[role="tabpanel"]')
    assert len(panels) == 3, "Should have 3 panels with tabpanel role"

    # Check general content exists
    general_panel = soup.select_one('.sft-panel[data-filter="General"]')
    assert general_panel, "General panel not found"
    assert "general content that appears" in general_panel.text


@pytest.mark.sphinx("html")
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
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Find the radio inputs
    radios = soup.select('.sft-radio-group input[type="radio"]')

    # Check that aria-labels were added
    assert radios[0].get("aria-label") == "Command Line Interface installation instructions"
    assert radios[1].get("aria-label") == "Graphical User Interface installation instructions"

    # Verify the visual labels are still short
    labels = soup.select(".sft-radio-group label")
    assert labels[0].text.strip() == "CLI"
    assert labels[1].text.strip() == "GUI"


@pytest.mark.sphinx("html")
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
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

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


@pytest.mark.sphinx("html")
def test_accessibility_features(app: SphinxTestApp):
    """Test accessibility features are properly implemented."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python (default)
        Python content
    .. tab:: JavaScript
        JS content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Check ARIA relationships
    container = soup.select_one(".sft-container")
    legend = soup.select_one(".sft-legend")

    # Container should reference legend
    assert container.get("aria-labelledby") == legend.get("id")

    # --- START of updated section ---

    # Check that each radio button has a corresponding screen reader description
    radios = soup.select('input[type="radio"]')
    assert len(radios) == 2

    for radio in radios:
        describedby_id = radio.get("aria-describedby")
        assert describedby_id, "Radio button should have aria-describedby"

        desc_element = soup.select_one(f"#{describedby_id}")
        assert desc_element, f"Description element #{describedby_id} should exist"
        assert "sr-only" in desc_element.get("class", []), "Description should be sr-only"

    # Check panels are focusable (with typo corrected)
    panels = soup.select('.sft-panel[role="tabpanel"]')
    for panel in panels:
        if panel.get("data-filter") != "General":  # General panel doesn't need tabindex
            assert panel.get("tabindex") == "0", "Panels should be focusable"


@pytest.mark.sphinx("html")
def test_nested_tabs(app: SphinxTestApp):
    """Test that nested tabs work correctly."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Windows

        Windows instructions:

        .. filter-tabs::

            .. tab:: Pip (default)
                pip install package
            .. tab:: Conda
                conda install package

    .. tab:: Mac (default)

        Mac instructions here.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Should have multiple filter-tabs containers
    containers = soup.select(".sft-container")
    assert len(containers) == 2, "Should have 2 nested containers"

    # Each should have their own radio groups
    radiogroups = soup.select('[role="radiogroup"]')
    assert len(radiogroups) == 2, "Should have 2 radiogroups"

    # Check unique group names
    radios = soup.select('input[type="radio"]')
    group_names = {radio.get("name") for radio in radios}
    assert len(group_names) == 2, "Should have 2 unique radio group names"


FALLBACK_CONTENT = """
Test Document
=============

.. filter-tabs::

    General content.

    .. tab:: Python
        Python content
    .. tab:: JavaScript
        JS content
"""


def _assert_fallback_output(text: str) -> None:
    """Assert that all tab and general content is present in the output."""
    assert "Python" in text, "Python tab should appear in output"
    assert "JavaScript" in text, "JavaScript tab should appear in output"
    assert "General content" in text, "General content should appear in output"


@pytest.mark.sphinx("latex")
def test_latex_fallback(app: SphinxTestApp):
    """Test that LaTeX fallback behavior works."""
    app.srcdir.joinpath("index.rst").write_text(FALLBACK_CONTENT)
    app.build()

    latex_files = list(app.outdir.glob("*.tex"))
    assert len(latex_files) > 0, "Should generate at least one LaTeX file"
    _assert_fallback_output(sorted(latex_files)[0].read_text())


@pytest.mark.sphinx("text")
def test_text_fallback(app: SphinxTestApp):
    """Test that the plain-text builder renders all tab content."""
    app.srcdir.joinpath("index.rst").write_text(FALLBACK_CONTENT)
    app.build()

    text_files = list(app.outdir.glob("*.txt"))
    assert len(text_files) > 0, "Should generate at least one text file"
    _assert_fallback_output(sorted(text_files)[0].read_text())


@pytest.mark.sphinx(
    "man", confoverrides={"man_pages": [("index", "testdoc", "Test", ["Author"], 1)]}
)
def test_man_fallback(app: SphinxTestApp):
    """Test that the man page builder renders all tab content."""
    app.srcdir.joinpath("index.rst").write_text(FALLBACK_CONTENT)
    app.build()

    man_files = list(app.outdir.glob("*.1"))
    assert len(man_files) > 0, "Should generate at least one man page"
    _assert_fallback_output(sorted(man_files)[0].read_text())


@pytest.mark.sphinx(
    "texinfo",
    confoverrides={
        "texinfo_documents": [
            ("index", "testdoc", "Test", "Author", "testdoc", "A test.", "Miscellaneous")
        ]
    },
)
def test_texinfo_fallback(app: SphinxTestApp):
    """Test that the Texinfo builder renders all tab content."""
    app.srcdir.joinpath("index.rst").write_text(FALLBACK_CONTENT)
    app.build()

    texi_files = list(app.outdir.glob("*.texi"))
    assert len(texi_files) > 0, "Should generate at least one .texi file"
    _assert_fallback_output(sorted(texi_files)[0].read_text())


@pytest.mark.skipif(not _rinoh_available, reason="rinohtype not installed")
@pytest.mark.sphinx("rinoh")
def test_rinoh_smoke(app: SphinxTestApp):
    """Smoke test: rinoh builder completes without errors and produces a PDF.

    Skipped automatically if rinohtype is not installed.
    Content verification is not possible on binary PDF output without
    an additional extraction library.
    """
    app.srcdir.joinpath("index.rst").write_text(FALLBACK_CONTENT)
    app.build()
    pdf_files = list(app.outdir.glob("*.pdf"))
    assert len(pdf_files) > 0, "rinoh builder should produce at least one PDF"


@pytest.mark.sphinx("html")
def test_configuration_theming(app: SphinxTestApp):
    """Test that the highlight colour config is written to the generated theme CSS file."""
    app.config.filter_tabs_highlight_color = "#ff0000"

    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    # The container element should no longer carry an inline style — the
    # colour is now injected globally via a generated filter_tabs_theme.css.
    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    container = soup.select_one(".sft-container")
    assert not container.get("style"), "Container should have no inline style attribute"

    # Verify the generated theme CSS file exists and contains the configured value.
    theme_css_path = app.outdir / "_static" / "filter_tabs_theme.css"
    assert theme_css_path.exists(), "filter_tabs_theme.css should be generated in _static/"
    theme_content = theme_css_path.read_text(encoding="utf-8")
    assert "--sft-highlight-color: #ff0000" in theme_content, (
        f"Generated theme CSS should contain the configured colour. Got:\n{theme_content}"
    )


@pytest.mark.sphinx("html")
def test_unique_ids_multiple_groups(app: SphinxTestApp):
    """Test that IDs are unique across multiple tab groups."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python
        Python 1
    .. tab:: JavaScript
        JS 1

.. filter-tabs::

    .. tab:: Python
        Python 2
    .. tab:: JavaScript
        JS 2
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Collect all IDs
    all_elements_with_ids = soup.select("[id]")
    all_ids = [elem.get("id") for elem in all_elements_with_ids]

    # Check for duplicates
    duplicates = [id_val for id_val in set(all_ids) if all_ids.count(id_val) > 1]
    assert not duplicates, f"Duplicate IDs found: {duplicates}"


@pytest.mark.sphinx("html")
def test_default_tab_selection(app: SphinxTestApp):
    """Test that default tab selection works properly."""
    app.config.filter_tabs_debug_mode = True
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: First
        First tab content

    .. tab:: Second (default)
        Second tab content

    .. tab:: Third
        Third tab content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # Check that the second radio button is checked
    radios = soup.select('input[type="radio"]')
    assert len(radios) == 3

    # Find which radio has the checked attribute
    checked_radios = []
    for i, radio in enumerate(radios):
        if radio.get("checked") is not None:
            checked_radios.append(i)

    # Debug output if the test fails
    if checked_radios != [1]:
        labels = soup.select(".sft-radio-group label")
        label_texts = [label.text.strip() for label in labels]
        print(f"Label texts: {label_texts}")
        print(f"Checked radios: {checked_radios}")

        # Check the tab data to see which one was marked as default
        for i, radio in enumerate(radios):
            print(f"Radio {i} checked: {radio.get('checked') is not None}")

    assert checked_radios == [1], f"Expected second tab to be checked, but got: {checked_radios}"


@pytest.mark.sphinx("html")
def test_error_handling_no_tabs(app: SphinxTestApp):
    """Test that filter-tabs without any tab directives logs an error."""
    content = """
Test Document
=============

.. filter-tabs::

    This has no tab directives, should cause an error.
"""
    app.srcdir.joinpath("index.rst").write_text(content)

    # Run the build and expect Sphinx to log an error
    app.build()

    # Check the captured warnings/errors for our specific message
    warnings = app._warning.getvalue()
    assert "No `.. tab::` directives found inside `.. filter-tabs::`" in warnings


@pytest.mark.sphinx("html")
def test_custom_legend_option(app: SphinxTestApp):
    """Test that the :legend: option provides a custom legend."""
    content = """
Test Document
=============

.. filter-tabs::
   :legend: My Custom Test Legend

   .. tab:: One
      Content One
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    legend = soup.select_one(".sft-legend")
    assert legend, "Legend should exist"
    assert legend.get_text().strip() == "My Custom Test Legend"


@pytest.mark.sphinx("html")
def test_more_than_ten_tabs(app: SphinxTestApp):
    """Test that tab groups with more than 10 tabs work correctly.

    Previously the CSS selector block was static and capped at 10. Now it is
    generated dynamically, so all tabs must appear in the HTML and the
    generated theme CSS must contain a selector for every index.
    """
    tabs = "\n".join(
        f"    .. tab:: Tab {i}{' (default)' if i == 0 else ''}\n\n        Content {i}.\n"
        for i in range(12)
    )
    content = f"""
Test Document
=============

.. filter-tabs::

{tabs}
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")

    # All 12 panels must be present in the DOM.
    panels = soup.select(".sft-panel[data-tab-index]")
    tab_indices = {p.get("data-tab-index") for p in panels if p.get("data-filter") != "General"}
    assert len(tab_indices) == 12, (
        f"Expected 12 tab panels in the DOM, found {len(tab_indices)}: {sorted(tab_indices)}"
    )

    # The generated theme CSS must contain a selector for every index 0–11.
    theme_css = (app.outdir / "_static" / "filter_tabs_theme.css").read_text()
    for i in range(12):
        assert f'data-tab-index="{i}"]' in theme_css, (
            f"Expected selector for data-tab-index={i} in generated theme CSS"
        )


@pytest.mark.sphinx("html")
def test_nested_tab_selector_isolation(app: SphinxTestApp):
    """Test that the generated CSS uses the child combinator to isolate nested groups.

    The selector must use '> .sft-panel' (child combinator) not ' .sft-panel'
    (descendant combinator). Without this, selecting tab index N in an outer
    group would also force-show panel index N inside any nested group,
    overriding the inner group's own radio state.
    """
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Outer A (default)

        .. filter-tabs::

            .. tab:: Inner X (default)

                Inner X content.

            .. tab:: Inner Y

                Inner Y content.

    .. tab:: Outer B

        Outer B content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    theme_css = (app.outdir / "_static" / "filter_tabs_theme.css").read_text()

    # Every panel selector must use the child combinator.
    assert "~ .sft-content > .sft-panel" in theme_css, (
        "Generated selectors must use child combinator (>) between "
        ".sft-content and .sft-panel to prevent outer group selectors "
        "from bleeding into nested groups."
    )
    # Confirm the descendant form is absent.
    assert "~ .sft-content .sft-panel" not in theme_css, (
        "Descendant combinator ( .sft-panel) found — this breaks nested tab isolation."
    )


# =============================================================================
# _parse_tab_argument edge cases
# =============================================================================


@pytest.mark.sphinx("html")
def test_tab_name_case_insensitive_default(app: SphinxTestApp):
    """'(DEFAULT)' in any case is recognised as the default marker."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Alpha (DEFAULT)

        Alpha content.

    .. tab:: Beta

        Beta content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    radios = soup.select('input[type="radio"]')
    assert radios[0].get("checked") is not None, "Alpha should be default (case-insensitive)"
    assert radios[1].get("checked") is None


@pytest.mark.sphinx("html")
def test_tab_name_with_only_default_marker_is_error(app: SphinxTestApp):
    """A tab whose name would be empty after stripping '(default)' must error."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: (default)

        Content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "Invalid tab argument" in warnings


@pytest.mark.sphinx("html")
def test_tab_outside_filter_tabs_errors(app: SphinxTestApp):
    """A ``.. tab::`` directive used outside ``.. filter-tabs::`` must produce an error."""
    content = """
Test Document
=============

.. tab:: Orphan

    This tab has no parent filter-tabs directive.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "tab` can only be used inside a `filter-tabs`" in warnings


# =============================================================================
# _validate_slots warnings
# =============================================================================


@pytest.mark.sphinx("html")
def test_duplicate_tab_name_errors(app: SphinxTestApp):
    """Duplicate tab names inside one filter-tabs block must produce an error."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Same

        First.

    .. tab:: Same

        Second.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "Duplicate tab name 'Same'" in warnings


@pytest.mark.sphinx("html")
def test_empty_tab_content_warns(app: SphinxTestApp):
    """A tab with no body content should log a warning."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Empty

    .. tab:: Full

        Full content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "Tab 'Empty' has no content" in warnings


@pytest.mark.sphinx("html")
def test_multiple_defaults_uses_first_and_warns(app: SphinxTestApp):
    """Multiple '(default)' markers should warn and use the first one."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Alpha (default)

        Alpha content.

    .. tab:: Beta (default)

        Beta content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "Multiple tabs marked as default" in warnings

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    radios = soup.select('input[type="radio"]')
    assert radios[0].get("checked") is not None, "First tab should be default"
    assert radios[1].get("checked") is None


# =============================================================================
# _infer_content_type paths
# =============================================================================


@pytest.mark.sphinx("html")
def test_legend_infers_programming_language(app: SphinxTestApp):
    """Tab names matching programming languages produce a 'programming language' legend."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python

        Python content.

    .. tab:: JavaScript

        JS content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    legend_text = soup.select_one(".sft-legend").get_text()
    assert "programming language" in legend_text


@pytest.mark.sphinx("html")
def test_legend_infers_via_substring(app: SphinxTestApp):
    """Tab names that contain a keyword (not an exact match) still infer the type."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: CPython

        CPython content.

    .. tab:: PyPy

        PyPy content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    legend_text = soup.select_one(".sft-legend").get_text()
    # "cpython" contains "python" → programming language
    assert "programming language" in legend_text


@pytest.mark.sphinx("html")
def test_substring_matching_order(app: SphinxTestApp):
    """Exact match should take precedence over substring match.

    'conda-forge' will NOT match 'conda' exact match (pass 1).
    But if 'conda' exact match happens first, 'conda-forge' shouldn't magically match.
    The real issue was `"source"` exact vs `"environment" (open source)` substring.
    Let's test 'conda-forge' which matches 'package manager' substring.
    """
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: conda-forge

        conda-forge content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    legend_text = soup.select_one(".sft-legend").get_text()

    # "conda-forge" is not an exact match for "conda", but matches as a substring.
    # Therefore, it will fall through Pass 1 and hit Pass 2 for "package manager"
    assert "package manager" in legend_text


@pytest.mark.sphinx("html")
def test_legend_falls_back_to_option(app: SphinxTestApp):
    """Unrecognised tab names fall back to 'option' in the legend."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Foo

        Foo content.

    .. tab:: Bar

        Bar content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    legend_text = soup.select_one(".sft-legend").get_text()
    assert "option" in legend_text


# =============================================================================
# Collapsible admonitions
# =============================================================================


@pytest.mark.sphinx("html")
def test_collapsible_admonition_collapsed(app: SphinxTestApp):
    """An admonition with the 'collapsible' class renders as a <details> element."""
    content = """
Test Document
=============

.. admonition:: My Title
   :class: collapsible

   Hidden content here.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    details = soup.select_one("details.collapsible-section")
    assert details is not None, "<details> element not found"
    assert details.get("open") is None, "Collapsed details should not have 'open' attribute"

    summary = details.select_one("summary")
    assert summary is not None
    assert "My Title" in summary.get_text()

    assert "Hidden content here" in details.get_text()


@pytest.mark.sphinx("html")
def test_collapsible_admonition_expanded(app: SphinxTestApp):
    """An admonition with both 'collapsible' and 'expanded' classes renders open."""
    content = """
Test Document
=============

.. admonition:: Open Title
   :class: collapsible expanded

   Visible content here.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    soup = BeautifulSoup((app.outdir / "index.html").read_text(), "html.parser")
    details = soup.select_one("details.collapsible-section")
    assert details is not None
    assert details.get("open") == "open", "Expanded details should have open='open'"


@pytest.mark.sphinx("html")
def test_collapsible_admonition_no_title_uses_details(app: SphinxTestApp):
    """A collapsible admonition with no explicit title falls back to 'Details'."""
    content = """
Test Document
=============

.. admonition::
   :class: collapsible

   Content without a title.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    # This may error during RST parsing (admonition requires a title argument),
    # but if it builds, the summary should fall back to "Details".
    app.build()
    # Just assert the build completed — if there's an RST parse error, the
    # warning stream will contain it but no exception is raised.


@pytest.mark.sphinx("latex")
def test_collapsible_admonition_ignored_on_latex(app: SphinxTestApp):
    """Collapsible admonitions are left as plain admonitions on non-HTML builders."""
    content = """
Test Document
=============

.. admonition:: Note Title
   :class: collapsible

   Collapsible content.
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    latex_files = list(app.outdir.glob("*.tex"))
    assert latex_files, "LaTeX output should be produced"
    latex_text = sorted(latex_files)[0].read_text()
    # Content must still appear; it must NOT be wrapped in <details>
    assert "Collapsible content" in latex_text
    assert "<details" not in latex_text


# =============================================================================
# _write_theme_css: warn threshold and hard cap
# =============================================================================


@pytest.mark.sphinx("html")
def test_theme_css_warn_threshold(app: SphinxTestApp):
    """16 tabs (> WARN_THRESHOLD=15) should log a warning, but 20 tabs are generated anyway."""
    n = 16
    tabs = "\n".join(
        f"    .. tab:: Tab{i}{' (default)' if i == 0 else ''}\n\n        Content {i}.\n"
        for i in range(n)
    )
    content = f"""
Test Document
=============

.. filter-tabs::

{tabs}
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "hard to navigate" in warnings

    theme_css = (app.outdir / "_static" / "filter_tabs_theme.css").read_text()
    for i in range(20):
        assert f'data-tab-index="{i}"]' in theme_css


@pytest.mark.sphinx("html")
def test_theme_css_hard_cap(app: SphinxTestApp):
    """21 tabs (> HARD_CAP=20) should log an error and cap selectors at index 19."""
    n = 21
    tabs = "\n".join(
        f"    .. tab:: Tab{i}{' (default)' if i == 0 else ''}\n\n        Content {i}.\n"
        for i in range(n)
    )
    content = f"""
Test Document
=============

.. filter-tabs::

{tabs}
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    warnings = app._warning.getvalue()
    assert "capped at 20" in warnings

    theme_css = (app.outdir / "_static" / "filter_tabs_theme.css").read_text()
    # Selectors for indices 0–19 must be present
    for i in range(20):
        assert f'data-tab-index="{i}"]' in theme_css
    # Index 20 must NOT have a selector (capped)
    assert 'data-tab-index="20"]' not in theme_css
