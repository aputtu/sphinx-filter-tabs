from __future__ import annotations

from docutils import nodes


class FilterTabsNode(nodes.General, nodes.Element):
    """The main container for a set of filter tabs.

    In the intermediate doctree (at parse time), this node contains children
    rendered as ``FilterTabSlotNode`` and any general content.

    In the resolved doctree (after ``process_filter_tabs_nodes``), this node
    becomes the final semantic container, holding children of type
    ``FilterTabNode`` and ``FilterTabsContentNode``.
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


class FilterTabNode(nodes.General, nodes.Element):
    """Represents a single tab's selection marker (radio + label) in the resolved tree.

    Attributes carry all metadata necessary for the HTML renderer:
    - ``tab_name``
    - ``is_default``
    - ``aria_label``
    - ``radio_id``
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
    - ``data_filter`` (e.g., "General" or lowercase tab name)
    - ``tab_index``
    - ``panel_id``
    - ``aria_labelledby`` (the radio_id of the corresponding tab)
    """

    pass


class DetailsNode(nodes.General, nodes.Element):
    """HTML <details> equivalent for collapsible admonitions."""

    pass


class SummaryNode(nodes.General, nodes.Element):
    """HTML <summary> equivalent for collapsible admonitions."""

    pass
