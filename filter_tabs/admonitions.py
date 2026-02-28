from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx

from .nodes import DetailsNode, SummaryNode

COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"


def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Convert admonitions with 'collapsible' class to details/summary elements."""
    if app.builder.format != "html":
        return
    if not app.config.filter_tabs_enable_collapsible_admonitions:
        return

    for node in list(doctree.findall(nodes.admonition)):
        if "collapsible" not in node.get("classes", []):
            continue

        is_expanded = "expanded" in node.get("classes", [])

        # Only look at direct children to find the title, otherwise we might
        # steal the title from a nested admonition or figure.
        title_node = None
        if node.children and isinstance(node.children[0], nodes.title):
            title_node = node.children[0]

        summary_text = title_node.astext() if title_node else "Details"

        if title_node:
            node.remove(title_node)

        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node["open"] = "open"

        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node

        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        # Move children instead of deepcopying them so reference identities
        # (and nested title nodes) aren't lost/duplicated for other transforms.
        for child in list(node.children):
            node.remove(child)
            content_node += child

        details_node += content_node

        node.replace_self(details_node)
