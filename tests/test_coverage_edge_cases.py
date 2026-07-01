from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from docutils import nodes
from docutils.statemachine import StringList
from docutils.utils import Reporter
from sphinx.testing.util import SphinxTestApp

from filter_tabs import _depart_noop, _visit_skip_node
from filter_tabs.admonitions import setup_collapsible_admonitions
from filter_tabs.assets import (
    _configured_highlight_color,
    _selector_count_for_build,
    register_static_assets,
    write_theme_css,
)
from filter_tabs.constants import SFT_DEFAULT_SELECTOR_COUNT
from filter_tabs.directives import TabDirective
from filter_tabs.nodes import FilterTabSlotNode, FilterTabsNode, SummaryNode
from filter_tabs.transforms import process_filter_tabs_nodes, validate_tabs_structure
from filter_tabs.utils import IDGenerator
from tests.helpers import build_index, html_soup


def test_validate_tabs_structure_no_slots():
    """Test validate_tabs_structure with no slots."""
    ft_node = FilterTabsNode()
    assert validate_tabs_structure(ft_node) is False


def test_validate_tabs_structure_missing_tab_name():
    """Test validate_tabs_structure with a slot missing tab_name."""
    ft_node = FilterTabsNode()
    slot = FilterTabSlotNode()
    # slot["tab_name"] is missing
    ft_node += slot
    assert validate_tabs_structure(ft_node) is False


def test_id_generator_boundary():
    """Test IDGenerator beyond reasonable index (if it were ever called)."""
    id_gen = IDGenerator("test-group")
    # Just to exercise the code for very large generated tab sets.
    assert id_gen.radio_id(999) == "test-group-radio-999"
    assert id_gen.label_id(999) == "test-group-label-999"


@pytest.mark.sphinx("text")
def test_assets_early_return_non_html(app: SphinxTestApp):
    """Exercise early return in assets.py for non-HTML builders."""
    content = """
Test
====
.. filter-tabs::
   .. tab:: A
      Content
"""
    build_index(app, content)
    assert (app.outdir / "index.txt").exists()
    assert not (app.outdir / "_static" / "filter_tabs_theme.css").exists()


def test_tab_directive_empty_arg():
    """Test _parse_tab_argument with empty string."""
    mock_state_machine = MagicMock()
    td = TabDirective("tab", ["name"], {}, StringList(), 1, 1, "", MagicMock(), mock_state_machine)
    with pytest.raises(ValueError, match="Tab argument cannot be empty"):
        td._parse_tab_argument("")


def test_init_safety_net():
    """Exercise _visit_skip_node and _depart_noop in __init__.py."""
    with pytest.raises(nodes.SkipNode):
        _visit_skip_node(None, nodes.Element())
    _depart_noop(None, nodes.Element())


@pytest.mark.sphinx("html")
def test_admonitions_disabled(app: SphinxTestApp):
    """Test collapsible admonitions when disabled via config."""
    app.config.filter_tabs_enable_collapsible_admonitions = False
    content = """
Test
====
.. admonition:: Test
   :class: sft-collapsible

   Content
"""
    build_index(app, content)

    soup = html_soup(app)
    assert not soup.select(".sft-fieldset")
    assert not soup.select("details")


@pytest.mark.sphinx("html")
def test_admonition_without_collapsible_class(app: SphinxTestApp):
    """Test that regular admonitions are not transformed."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test
====
.. admonition:: Regular

   Content
"""
    build_index(app, content)

    soup = html_soup(app)
    assert not soup.select("details")
    assert soup.select_one(".admonition-regular")


@pytest.mark.sphinx("html")
def test_legacy_generic_collapsible_class_is_ignored(app: SphinxTestApp):
    """The optional feature should not hook the generic 'collapsible' class."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    content = """
Test
====
.. admonition:: Legacy
   :class: collapsible

   Content
"""
    build_index(app, content)

    soup = html_soup(app)
    assert not soup.select("details")
    assert soup.select_one(".admonition.collapsible")


@pytest.mark.sphinx("html", confoverrides={"language": "da"})
def test_collapsible_admonition_fallback_summary_is_localized(app: SphinxTestApp):
    """The no-title fallback summary should use the active Sphinx locale."""
    app.config.filter_tabs_enable_collapsible_admonitions = True
    doctree = nodes.document({}, Reporter("test", 1, 5))
    admonition = nodes.admonition(classes=["sft-collapsible"])
    admonition += nodes.paragraph(text="Content without a title.")
    doctree += admonition

    setup_collapsible_admonitions(app, doctree, "index")

    summary = next(doctree.findall(SummaryNode))
    assert "Detaljer" in summary.astext()


def test_write_theme_css_ignored_for_non_html_builder():
    """Generated theme CSS is only written for HTML builders."""
    app = MagicMock()
    app.builder.format = "latex"
    write_theme_css(app, None)
    app.outdir.__truediv__.assert_not_called()


def test_configured_highlight_color_none_uses_theme_color():
    """None should behave like auto/theme highlight color."""
    app = MagicMock()
    app.config.filter_tabs_highlight_color = None

    assert _configured_highlight_color(app).startswith("var(--pst-color-primary")


def test_selector_count_for_build_handles_missing_or_unreadable_env():
    """Doctree inspection failures should not break CSS generation."""
    assert _selector_count_for_build(None) == SFT_DEFAULT_SELECTOR_COUNT

    env = MagicMock()
    env.found_docs = {"broken"}
    env.get_doctree.side_effect = RuntimeError("cannot read doctree")

    assert _selector_count_for_build(env) == SFT_DEFAULT_SELECTOR_COUNT


def test_register_static_assets_uses_add_static_dir_when_available():
    """Modern Sphinx should receive extension static files via add_static_dir()."""
    app = MagicMock()
    app.builder.format = "html"
    app.config.html_static_path = []

    register_static_assets(app)

    app.add_static_dir.assert_called_once()
    assert app.config.html_static_path == []
    app.add_css_file.assert_any_call("filter_tabs.css")
    app.add_css_file.assert_any_call("filter_tabs_theme.css")


def test_register_static_assets_falls_back_to_html_static_path():
    """Older supported Sphinx versions should still receive the static path."""

    class Builder:
        format = "html"

    class Config:
        def __init__(self) -> None:
            self.html_static_path: list[str] = []

    class LegacyApp:
        def __init__(self) -> None:
            self.builder = Builder()
            self.config = Config()
            self.css_files: list[str] = []

        def add_css_file(self, filename: str) -> None:
            self.css_files.append(filename)

    app = LegacyApp()
    register_static_assets(app)

    assert app.config.html_static_path
    assert app.css_files == ["filter_tabs.css", "filter_tabs_theme.css"]


def test_process_filter_tabs_nodes_invalid():
    """Directly exercise process_filter_tabs_nodes with invalid node."""
    app = MagicMock()
    app.builder.format = "html"
    app.config = MagicMock()
    doctree = nodes.document({}, Reporter("test", 1, 5))
    parent = nodes.section()
    ft_node = FilterTabsNode()
    parent += ft_node
    doctree += parent

    process_filter_tabs_nodes(app, doctree, "testdoc")

    assert ft_node not in parent
