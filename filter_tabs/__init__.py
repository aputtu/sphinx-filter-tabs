from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from docutils import nodes as docutils_nodes
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

__version__ = "1.6.0"

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
    RenderedFilterTabsNode,
    SummaryNode,
)
from .render_html import (
    depart_details_node,
    depart_filter_tab_node,
    depart_filter_tab_panel_node,
    depart_filter_tabs_content_node,
    depart_rendered_filter_tabs_node,
    depart_summary_node,
    visit_details_node,
    visit_filter_tab_node,
    visit_filter_tab_panel_node,
    visit_filter_tabs_content_node,
    visit_rendered_filter_tabs_node,
    visit_summary_node,
)
from .transforms import process_filter_tabs_nodes

__all__ = ["setup", "__version__"]

# Sphinx visitor functions receive the active translator and a concrete node
# subtype; the registration table intentionally stores those subtypes together.
NodeVisitorFunc = Callable[[Any, Any], None]


def _visit_skip_node(self: Any, node: docutils_nodes.Element) -> None:
    """Safety-net visitor for intermediate nodes: skip entirely."""
    raise docutils_nodes.SkipNode


def _depart_noop(self: Any, node: docutils_nodes.Element) -> None:
    pass


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the sphinx-filter-tabs extension."""

    app.add_config_value("filter_tabs_highlight_color", "auto", "html", [str])
    app.add_config_value("filter_tabs_theme_mode", "native", "html", [str])
    app.add_config_value("filter_tabs_flavor", "default", "html", [str])
    app.add_config_value("filter_tabs_debug_mode", False, "html", [bool])
    app.add_config_value("filter_tabs_enable_collapsible_admonitions", False, "html", [bool])

    app.add_message_catalog("sphinx-filter-tabs", str(Path(__file__).parent / "locale"))

    VisitorPair = tuple[NodeVisitorFunc, NodeVisitorFunc]
    _skip: VisitorPair = (_visit_skip_node, _depart_noop)
    _skip_builders = ("latex", "text", "man", "texinfo", "xml", "epub", "rinoh", "dummy")
    _skip_kwargs: dict[str, VisitorPair] = {b: _skip for b in _skip_builders}

    html_nodes: tuple[tuple[type[docutils_nodes.Element], VisitorPair], ...] = (
        (
            RenderedFilterTabsNode,
            (visit_rendered_filter_tabs_node, depart_rendered_filter_tabs_node),
        ),
        (FilterTabNode, (visit_filter_tab_node, depart_filter_tab_node)),
        (
            FilterTabsContentNode,
            (visit_filter_tabs_content_node, depart_filter_tabs_content_node),
        ),
        (FilterTabPanelNode, (visit_filter_tab_panel_node, depart_filter_tab_panel_node)),
        (DetailsNode, (visit_details_node, depart_details_node)),
        (SummaryNode, (visit_summary_node, depart_summary_node)),
    )
    for node_class, html_visitors in html_nodes:
        app.add_node(node_class, html=html_visitors, **_skip_kwargs)
    app.add_node(FilterTabsNode, html=_skip, **_skip_kwargs)
    app.add_node(FilterTabSlotNode, html=_skip, **_skip_kwargs)

    app.add_directive("filter-tabs", FilterTabsDirective)
    app.add_directive("tab", TabDirective)

    app.connect("builder-inited", register_static_assets)
    app.connect("doctree-resolved", process_filter_tabs_nodes)
    app.connect("doctree-resolved", setup_collapsible_admonitions)
    app.connect("env-updated", write_theme_css)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
