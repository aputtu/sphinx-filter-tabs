from __future__ import annotations

from docutils import nodes

from .nodes import FilterTabSlotNode


def render_fallback(
    slots: list[FilterTabSlotNode],
    general_content: list[nodes.Node],
) -> list[nodes.Node]:
    """Produce plain admonition nodes for LaTeX and other non-HTML builders."""
    output: list[nodes.Node] = []
    if general_content:
        output.extend(c.deepcopy() for c in general_content)
    for slot in slots:
        admonition = nodes.admonition()
        admonition += nodes.title(text=slot["tab_name"])
        admonition.extend(c.deepcopy() for c in slot.children)
        output.append(admonition)
    return output
