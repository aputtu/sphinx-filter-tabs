# filter_tabs/renderer.py
"""
Simplified FilterTabsRenderer with only improved accessibility implementation.
"""

from __future__ import annotations

import copy
from pathlib import Path
from docutils import nodes
from sphinx.util import logging
from typing import TYPE_CHECKING, Any, Dict, List

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
    """
    
    def __init__(self, directive: Directive, tab_data: List[Dict], general_content: List[nodes.Node]):
        self.directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.app = self.env.app
        self.tab_data = tab_data
        self.general_content = general_content
        
        # Generate unique group ID
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        self.group_id = f"filter-group-{self.env.filter_tabs_counter}"
        
    def render_html(self) -> List[nodes.Node]:
        """Render HTML with improved accessibility implementation."""
        if self.app.config.filter_tabs_debug_mode:
            logger.info(f"Rendering filter-tabs group {self.group_id}")
        
        # Create container with proper attributes
        container_attrs = self._get_container_attributes()
        container = ContainerNode(**container_attrs)

        # Build semantic structure with proper radiogroup
        fieldset = FieldsetNode(role="radiogroup")
        
        # Create meaningful, visible legend
        tab_names = [tab['name'] for tab in self.tab_data]
        legend = LegendNode(classes=[SFT_LEGEND], ids=[f"{self.group_id}-legend"])
        legend += nodes.Text(f"Choose {self._get_content_type()}: {', '.join(tab_names)}")
        fieldset += legend
        
        # Generate and add dynamic CSS
        self._generate_dynamic_css()
        
        # Radio group container
        radio_group = ContainerNode(classes=[SFT_RADIO_GROUP])
        fieldset += radio_group

        # Content area
        content_area = ContainerNode(classes=[SFT_CONTENT])
        fieldset += content_area

        # Determine default tab
        default_index = next((i for i, tab in enumerate(self.tab_data) if tab['is_default']), 0)

        # Debug output:
        if self.app.config.filter_tabs_debug_mode:
            logger.info(f"Tab data for group {self.group_id}:")
            for i, tab in enumerate(self.tab_data):
                logger.info(f"  Tab {i}: name='{tab['name']}', is_default={tab['is_default']}")
            logger.info(f"  Selected default_index: {default_index}")
        
        # Create radio buttons with proper descriptions
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

        # Create all tab panels
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
    
    def render_fallback(self) -> List[nodes.Node]:
        """Render for non-HTML builders (LaTeX, etc.)."""
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
    
    def _get_container_attributes(self) -> Dict[str, Any]:
        """Get container attributes with CSS custom properties."""
        attrs = {
            'classes': [SFT_CONTAINER],
            'role': 'region',
            'aria-labelledby': f'{self.group_id}-legend',
            'style': self._get_css_custom_properties()
        }
        return attrs
    
    def _get_css_custom_properties(self) -> str:
        """Generate CSS custom properties from configuration."""
        config = self.app.config
        properties = {
            "--sft-border-radius": getattr(config, 'filter_tabs_border_radius', '8px'),
            "--sft-tab-background": getattr(config, 'filter_tabs_tab_background_color', '#f0f0f0'),
            "--sft-tab-font-size": getattr(config, 'filter_tabs_tab_font_size', '1em'),
            "--sft-tab-highlight-color": getattr(config, 'filter_tabs_tab_highlight_color', '#007bff'),
            "--sft-collapsible-accent-color": getattr(config, 'filter_tabs_collapsible_accent_color', '#17a2b8'),
        }
        
        return "; ".join([f"{key}: {value}" for key, value in properties.items()])
    
    def _generate_dynamic_css(self) -> None:
        """Generate CSS rules for showing/hiding panels based on radio button state."""
        css_rules = []
        
        for i, tab in enumerate(self.tab_data):
            radio_id = f"{self.group_id}-radio-{i}"
            panel_selector = f'.sft-panel[data-tab="{tab["name"].lower().replace(" ", "-")}"]'
            
            css_rules.append(
                f'.sft-radio-group:has(#{radio_id}:checked) ~ .sft-content > {panel_selector} {{ display: block; }}'
            )
        
        # Write dynamic CSS to file
        css_content = '\n'.join(css_rules)
        static_dir = Path(self.app.outdir) / '_static'
        static_dir.mkdir(parents=True, exist_ok=True)
        css_filename = f"dynamic-filter-tabs-{self.group_id}.css"
        (static_dir / css_filename).write_text(css_content, encoding='utf-8')
        self.app.add_css_file(css_filename)


# Custom nodes
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
