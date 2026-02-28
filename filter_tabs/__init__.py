from __future__ import annotations

from collections.abc import Callable
from typing import Any

from docutils import nodes as docutils_nodes
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

__version__ = "1.4.3"

from .admonitions import setup_collapsible_admonitions
from .assets import register_static_assets, write_theme_css
from .directives import FilterTabsDirective, TabDirective
from .nodes import (
    DetailsNode,
    FilterTabNode,
    FilterTabPanelNode,
    FilterTabsContentNode,
    FilterTabSlotNode,
    FilterTabsNode,
    SummaryNode,
)
from .render_html import (
    depart_details_node,
    depart_filter_tab_node,
    depart_filter_tab_panel_node,
    depart_filter_tabs_content_node,
    depart_filter_tabs_node,
    depart_summary_node,
    visit_details_node,
    visit_filter_tab_node,
    visit_filter_tab_panel_node,
    visit_filter_tabs_content_node,
    visit_filter_tabs_node,
    visit_summary_node,
)
from .transforms import process_filter_tabs_nodes

__all__ = ["setup", "__version__"]

# Type alias for the generic visitor/depart functions used as safety-net skips.
NodeVisitorFunc = Callable[[Any, docutils_nodes.Element], None]


def _visit_skip_node(self: NodeVisitorFunc, node: docutils_nodes.Element) -> None:
    """Safety-net visitor for intermediate nodes: skip entirely."""
    raise docutils_nodes.SkipNode


def _depart_noop(self: NodeVisitorFunc, node: docutils_nodes.Element) -> None:
    pass


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the sphinx-filter-tabs extension."""

    app.add_config_value("filter_tabs_highlight_color", "#007bff", "html", [str])
    app.add_config_value("filter_tabs_debug_mode", False, "html", [bool])
    app.add_config_value("filter_tabs_enable_collapsible_admonitions", True, "html", [bool])

    # Register message catalog for translations
    from pathlib import Path

    locale_dir = str(Path(__file__).parent / "locale")
    app.add_message_catalog("sphinx-filter-tabs", locale_dir)

    # Configuration for builders that don't support the interactive tab output.
    VisitorPair = tuple[NodeVisitorFunc, NodeVisitorFunc]
    _skip: VisitorPair = (_visit_skip_node, _depart_noop)
    _skip_builders = ("latex", "text", "man", "texinfo", "xml", "epub", "rinoh", "dummy")
    _skip_kwargs: dict[str, VisitorPair] = {b: _skip for b in _skip_builders}

    # Intermediate nodes — stored in .doctrees, replaced at write time.
    app.add_node(
        FilterTabsNode, html=(visit_filter_tabs_node, depart_filter_tabs_node), **_skip_kwargs
    )
    app.add_node(FilterTabSlotNode, html=_skip, **_skip_kwargs)

    # Resolved semantic nodes — only appear after doctree-resolved.
    app.add_node(
        FilterTabNode, html=(visit_filter_tab_node, depart_filter_tab_node), **_skip_kwargs
    )
    app.add_node(
        FilterTabsContentNode,
        html=(visit_filter_tabs_content_node, depart_filter_tabs_content_node),
        **_skip_kwargs,
    )
    app.add_node(
        FilterTabPanelNode,
        html=(visit_filter_tab_panel_node, depart_filter_tab_panel_node),
        **_skip_kwargs,
    )

    # Collapsible Admonition nodes
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node), **_skip_kwargs)
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node), **_skip_kwargs)

    app.add_directive("filter-tabs", FilterTabsDirective)
    app.add_directive("tab", TabDirective)

    app.connect("builder-inited", register_static_assets)
    app.connect("doctree-resolved", process_filter_tabs_nodes)
    app.connect("doctree-resolved", setup_collapsible_admonitions)
    app.connect("build-finished", write_theme_css)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
