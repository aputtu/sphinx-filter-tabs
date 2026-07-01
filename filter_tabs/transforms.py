from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.locale import get_translation
from sphinx.util import logging

from .constants import SFT_WARN_THRESHOLD
from .nodes import FilterTabsNode, split_filter_tab_children
from .render_fallback import render_fallback
from .render_html import render_html
from .utils import IDGenerator

logger = logging.getLogger(__name__)
_ = get_translation("sphinx-filter-tabs")


def validate_tabs_structure(ft_node: FilterTabsNode) -> bool:
    """Perform a structural check on a FilterTabsNode before rendering.

    Verifies that the node contains at least one slot and that all slots
    have a name. Returns True if valid, False otherwise.
    """
    slots, _general_content = split_filter_tab_children(ft_node.children)

    if not slots:
        logger.error(
            "filter-tabs: Missing tab slots.",
            type="filter-tabs",
            subtype="structure",
            location=ft_node,
        )
        return False

    for i, slot in enumerate(slots):
        if not slot.get("tab_name"):
            logger.error(
                "filter-tabs: Slot %s missing tab_name.",
                i,
                type="filter-tabs",
                subtype="structure",
                location=slot,
            )
            return False

    return True


def process_filter_tabs_nodes(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace each FilterTabsNode with builder-appropriate output.

    Connected to the ``doctree-resolved`` event.
    """
    is_html = app.builder.format == "html"

    # Per-document counter stored on the doctree node itself.
    doc_counter_key = "_filter_tabs_counter"

    # We iterate in reverse to allow safe nested replacement.
    for ft_node in reversed(list(doctree.findall(FilterTabsNode))):
        if not validate_tabs_structure(ft_node):
            # If invalid, we just remove it to prevent a crash, but the log
            # already contains the error.
            ft_node.parent.remove(ft_node)
            continue

        custom_legend: str | None = ft_node.get("custom_legend")
        hide_legend = bool(ft_node.get("hide_legend", False))

        slots, general_content = split_filter_tab_children(ft_node.children)
        n = len(slots)
        if n > SFT_WARN_THRESHOLD:
            logger.warning(
                _(
                    "filter-tabs: a tab group with {n} tabs was found. "
                    "Tab groups this large can be hard to navigate; "
                    "consider restructuring the content."
                ).format(n=n),
                type="filter-tabs",
                subtype="large-group",
                location=ft_node,
            )

        current = doctree.get(doc_counter_key, 0) + 1
        doctree[doc_counter_key] = current
        safe_docname = nodes.make_id(docname) or "document"
        group_id = f"filter-group-{safe_docname}-{current}"
        id_gen = IDGenerator(group_id)

        if getattr(app.config, "filter_tabs_debug_mode", False):
            logger.info(
                f"filter-tabs: resolving group '{group_id}' for builder '{app.builder.name}'"
            )

        if is_html:
            replacement = render_html(
                slots,
                general_content,
                custom_legend,
                hide_legend,
                id_gen,
            )
        else:
            replacement = render_fallback(slots, general_content)

        ft_node.replace_self(replacement)
