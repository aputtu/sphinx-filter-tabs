# filter_tabs/extension.py

from __future__ import annotations
from .renderer import FilterTabsRenderer
import re
import copy
import shutil
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.writers.html import HTML5Translator

from typing import TYPE_CHECKING, Any, Dict, List
from . import __version__

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

# --- Constants ---
COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"

logger = logging.getLogger(__name__)

# --- Custom Nodes ---
class ContainerNode(nodes.General, nodes.Element): pass
class FieldsetNode(nodes.General, nodes.Element): pass
class LegendNode(nodes.General, nodes.Element): pass
class RadioInputNode(nodes.General, nodes.Element): pass
class LabelNode(nodes.General, nodes.Element): pass
class PanelNode(nodes.General, nodes.Element): pass
class DetailsNode(nodes.General, nodes.Element): pass
class SummaryNode(nodes.General, nodes.Element): pass


class TabDirective(Directive):
    """Handles the `.. tab::` directive, capturing its content and options."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {'aria-label': directives.unchanged}

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        if not hasattr(env, 'sft_context') or not env.sft_context:
            raise self.error("`tab` can only be used inside a `filter-tabs` directive.")
        
        # Get ONLY the first argument line, not the content
        tab_arg = self.arguments[0].strip()
        
        # Split by newlines and take only the first line (the actual argument)
        tab_lines = tab_arg.split('\n')
        first_line = tab_lines[0].strip()
        
        is_default = False
        tab_name = first_line
        
        # Parse (default) correctly from the first line only
        match = re.match(r"^(.*?)\s*\(\s*default\s*\)$", first_line, re.IGNORECASE)
        if match:
            tab_name = match.group(1).strip()  # Remove (default) from name
            is_default = True
        
        container = nodes.container(classes=["sft-temp-panel"])
        container['filter_name'] = tab_name  # Should be clean name only
        container['is_default'] = is_default
        container['aria_label'] = self.options.get('aria-label', None)
        
        # Parse the content separately
        self.state.nested_parse(self.content, self.content_offset, container)
        
        return [container]


class FilterTabsDirective(Directive):
    """Handles the main `.. filter-tabs::` directive."""
    has_content = True
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        
        if not hasattr(env, 'sft_context'):
            env.sft_context = []
        env.sft_context.append(True)

        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)
        
        env.sft_context.pop()

        general_content = []
        tab_data = []
        
        for node in temp_container.children:
            if isinstance(node, nodes.Element) and "sft-temp-panel" in node.get('classes', []):
                # Get the stored attributes from TabDirective
                filter_name = node.get('filter_name', 'Unknown')
                is_default = node.get('is_default', False)
                aria_label = node.get('aria_label', None)
                
                tab_data.append({
                    'name': filter_name,
                    'is_default': is_default,
                    'aria_label': aria_label,
                    'content': list(node.children)
                })
            else:
                general_content.append(node)
        
        if not tab_data:
            raise self.error("No `.. tab::` directives found inside `filter-tabs`.")
        
        # Only set first tab as default if NO tab has is_default=True
        default_tabs = [i for i, tab in enumerate(tab_data) if tab['is_default']]
        
        if not default_tabs:
            tab_data[0]['is_default'] = True
        
        renderer = FilterTabsRenderer(self, tab_data, general_content)
        return renderer.render_html() if env.app.builder.name == 'html' else renderer.render_fallback()

def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str):
    """Convert admonitions with 'collapsible' class to details/summary elements."""
    if not app.config.filter_tabs_collapsible_enabled or app.builder.name != 'html':
        return
        
    for node in list(doctree.findall(nodes.admonition)):
        if 'collapsible' not in node.get('classes', []):
            continue
            
        is_expanded = 'expanded' in node.get('classes', [])
        title_node = next(iter(node.findall(nodes.title)), None)
        summary_text = title_node.astext() if title_node else "Details"
        
        if title_node:
            title_node.parent.remove(title_node)

        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node['open'] = 'open'
        
        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node
        
        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        content_node.extend(copy.deepcopy(node.children))
        details_node += content_node
        
        node.replace_self(details_node)


def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    """Extract HTML attributes from a docutils node, excluding internal attributes."""
    attrs = node.attributes.copy()
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'):
        attrs.pop(key, None)
    return attrs


# --- HTML Visitor Functions ---
def visit_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append(self.starttag(node, 'div', **_get_html_attrs(node)))

def depart_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append('</div>')

def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    attrs = _get_html_attrs(node)
    if 'role' in node.attributes:
        attrs['role'] = node['role']
    self.body.append(self.starttag(node, 'fieldset', CLASS="sft-fieldset", **attrs))

def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append('</fieldset>')

def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append(self.starttag(node, 'legend', CLASS="sft-legend"))

def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append('</legend>')

def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ['type', 'name', 'checked', 'aria-label', 'aria-describedby']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'input', **attrs))

def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    pass  # Self-closing tag

def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    if 'for_id' in node.attributes:
        attrs['for'] = node['for_id']
    self.body.append(self.starttag(node, 'label', **attrs))

def depart_label_node(self: HTML5Translator, node: LabelNode) -> None:
    self.body.append('</label>')

def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ['role', 'aria-labelledby', 'tabindex', 'data-filter', 'data-tab']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'div', CLASS="sft-panel", **attrs))

def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append('</div>')

def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    attrs = _get_html_attrs(node)
    if 'open' in node.attributes:
        attrs['open'] = 'open'
    self.body.append(self.starttag(node, 'details', **attrs))

def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append('</details>')

def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, 'summary', **_get_html_attrs(node)))

def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append('</summary>')


def copy_static_files(app: Sphinx):
    """Copy CSS and JS files to the build directory."""
    if app.builder.name != 'html':
        return
        
    static_source_dir = Path(__file__).parent / "static"
    dest_dir = Path(app.outdir) / "_static"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in static_source_dir.glob("*.css"):
        shutil.copy(file_path, dest_dir)
    for file_path in static_source_dir.glob("*.js"):
        shutil.copy(file_path, dest_dir)


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Sphinx extension."""
    # Basic theming configuration
    app.add_config_value('filter_tabs_tab_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_tab_background_color', '#f0f0f0', 'html', [str])
    app.add_config_value('filter_tabs_tab_font_size', '1em', 'html', [str])
    app.add_config_value('filter_tabs_border_radius', '8px', 'html', [str])
    
    # Feature configuration
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_enabled', True, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_accent_color', '#17a2b8', 'html', [str])
    
    # Accessibility configuration
    app.add_config_value('filter_tabs_keyboard_navigation', True, 'html', [bool])
    app.add_config_value('filter_tabs_announce_changes', True, 'html', [bool])
    
    # Add CSS and JS files
    app.add_css_file('filter_tabs.css')
    app.add_js_file('filter_tabs.js')
    
    # Register custom nodes
    app.add_node(ContainerNode, html=(visit_container_node, depart_container_node))
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node))
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node))
    app.add_node(RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node))
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node))
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node))
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node))
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node))
    
    # Register directives
    app.add_directive('filter-tabs', FilterTabsDirective)
    app.add_directive('tab', TabDirective)
    
    # Connect event handlers
    app.connect('builder-inited', copy_static_files)
    app.connect('doctree-resolved', setup_collapsible_admonitions)
    
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
