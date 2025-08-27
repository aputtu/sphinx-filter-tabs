# filter_tabs/renderer.py
"""
Updated FilterTabsRenderer with dual implementation support for gradual
migration to improved accessibility.
"""

from __future__ import annotations

import re
import uuid
import copy
import shutil
from pathlib import Path
from docutils import nodes
from sphinx.util import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from docutils.parsers.rst import Directive

from .config import FilterTabsConfig

logger = logging.getLogger(__name__)

# Constants
SFT_CONTAINER = "sft-container"
SFT_FIELDSET = "sft-fieldset"
SFT_LEGEND = "sft-legend"
SFT_TAB_BAR = "sft-tab-bar"
SFT_RADIO_GROUP = "sft-radio-group"
SFT_CONTENT = "sft-content"
SFT_PANEL = "sft-panel"


class DualImplementationRenderer:
    """
    Handles rendering for both legacy and improved accessibility implementations.
    """
    
    def __init__(self, directive: Directive, tab_data: List[Dict], general_content: List[nodes.Node]):
        self.directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.config = FilterTabsConfig(self.env.app)
        self.tab_data = tab_data
        self.general_content = general_content
        
        # Generate unique group ID
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        self.group_id = f"filter-group-{self.env.filter_tabs_counter}"
        
    def render_html(self) -> List[nodes.Node]:
        """Route to appropriate implementation based on configuration."""
        implementation_mode = self.config.get_implementation_mode()
        
        if self.config.config.filter_tabs_debug_mode:
            logger.info(f"Rendering filter-tabs group {self.group_id} using {implementation_mode} implementation")
        
        if implementation_mode == "improved":
            return self._render_improved_html()
        else:
            return self._render_legacy_html()
    
    def render_fallback(self) -> List[nodes.Node]:
        """Render for non-HTML builders (LaTeX, etc.) - unchanged from original."""
        output_nodes: List[nodes.Node] = []
        
        # Add general content first if it exists
        if self.general_content:
            output_nodes.extend(copy.deepcopy(self.general_content))
        
        # Add each tab's content in a titled admonition
        for tab in self.tab_data:
            admonition = nodes.admonition()
            admonition += nodes.title(text=tab['name'])
            admonition.extend(copy.deepcopy(tab['content']))
            output_nodes.append(admonition)
        
        return output_nodes
    
    def _render_legacy_html(self) -> List[nodes.Node]:
        """Legacy implementation - preserves existing behavior."""
        # Get container attributes from config
        container_attrs = self.config.get_container_attributes(self.group_id)
        container = ContainerNode(**container_attrs)

        # Build the semantic structure using fieldset and hidden legend
        fieldset = FieldsetNode()
        tab_names = [tab['name'] for tab in self.tab_data]
        legend = LegendNode(classes=[SFT_LEGEND])
        legend += nodes.Text(f"Filter by: {', '.join(tab_names)}")
        fieldset += legend
        
        # Generate and add dynamic CSS
        self._generate_dynamic_css()
        
        # The tab bar container
        tab_bar = ContainerNode(classes=[SFT_TAB_BAR])
        fieldset += tab_bar

        # The content area holds all the panels
        content_area = ContainerNode(classes=[SFT_CONTENT])
        fieldset += content_area

        # Determine default tab
        default_index = next((i for i, tab in enumerate(self.tab_data) if tab['is_default']), 0)
        
        # Create radio buttons and labels (legacy style)
        for i, tab in enumerate(self.tab_data):
            radio_id = f"{self.group_id}-tab-{i}"
            panel_id = f"{radio_id}-panel"
            
            # Radio button for state management
            radio = RadioInputNode(type='radio', name=self.group_id, ids=[radio_id])
            
            # Add aria-label if provided
            if tab.get('aria_label'):
                radio['aria-label'] = tab['aria_label']
            
            if i == default_index:
                radio['checked'] = 'checked'
            tab_bar += radio

            # Label without additional ARIA attributes
            label = LabelNode(for_id=radio_id)
            label += nodes.Text(tab['name'])
            tab_bar += label

        # Create the general panel if there's general content
        if self.general_content:
            general_panel = PanelNode(
                classes=[SFT_PANEL], 
                **{'data-filter': 'General'}
            )
            general_panel.extend(copy.deepcopy(self.general_content))
            content_area += general_panel

        # Create all tab panels
        for i, tab in enumerate(self.tab_data):
            radio_id = f"{self.group_id}-tab-{i}"
            panel_id = f"{radio_id}-panel"
            
            panel_attrs = {
                'classes': [SFT_PANEL],
                'ids': [panel_id],
                'role': 'tabpanel',  # Legacy uses tabpanel role
                'aria-labelledby': radio_id,
                'tabindex': '0'
            }
            panel = PanelNode(**panel_attrs)
            panel.extend(copy.deepcopy(tab['content']))
            content_area += panel

        container.children = [fieldset]
        return [container]
    
    def _render_improved_html(self) -> List[nodes.Node]:
        """Improved accessibility implementation with proper radiogroup semantics."""
        # Get container attributes from config (includes data-accessibility="improved")
        container_attrs = self.config.get_container_attributes(self.group_id)
        container = ContainerNode(**container_attrs)

        # Build semantic structure with proper radiogroup
        fieldset = FieldsetNode(role="radiogroup")
        
        tab_names = [tab['name'] for tab in self.tab_data]
        # Create meaningful, visible legend
        legend = LegendNode(classes=[SFT_LEGEND], ids=[f"{self.group_id}-legend"])
        legend += nodes.Text(f"Choose {self._get_content_type()}: {', '.join(tab_names)}")
        fieldset += legend
        
        # Generate and add dynamic CSS
        self._generate_dynamic_css()
        
        # Radio group container (different from legacy tab bar)
        radio_group = ContainerNode(classes=[SFT_RADIO_GROUP])
        fieldset += radio_group

        # Content area should be a sibling of the radio_group, not a child
        content_area = ContainerNode(classes=[SFT_CONTENT])
        fieldset += content_area # <-- FIX: Move this line here...
        # radio_group += content_area <-- ...from here.

        # Determine default tab
        default_index = next((i for i, tab in enumerate(self.tab_data) if tab['is_default']), 0)
        
        # Create radio buttons with proper descriptions and add them to the radio_group
        for i, tab in enumerate(self.tab_data):
            radio_id = f"{self.group_id}-radio-{i}"
            desc_id = f"{self.group_id}-desc-{i}"
            
            # Radio button with ARIA description
            radio = RadioInputNode(
                type='radio', 
                name=self.group_id, 
                ids=[radio_id],
                **{"aria-describedby": desc_id}
            )
            
            if tab.get('aria_label'):
                radio['aria-label'] = tab['aria_label']
            
            if i == default_index:
                radio['checked'] = 'checked'
            radio_group += radio

            # Label for visual interaction
            label = LabelNode(for_id=radio_id)
            label += nodes.Text(tab['name'])
            radio_group += label
            
            # Screen reader description
            desc = nodes.inline(ids=[desc_id], classes=["sr-only"])
            desc += nodes.Text(f"Show {tab['name'].lower()} content")
            radio_group += desc

        # Create the general panel if there's general content
        if self.general_content:
            general_panel = PanelNode(
                classes=[SFT_PANEL], 
                **{'data-filter': 'General'}
            )
            general_panel.extend(copy.deepcopy(self.general_content))
            content_area += general_panel

        # Create all tab panels and add them to the content_area
        for i, tab in enumerate(self.tab_data):
            radio_id = f"{self.group_id}-radio-{i}"
            panel_id = f"{self.group_id}-panel-{i}"
            
            panel_attrs = {
                'classes': [SFT_PANEL],
                'ids': [panel_id],
                'role': 'region',
                'aria-labelledby': radio_id,
                'tabindex': '0',
                'data-tab': tab['name'].lower().replace(' ', '-')
            }
            panel = PanelNode(**panel_attrs)
            panel.extend(copy.deepcopy(tab['content']))
            content_area += panel

        container.children = [fieldset]
        return [container]
    
    def _get_content_type(self) -> str:
        """Infer content type from tab names for better legend text."""
        tab_names = [tab['name'].lower() for tab in self.tab_data]
        
        # Common patterns to provide better context
        if any(name in tab_names for name in ['python', 'javascript', 'java', 'c++', 'rust']):
            return "programming language"
        elif any(name in tab_names for name in ['windows', 'mac', 'linux', 'macos']):
            return "operating system"
        elif any(name in tab_names for name in ['pip', 'conda', 'npm', 'yarn']):
            return "package manager"
        elif any(name in tab_names for name in ['cli', 'gui', 'terminal', 'command']):
            return "interface"
        else:
            return "option"
    
    def _generate_dynamic_css(self) -> None:
        """Generate CSS rules for showing/hiding panels based on radio button state."""
        css_rules = []
        
        for i, tab in enumerate(self.tab_data):
            if self.config.get_implementation_mode() == "improved":
                radio_id = f"{self.group_id}-radio-{i}"
                # Make the panel selector more specific by targeting the data-tab attribute
                panel_selector = f'.sft-panel[data-tab="{tab["name"].lower().replace(" ", "-")}"]'
                
                # UPDATE THIS LINE
                css_rules.append(
                    f'.sft-radio-group:has(#{radio_id}:checked) ~ .sft-content > {panel_selector} {{ display: block; }}'
                )
            else:
                # Legacy implementation
                radio_id = f"{self.group_id}-tab-{i}"
                panel_id = f"{radio_id}-panel"
                css_rules.append(
                    f'.{SFT_TAB_BAR}:has(#{radio_id}:checked) ~ .{SFT_CONTENT} > #{panel_id} {{ display: block; }}'
                )
        
        # Write dynamic CSS to file
        css_content = '\n'.join(css_rules)
        static_dir = Path(self.env.app.outdir) / '_static'
        static_dir.mkdir(parents=True, exist_ok=True)
        css_filename = f"dynamic-filter-tabs-{self.group_id}.css"
        (static_dir / css_filename).write_text(css_content, encoding='utf-8')
        self.env.app.add_css_file(css_filename)

# Custom nodes (these remain the same as original)
class ContainerNode(nodes.General, nodes.Element):
    pass

class FieldsetNode(nodes.General, nodes.Element): 
    pass

class LegendNode(nodes.General, nodes.Element): 
    pass

class RadioInputNode(nodes.General, nodes.Element): 
    pass

class LabelNode(nodes.General, nodes.Element): 
    pass

class PanelNode(nodes.General, nodes.Element): 
    pass


# HTML visitor functions (these need minor updates to handle new attributes)
def visit_container_node(self, node: ContainerNode) -> None:
    attrs = _get_html_attrs(node)
    self.body.append(self.starttag(node, 'div', **attrs))

def depart_container_node(self, node: ContainerNode) -> None:
    self.body.append('</div>')

def visit_fieldset_node(self, node: FieldsetNode) -> None:
    attrs = _get_html_attrs(node)
    if 'role' in node.attributes:
        attrs['role'] = node['role']
    self.body.append(self.starttag(node, 'fieldset', CLASS=SFT_FIELDSET, **attrs))

def depart_fieldset_node(self, node: FieldsetNode) -> None:
    self.body.append('</fieldset>')

def visit_legend_node(self, node: LegendNode) -> None:
    self.body.append(self.starttag(node, 'legend', CLASS=SFT_LEGEND))

def depart_legend_node(self, node: LegendNode) -> None:
    self.body.append('</legend>')

def visit_radio_input_node(self, node: RadioInputNode) -> None:
    attrs = _get_html_attrs(node)
    # Include important attributes
    for key in ['type', 'name', 'checked', 'aria-label', 'aria-describedby']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'input', **attrs))

def depart_radio_input_node(self, node: RadioInputNode) -> None:
    pass

def visit_label_node(self, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    if 'for_id' in node.attributes:
        attrs['for'] = node['for_id']
    self.body.append(self.starttag(node, 'label', **attrs))

def depart_label_node(self, node: LabelNode) -> None:
    self.body.append('</label>')

def visit_panel_node(self, node: PanelNode) -> None:
    attrs = _get_html_attrs(node)
    # Handle ARIA and data attributes
    for key in ['role', 'aria-labelledby', 'tabindex', 'data-filter', 'data-tab']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'div', CLASS=SFT_PANEL, **attrs))

def depart_panel_node(self, node: PanelNode) -> None:
    self.body.append('</div>')


def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    """Helper to get clean dictionary of HTML attributes from docutils node."""
    attrs = node.attributes.copy()
    # Remove docutils-internal attributes
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'):
        attrs.pop(key, None)
    return attrs
