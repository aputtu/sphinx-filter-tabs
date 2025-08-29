# filter_tabs/renderer.py
"""
Renders the HTML and fallback output for the filter-tabs directive.

This module contains the FilterTabsRenderer class which is responsible for
converting the collected tab data into a final doctree structure.
"""

from __future__ import annotations

import copy
from pathlib import Path
from docutils import nodes
from sphinx.util import logging
from typing import TYPE_CHECKING, Any, Dict, List

from .models import TabData, FilterTabsConfig, IDGenerator
from .parsers import ContentTypeInferrer
from .nodes import ContainerNode, FieldsetNode, LegendNode, RadioInputNode, LabelNode, PanelNode


if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from docutils.parsers.rst import Directive

logger = logging.getLogger(__name__)

# Constants
SFT_CONTAINER = "sft-container"
SFT_FIELDSET = "sft-fieldset"
SFT_LEGEND = "sft-legend"
SFT_RADIO_GROUP = "sft-radio-group"
SFT_CONTENT = "sft-content"
SFT_PANEL = "sft-panel"


class FilterTabsRenderer:
    """
    Renders filter tabs with improved accessibility implementation.
    
    Now uses type-safe TabData objects and centralized ID generation.
    """
    
    def __init__(self, directive: Directive, tab_data: List[TabData], general_content: List[nodes.Node]):
        """
        Initialize the renderer.
        
        Args:
            directive: The FilterTabsDirective instance
            tab_data: List of TabData objects containing tab information
            general_content: List of nodes for general content
        """
        self.directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.app = self.env.app
        self.tab_data = tab_data
        self.general_content = general_content
        
        # Load configuration
        self.config = FilterTabsConfig.from_sphinx_config(self.app.config)
        
        # Generate unique group ID and create ID generator
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        self.group_id = f"filter-group-{self.env.filter_tabs_counter}"
        self.id_gen = IDGenerator(self.group_id)
        
    def render_html(self) -> List[nodes.Node]:
        """
        Render HTML with improved accessibility implementation.
        
        Returns:
            List of docutils nodes representing the complete tab structure
        """
        if self.config.debug_mode:
            logger.info(f"Rendering filter-tabs group {self.group_id}")
            self._log_tab_data()

        # Generate dynamic CSS as a style node
        style_node = self._generate_dynamic_css()
        
        # Create container with proper attributes
        container_attrs = self._get_container_attributes()
        container = ContainerNode(**container_attrs)

        # Build semantic structure
        fieldset = self._create_fieldset()
        container.children = [fieldset]
        
        return [style_node, container]
    
    def render_fallback(self) -> List[nodes.Node]:
        """
        Render for non-HTML builders (LaTeX, etc.).
        
        Returns:
            List of nodes suitable for non-HTML output
        """
        output_nodes: List[nodes.Node] = []
        
        # Add general content first if it exists
        if self.general_content:
            output_nodes.extend(copy.deepcopy(self.general_content))
        
        # Add each tab's content in a titled admonition
        for tab in self.tab_data:
            admonition = nodes.admonition()
            admonition += nodes.title(text=tab.name)
            admonition.extend(copy.deepcopy(tab.content))
            output_nodes.append(admonition)
        
        return output_nodes
    
    def _create_fieldset(self) -> FieldsetNode:
        """Create the main fieldset structure with all components."""
        fieldset = FieldsetNode(role="radiogroup")
        
        # Create legend
        legend = self._create_legend()
        fieldset += legend
        
        # Create radio group
        radio_group = ContainerNode(classes=[SFT_RADIO_GROUP])
        self._populate_radio_group(radio_group)
        fieldset += radio_group
        
        # Create content area
        content_area = ContainerNode(classes=[SFT_CONTENT])
        self._populate_content_area(content_area)
        fieldset += content_area
        
        return fieldset
    
    def _create_legend(self) -> LegendNode:
        """Create a meaningful, visible legend."""
        tab_names = [tab.name for tab in self.tab_data]
        content_type = ContentTypeInferrer.infer_type(tab_names)
        
        legend = LegendNode(
            classes=[SFT_LEGEND],
            ids=[self.id_gen.legend_id()]
        )
        legend_text = f"Choose {content_type}: {', '.join(tab_names)}"
        legend += nodes.Text(legend_text)
        
        return legend
    
    def _populate_radio_group(self, radio_group: ContainerNode) -> None:
        """Populate the radio group with radio buttons and labels."""
        # Find default tab index
        default_index = next(
            (i for i, tab in enumerate(self.tab_data) if tab.is_default),
            0
        )
     
        for i, tab in enumerate(self.tab_data):
            # Create radio button
            radio = self._create_radio_button(i, tab, is_checked=(i == default_index))
            radio_group += radio
            
            # Create label
            label = self._create_label(i, tab)
            radio_group += label
            
            # Create screen reader description
            desc_text = f"Show content for {tab.name}"
            description_node = ContainerNode(
                classes=['sr-only'], ids=[self.id_gen.desc_id(i)]
            )
            description_node += nodes.Text(desc_text)
            radio_group += description_node
    
    def _create_radio_button(self, index: int, tab: TabData, is_checked: bool) -> RadioInputNode:
        """Create a radio button for a tab."""
        radio = RadioInputNode(
            classes=['sr-only'],
            type='radio',
            name=self.group_id,
            ids=[self.id_gen.radio_id(index)],
            **{'aria-describedby': self.id_gen.desc_id(index)}
        )
        
        if tab.aria_label:
            radio['aria-label'] = tab.aria_label
        
        if is_checked:
            radio['checked'] = 'checked'
            
        return radio
    
    def _create_label(self, index: int, tab: TabData) -> LabelNode:
        """Create a label for a radio button."""
        label = LabelNode(for_id=self.id_gen.radio_id(index))
        label += nodes.Text(tab.name)
        return label
    
    def _populate_content_area(self, content_area: ContainerNode) -> None:
        """Populate the content area with general and tab panels."""
        # Add general panel if there's general content
        if self.general_content:
            general_panel = PanelNode(
                classes=[SFT_PANEL],
                **{'data-filter': 'General'}
            )
            general_panel.extend(copy.deepcopy(self.general_content))
            content_area += general_panel
        
        # Add tab panels
        for i, tab in enumerate(self.tab_data):
            panel = self._create_tab_panel(i, tab)
            content_area += panel
    
    def _create_tab_panel(self, index: int, tab: TabData) -> PanelNode:
        """Create a panel for tab content."""
        panel_attrs = {
            'classes': [SFT_PANEL],
            'ids': [self.id_gen.panel_id(index)],
            'role': 'region',
            'aria-labelledby': self.id_gen.radio_id(index),
            'tabindex': '0',
            'data-tab': tab.name.lower().replace(' ', '-')
        }
        panel = PanelNode(**panel_attrs)
        panel.extend(copy.deepcopy(tab.content))
        return panel
    
    def _get_container_attributes(self) -> Dict[str, Any]:
        """Get container attributes with CSS custom properties."""
        return {
            'classes': [SFT_CONTAINER],
            'role': 'region',
            'aria-labelledby': self.id_gen.legend_id(),
            'style': self.config.to_css_properties()
        }
    
    def _generate_dynamic_css(self) -> nodes.raw:
        """Generate CSS rules and return them as a raw HTML style node."""
        css_rules = []
        
        for i, tab in enumerate(self.tab_data):
            radio_id = self.id_gen.radio_id(i)
            panel_selector = f'.sft-panel[data-tab="{tab.name.lower().replace(" ", "-")}"]'
            
            css_rules.append(
                f'.sft-radio-group:has(#{radio_id}:checked) ~ .sft-content > {panel_selector} {{ display: block; }}'
            )

        # Embed dynamic CSS in a style tag
        css_content = '\n'.join(css_rules)
        style_node = nodes.raw(
            text=f"<style>\n{css_content}\n</style>", format='html'
        )
        return style_node
    
    def _log_tab_data(self) -> None:
        """Log tab data for debugging purposes."""
        logger.info(f"Tab data for group {self.group_id}:")
        for i, tab in enumerate(self.tab_data):
            logger.info(
                f"  Tab {i}: name='{tab.name}', "
                f"is_default={tab.is_default}, "
                f"aria_label='{tab.aria_label or 'None'}'"
            )
        default_index = next(
            (i for i, tab in enumerate(self.tab_data) if tab.is_default),
            0
        )
        logger.info(f"  Selected default_index: {default_index}")
