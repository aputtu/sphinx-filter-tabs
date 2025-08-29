# filter_tabs/nodes.py
"""Custom Docutils nodes for the sphinx-filter-tabs extension."""

from docutils import nodes

class ContainerNode(nodes.General, nodes.Element): pass
class FieldsetNode(nodes.General, nodes.Element): pass
class LegendNode(nodes.General, nodes.Element): pass
class RadioInputNode(nodes.General, nodes.Element): pass
class LabelNode(nodes.General, nodes.Element): pass
class PanelNode(nodes.General, nodes.Element): pass
class DetailsNode(nodes.General, nodes.Element): pass
class SummaryNode(nodes.General, nodes.Element): pass
