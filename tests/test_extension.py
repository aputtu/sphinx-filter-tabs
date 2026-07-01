import importlib.util
import re
import subprocess
import sys
import textwrap
import zlib

import pytest
from sphinx.testing.util import SphinxTestApp

from tests.helpers import build_index, html_soup, read_theme_css, tab_group_rst, warning_text

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
    build_index(app, content)

    soup = html_soup(app)

    # Check container structure
    container = soup.select_one(".sft-container")
    assert container, "Container should exist"
    assert container.get("role") is None, "Container should remain a structural wrapper"
    assert container.get("aria-labelledby") is None

    # Check native grouping
    fieldset = soup.select_one(".sft-fieldset")
    assert fieldset, "Fieldset should exist"
    assert fieldset.get("role") is None, "Fieldset should use native grouping semantics"

    # Check visible legend
    legend = soup.select_one(".sft-legend")
    assert legend, "Legend should exist"
    legend_text = legend.get_text().strip()
    assert "Choose" in legend_text, "Legend should have meaningful text"

    # Check tabs were created
    radios = soup.select('.sft-interactive input[type="radio"]')
    assert len(radios) == 3, f"Expected 3 tabs, found {len(radios)}"

    # Check tab names from labels
    labels = soup.select(".sft-interactive label")
    tab_names = [label.text.strip() for label in labels]
    assert tab_names == ["Python", "JavaScript", "Rust"]

    # Check JavaScript is default (second radio should be checked)
    assert radios[1].get("checked") is not None, "JavaScript tab should be default"

    # Check tab-specific panels are plain content containers.
    panels = soup.select(".sft-panel[data-tab-index]")
    assert len(panels) == 3, "Should have 3 tab-specific panels"
    assert not soup.select('.sft-panel[role="tabpanel"]')

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
    build_index(app, content)

    soup = html_soup(app)

    # Find the radio inputs
    radios = soup.select('.sft-interactive input[type="radio"]')

    # Check that aria-labels were added
    assert radios[0].get("aria-label") == "Command Line Interface installation instructions"
    assert radios[1].get("aria-label") == "Graphical User Interface installation instructions"

    # Verify the visual labels are still short
    labels = soup.select(".sft-interactive label")
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
    build_index(app, content)

    soup = html_soup(app)

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
    build_index(app, content)

    soup = html_soup(app)

    # Check native group semantics and ARIA relationships
    container = soup.select_one(".sft-container")
    legend = soup.select_one(".sft-legend")
    fieldset = soup.select_one(".sft-fieldset")
    assert container.get("role") is None
    assert fieldset is not None
    assert legend is not None

    # Check that each radio button has a corresponding screen reader description
    radios = soup.select('input[type="radio"]')
    assert len(radios) == 2

    for radio in radios:
        describedby_id = radio.get("aria-describedby")
        assert describedby_id, "Radio button should have aria-describedby"

        desc_element = soup.select_one(f"#{describedby_id}")
        assert desc_element, f"Description element #{describedby_id} should exist"
        assert "sft-sr-only" in desc_element.get("class", []), (
            "Description should use namespaced screen-reader-only class"
        )

    # Radios control plain panels; panels are not ARIA tabpanel widgets.
    panels = soup.select(".sft-panel[data-tab-index]")
    assert len(panels) == len(radios)
    for radio in radios:
        panel_id = radio.get("aria-controls")
        panel = soup.select_one(f"#{panel_id}")
        assert panel is not None, "Radio button should reference an existing panel"
        assert panel.get("role") is None, "Panels should not use tabpanel without tablist"
        assert panel.get("tabindex") is None, "Panels should keep native focus behavior"
        assert panel.get("aria-labelledby") is None


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
    build_index(app, content)

    soup = html_soup(app)

    # Should have multiple filter-tabs containers
    containers = soup.select(".sft-container")
    assert len(containers) == 2, "Should have 2 nested containers"

    # Each should have its own native fieldset group
    fieldsets = soup.select(".sft-fieldset")
    assert len(fieldsets) == 2, "Should have 2 fieldset groups"

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
    build_index(app, FALLBACK_CONTENT)

    latex_files = list(app.outdir.glob("*.tex"))
    assert len(latex_files) > 0, "Should generate at least one LaTeX file"
    _assert_fallback_output(sorted(latex_files)[0].read_text())


@pytest.mark.sphinx("text")
def test_text_fallback(app: SphinxTestApp):
    """Test that the plain-text builder renders all tab content."""
    build_index(app, FALLBACK_CONTENT)

    text_files = list(app.outdir.glob("*.txt"))
    assert len(text_files) > 0, "Should generate at least one text file"
    _assert_fallback_output(sorted(text_files)[0].read_text())


@pytest.mark.sphinx(
    "man", confoverrides={"man_pages": [("index", "testdoc", "Test", ["Author"], 1)]}
)
def test_man_fallback(app: SphinxTestApp):
    """Test that the man page builder renders all tab content."""
    build_index(app, FALLBACK_CONTENT)

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
    build_index(app, FALLBACK_CONTENT)

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
    build_index(app, FALLBACK_CONTENT)
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
    build_index(app, content)

    # The container element should no longer carry an inline style — the
    # colour is now injected globally via a generated filter_tabs_theme.css.
    soup = html_soup(app)
    container = soup.select_one(".sft-container")
    assert not container.get("style"), "Container should have no inline style attribute"

    # Verify the generated theme CSS file exists and contains the configured value.
    theme_content = read_theme_css(app)
    assert "--sft-highlight-color: #ff0000" in theme_content, (
        f"Generated theme CSS should contain the configured colour. Got:\n{theme_content}"
    )


@pytest.mark.sphinx("html")
def test_configuration_theming_accepts_modern_css_color(app: SphinxTestApp):
    """Modern CSS color syntax should be accepted when it is safe."""
    app.config.filter_tabs_highlight_color = "oklch(60% 0.12 240 / 85%)"

    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    build_index(app, content)

    theme_css = read_theme_css(app)
    assert "--sft-highlight-color: oklch(60% 0.12 240 / 85%)" in theme_css


def test_generated_theme_css_cache_buster_matches_written_file(tmp_path, rootdir):
    """The generated CSS must exist before Sphinx calculates static asset hashes."""
    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    srcdir.mkdir()
    srcdir.joinpath("index.rst").write_text(
        textwrap.dedent(
            """
            Test Document
            =============

            .. filter-tabs::

               .. tab:: CLI

                  CLI content.

               .. tab:: GUI

                  GUI content.
            """
        ),
        encoding="utf-8",
    )

    conf_template = textwrap.dedent(
        """
        import sys

        sys.path.insert(0, {rootdir!r})

        extensions = ["filter_tabs"]
        project = "Cache test"
        root_doc = "index"
        exclude_patterns = []
        html_static_path = []
        filter_tabs_highlight_color = "{color}"
        """
    )

    def build_with_color(color: str) -> tuple[str, str, str]:
        srcdir.joinpath("conf.py").write_text(
            conf_template.format(rootdir=str(rootdir), color=color),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx.cmd.build",
                "-q",
                "-b",
                "html",
                str(srcdir),
                str(outdir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        html = outdir.joinpath("index.html").read_text(encoding="utf-8")
        match = re.search(r"filter_tabs_theme\.css\?v=([0-9a-f]+)", html)
        assert match is not None, html

        theme_css = outdir.joinpath("_static", "filter_tabs_theme.css").read_bytes()
        actual_crc = f"{zlib.crc32(theme_css) & 0xFFFFFFFF:08x}"
        return match.group(1), actual_crc, theme_css.decode("utf-8")

    first_link_crc, first_actual_crc, first_css = build_with_color("#111111")
    assert first_link_crc == first_actual_crc
    assert "--sft-highlight-color: #111111" in first_css

    second_link_crc, second_actual_crc, second_css = build_with_color("#222222")
    assert second_link_crc == second_actual_crc
    assert "--sft-highlight-color: #222222" in second_css
    assert second_actual_crc != first_actual_crc


@pytest.mark.sphinx("html")
def test_native_theming_defaults_to_sphinx_theme_variables(app: SphinxTestApp):
    """Native mode should follow the active Sphinx theme unless explicitly configured."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    build_index(app, content)

    theme_css = read_theme_css(app)

    assert "--sft-highlight-color: var(--pst-color-primary" in theme_css
    assert "--sft-text: var(--pst-color-text-base" in theme_css
    assert "--sft-bg: transparent" in theme_css
    assert "--sft-tab-active-bg: transparent" in theme_css
    assert "#007bff" not in theme_css
    assert "#ffffff" not in theme_css


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
    build_index(app, content)

    soup = html_soup(app)

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
    build_index(app, content)

    soup = html_soup(app)

    radios = soup.select('input[type="radio"]')
    assert len(radios) == 3

    checked_radios = [i for i, radio in enumerate(radios) if radio.get("checked") is not None]
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
    build_index(app, content)

    # Check the captured warnings/errors for our specific message
    warnings = warning_text(app)
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
    build_index(app, content)

    soup = html_soup(app)

    legend = soup.select_one(".sft-legend")
    assert legend, "Legend should exist"
    assert legend.get_text().strip() == "My Custom Test Legend"


@pytest.mark.sphinx("html")
def test_hide_legend_option_keeps_accessible_legend(app: SphinxTestApp):
    """The :hide-legend: option hides the legend visually, but keeps it semantic."""
    content = """
Test Document
=============

.. filter-tabs::
   :hide-legend:

   .. tab:: Windows
      Windows content

   .. tab:: Linux
      Linux content
"""
    build_index(app, content)

    soup = html_soup(app)

    legend = soup.select_one(".sft-legend")

    assert legend, "Legend should still exist"
    assert "sft-sr-only" in legend.get("class", [])
    assert "operating system" in legend.get_text()


@pytest.mark.sphinx("html")
def test_hide_legend_option_with_custom_legend(app: SphinxTestApp):
    """A custom hidden legend should preserve the editor-provided accessible name."""
    content = """
Test Document
=============

.. filter-tabs::
   :legend: Choose where to deploy
   :hide-legend:

   .. tab:: Staging
      Staging content

   .. tab:: Production
      Production content
"""
    build_index(app, content)

    soup = html_soup(app)
    legend = soup.select_one(".sft-legend")

    assert legend.get_text().strip() == "Choose where to deploy"
    assert "sft-sr-only" in legend.get("class", [])


@pytest.mark.sphinx("html")
def test_directive_context_is_document_local(app: SphinxTestApp):
    """The parser-only tab context should not leave state on the build environment."""
    content = """
Test Document
=============

.. filter-tabs::

   .. tab:: Python
      Python content
"""
    build_index(app, content)

    assert not hasattr(app.env, "sft_context")


@pytest.mark.sphinx("html")
def test_more_than_ten_tabs(app: SphinxTestApp):
    """Test that tab groups with more than 10 tabs work correctly.

    Previously the CSS selector block was static and capped at 10. Now it is
    generated dynamically, so all tabs must appear in the HTML and the
    generated theme CSS must contain a selector for every index.
    """
    build_index(app, tab_group_rst(12))

    soup = html_soup(app)

    # All 12 panels must be present in the DOM.
    panels = soup.select(".sft-panel[data-tab-index]")
    tab_indices = {p.get("data-tab-index") for p in panels if p.get("data-filter") != "General"}
    assert len(tab_indices) == 12, (
        f"Expected 12 tab panels in the DOM, found {len(tab_indices)}: {sorted(tab_indices)}"
    )

    # The generated theme CSS must contain a selector for every index 0–11.
    theme_css = read_theme_css(app)
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
    build_index(app, content)

    theme_css = read_theme_css(app)

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
    build_index(app, content)

    soup = html_soup(app)
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
    build_index(app, content)

    warnings = warning_text(app)
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
    build_index(app, content)

    warnings = warning_text(app)
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
    build_index(app, content)

    warnings = warning_text(app)
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
    build_index(app, content)

    warnings = warning_text(app)
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
    build_index(app, content)

    warnings = warning_text(app)
    assert "Multiple tabs marked as default" in warnings

    soup = html_soup(app)
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
    build_index(app, content)

    soup = html_soup(app)
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
    build_index(app, content)

    soup = html_soup(app)
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
    build_index(app, content)

    soup = html_soup(app)
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
    build_index(app, content)

    soup = html_soup(app)
    legend_text = soup.select_one(".sft-legend").get_text()
    assert "option" in legend_text


# =============================================================================
# Collapsible admonitions
# =============================================================================


@pytest.mark.sphinx("html")
def test_collapsible_admonition_collapsed(app: SphinxTestApp):
    """An opted-in admonition renders as a <details> element."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test Document
=============

.. admonition:: My Title
   :class: sft-collapsible

   Hidden content here.
"""
    build_index(app, content)

    soup = html_soup(app)
    details = soup.select_one("details.sft-collapsible-section")
    assert details is not None, "<details> element not found"
    assert details.get("open") is None, "Collapsed details should not have 'open' attribute"

    summary = details.select_one("summary")
    assert summary is not None
    assert "My Title" in summary.get_text()

    assert "Hidden content here" in details.get_text()


@pytest.mark.sphinx("html")
def test_collapsible_admonition_expanded(app: SphinxTestApp):
    """An opted-in admonition with sft-expanded renders open."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test Document
=============

.. admonition:: Open Title
   :class: sft-collapsible sft-expanded

   Visible content here.
"""
    build_index(app, content)

    soup = html_soup(app)
    details = soup.select_one("details.sft-collapsible-section")
    assert details is not None
    assert details.get("open") == "open", "Expanded details should have open='open'"


@pytest.mark.sphinx("html")
def test_collapsible_admonition_preserves_title_markup(app: SphinxTestApp):
    """Inline markup in collapsible admonition titles should stay semantic."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test Document
=============

.. admonition:: **Bold** `Python <https://python.org>`_
   :class: sft-collapsible

   Hidden content here.
"""
    build_index(app, content)

    soup = html_soup(app)
    summary = soup.select_one("details.sft-collapsible-section summary")

    assert summary is not None
    assert summary.select_one("strong").get_text() == "Bold"
    link = summary.select_one('a[href="https://python.org"]')
    assert link is not None
    assert link.get_text() == "Python"


@pytest.mark.sphinx("latex")
def test_collapsible_admonition_ignored_on_latex(app: SphinxTestApp):
    """Collapsible admonitions are left as plain admonitions on non-HTML builders."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test Document
=============

.. admonition:: Note Title
   :class: sft-collapsible

   Collapsible content.
"""
    build_index(app, content)

    latex_files = list(app.outdir.glob("*.tex"))
    assert latex_files, "LaTeX output should be produced"
    latex_text = sorted(latex_files)[0].read_text()
    # Content must still appear; it must NOT be wrapped in <details>
    assert "Collapsible content" in latex_text
    assert "<details" not in latex_text


# =============================================================================
# _write_theme_css: warn threshold and dynamic selector count
# =============================================================================


@pytest.mark.sphinx("html")
def test_theme_css_warn_threshold(app: SphinxTestApp):
    """16 tabs should log a warning while selectors remain available."""
    build_index(app, tab_group_rst(16))

    warnings = warning_text(app)
    assert "hard to navigate" in warnings

    theme_css = read_theme_css(app)
    for i in range(20):
        assert f'data-tab-index="{i}"]' in theme_css


@pytest.mark.sphinx("html")
def test_theme_css_scales_beyond_default_selector_count(app: SphinxTestApp):
    """21 tabs should render all panels and selectors instead of being capped."""
    build_index(app, tab_group_rst(21))

    warnings = warning_text(app)
    assert "can be hard to navigate" in warnings
    assert "capped at 20" not in warnings

    soup = html_soup(app)
    panels = soup.select(".sft-panel[data-tab-index]")
    assert len(panels) == 21

    theme_css = read_theme_css(app)
    for i in range(21):
        assert f'data-tab-index="{i}"]' in theme_css


@pytest.mark.sphinx("html")
def test_configuration_theme_mode_and_flavor(app: SphinxTestApp):
    """Test that theme modes and flavors apply correctly."""
    app.config.filter_tabs_theme_mode = "opinionated"
    app.config.filter_tabs_flavor = "minimal"

    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    build_index(app, content)

    theme_content = read_theme_css(app)

    assert "--sft-bg: #ffffff" in theme_content
    assert "--sft-border: #e0e0e0" in theme_content
    assert "--sft-border-radius: 0" in theme_content
    assert "--sft-tab-font-size: 0.9em" in theme_content


@pytest.mark.sphinx("html")
def test_invalid_theme_mode_and_flavor_warn_and_fall_back(app: SphinxTestApp):
    """Invalid closed-set config values should warn instead of silently changing behavior."""
    app.config.filter_tabs_theme_mode = "natvie"
    app.config.filter_tabs_flavor = "compact"

    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    build_index(app, content)

    warnings = warning_text(app)
    assert "invalid filter_tabs_theme_mode value 'natvie'" in warnings
    assert "invalid filter_tabs_flavor value 'compact'" in warnings

    theme_content = read_theme_css(app)
    assert "--sft-text: var(--pst-color-text-base" in theme_content
    assert "--sft-border-radius: 0" not in theme_content
