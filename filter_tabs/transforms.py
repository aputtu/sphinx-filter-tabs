from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util import logging

from .config import FilterTabsConfig
from .nodes import FilterTabSlotNode, FilterTabsNode
from .render_fallback import render_fallback
from .render_html import render_html
from .utils import IDGenerator

logger = logging.getLogger(__name__)


def validate_tabs_structure(ft_node: FilterTabsNode) -> bool:
    """Perform a structural check on a FilterTabsNode before rendering.

    Verifies that the node contains at least one slot and that all slots
    have a name. Returns True if valid, False otherwise.
    """
    slots = [c for c in ft_node.children if isinstance(c, FilterTabSlotNode)]

    if not slots:
        logger.error(f"filter-tabs: {ft_node.source}:{ft_node.line}: Missing tab slots.")
        return False

    for i, slot in enumerate(slots):
        if not slot.get("tab_name"):
            logger.error(
                f"filter-tabs: {ft_node.source}:{ft_node.line}: Slot {i} missing tab_name."
            )
            return False

    return True


def process_filter_tabs_nodes(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace each FilterTabsNode with builder-appropriate output.

    Connected to the ``doctree-resolved`` event.
    """
    config = FilterTabsConfig.from_sphinx_config(app.config)
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

        slots = [c for c in ft_node.children if isinstance(c, FilterTabSlotNode)]
        general_content = [c for c in ft_node.children if not isinstance(c, FilterTabSlotNode)]

        current = doctree.get(doc_counter_key, 0) + 1
        doctree[doc_counter_key] = current
        group_id = f"filter-group-{docname.replace('/', '-')}-{current}"
        id_gen = IDGenerator(group_id)

        if config.debug_mode:
            logger.info(
                f"filter-tabs: resolving group '{group_id}' for builder '{app.builder.name}'"
            )

        if is_html:
            replacement = render_html(
                slots,
                general_content,
                custom_legend,
                id_gen,
                config,
                app.env,
            )
        else:
            replacement = render_fallback(slots, general_content)

        ft_node.replace_self(replacement)
