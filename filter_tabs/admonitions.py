from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.locale import get_translation

from .constants import (
    SFT_COLLAPSIBLE_CLASS,
    SFT_COLLAPSIBLE_CONTENT,
    SFT_COLLAPSIBLE_SECTION,
    SFT_CUSTOM_ARROW,
    SFT_EXPANDED_CLASS,
)
from .nodes import DetailsNode, SummaryNode

_ = get_translation("sphinx-filter-tabs")


def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Convert opted-in admonitions to details/summary elements."""
    if app.builder.format != "html":
        return
    if not app.config.filter_tabs_enable_collapsible_admonitions:
        return

    for node in list(doctree.findall(nodes.admonition)):
        classes: list[str] = node.get("classes", [])
        if SFT_COLLAPSIBLE_CLASS not in classes:
            continue

        is_expanded = SFT_EXPANDED_CLASS in classes

        # Only look at direct children to find the title, otherwise we might
        # steal the title from a nested admonition or figure.
        title_node = None
        if node.children and isinstance(node.children[0], nodes.title):
            title_node = node.children[0]

        if title_node:
            node.remove(title_node)

        details_node = DetailsNode(classes=[SFT_COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node["open"] = "open"

        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[SFT_CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        if title_node:
            title_content = nodes.inline()
            for child in list(title_node.children):
                title_node.remove(child)
                title_content += child
            summary_node += title_content
        else:
            summary_node += nodes.Text(_("Details"))
        details_node += summary_node

        content_node = nodes.container(classes=[SFT_COLLAPSIBLE_CONTENT])
        # Move children instead of deepcopying them so reference identities
        # (and nested title nodes) aren't lost/duplicated for other transforms.
        for child in list(node.children):
            node.remove(child)
            content_node += child

        details_node += content_node

        node.replace_self(details_node)
