from __future__ import annotations

from collections.abc import Iterable

from docutils import nodes


class FilterTabsNode(nodes.General, nodes.Element):
    """Parse-time container for a set of filter tabs.

    This node contains children rendered as ``FilterTabSlotNode`` and any
    general content that should be available to normal Sphinx transforms before
    ``process_filter_tabs_nodes`` resolves the group.

    Attributes:
    - ``custom_legend`` – optional visible legend override
    - ``hide_legend`` – hide the legend visually while preserving it for AT
    """

    pass


class RenderedFilterTabsNode(nodes.General, nodes.Element):
    """Resolved HTML container for a set of filter tabs.

    This node is created after source tab groups have been validated. It holds
    ``FilterTabNode`` controls and ``FilterTabsContentNode`` content.

    Attributes:
    - ``legend_text``
    - ``legend_id``
    - ``hide_legend``
    - ``group_id``
    """

    pass


class FilterTabSlotNode(nodes.General, nodes.Element):
    """Marks one tab's content inside a ``FilterTabsNode`` during parsing.

    Attributes:
    - ``tab_name``   – display name of the tab
    - ``is_default`` – whether this tab is initially selected
    - ``aria_label`` – optional ARIA label override
    """

    pass


def split_filter_tab_children(
    children: Iterable[nodes.Node],
) -> tuple[list[FilterTabSlotNode], list[nodes.Node]]:
    """Split parsed filter-tabs children into tab slots and general content."""
    slots: list[FilterTabSlotNode] = []
    general_content: list[nodes.Node] = []
    for child in children:
        if isinstance(child, FilterTabSlotNode):
            slots.append(child)
        else:
            general_content.append(child)
    return slots, general_content


class FilterTabNode(nodes.General, nodes.Element):
    """Represents a single tab's selection marker (radio + label) in the resolved tree.

    Attributes carry all metadata necessary for the HTML renderer:
    - ``tab_name``
    - ``is_default``
    - ``aria_label``
    - ``radio_id``
    - ``label_id``
    - ``desc_id``
    - ``panel_id``
    - ``tab_index``
    - ``group_id``
    """

    pass


class FilterTabsContentNode(nodes.General, nodes.Element):
    """Container for all panels (general and tab-specific) in the resolved tree."""

    pass


class FilterTabPanelNode(nodes.General, nodes.Element):
    """Represents a content panel in the resolved tree.

    Attributes:
    - ``data-filter`` for general content panels
    - ``data-tab`` and ``data-tab-index`` for tab-specific panels
    """

    pass


class DetailsNode(nodes.General, nodes.Element):
    """HTML <details> equivalent for collapsible admonitions."""

    pass


class SummaryNode(nodes.General, nodes.Element):
    """HTML <summary> equivalent for collapsible admonitions."""

    pass
