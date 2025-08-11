from __future__ import annotations

import re
import uuid
import copy
import shutil
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.writers.html import HTML5Translator

from typing import TYPE_CHECKING, Any, Dict, List

from . import __version__

if TYPE_CHECKING:
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

# --- Custom Nodes ---
# We define custom docutils nodes for semantic clarity and to have dedicated
# visitor functions, giving us full control over the final HTML rendering.
class FieldsetNode(nodes.General, nodes.Element): pass
class LegendNode(nodes.General, nodes.Element): pass
class RadioInputNode(nodes.General, nodes.Element): pass
class LabelNode(nodes.General, nodes.Element): pass
class PanelNode(nodes.General, nodes.Element): pass
class DetailsNode(nodes.General, nodes.Element): pass
class SummaryNode(nodes.General, nodes.Element): pass

# --- Renderer Class ---
class FilterTabsRenderer:
    """
    Handles the rendering logic for the filter-tabs directive.
    This class is responsible for generating the correct docutils node structure
    for both HTML and fallback formats (like LaTeX).
    """
    def __init__(self, directive: Directive, tab_names: list[str], default_tab: str, temp_blocks: list[nodes.Node]):
        self.directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.tab_names = tab_names
        self.default_tab = default_tab
        self.temp_blocks = temp_blocks

    def render_html(self) -> list[nodes.Node]:
        """
        Renders the tab set for HTML output. This method uses a modern, robust
        architecture that combines CSS Custom Properties for theming and a scoped,
        inline <style> block for the dynamic filtering logic.
        """
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        group_id = f"filter-group-{self.env.filter_tabs_counter}"

        config = self.env.app.config
        
        # 1. THEME: Pass config values to the CSS via inline CSS Custom Properties.
        # This decouples the Python logic from the CSS styling.
        style_vars = {
            "--sft-border-radius": str(config.filter_tabs_border_radius),
            "--sft-tab-background": str(config.filter_tabs_tab_background_color),
            "--sft-tab-font-size": str(config.filter_tabs_tab_font_size),
            "--sft-tab-highlight-color": str(config.filter_tabs_tab_highlight_color),
            "--sft-collapsible-accent-color": str(config.filter_tabs_collapsible_accent_color),
        }
        style_string = "; ".join([f"{key}: {value}" for key, value in style_vars.items()])

        container = nodes.container(classes=['sft-container'], style=style_string)
        if config.filter_tabs_debug_mode: container += nodes.comment(f" ID: {group_id} ", f" ID: {group_id} ")

        fieldset = FieldsetNode()
        legend = LegendNode(); legend += nodes.Text(f"Filter by: {', '.join(self.tab_names)}"); fieldset += legend

        # 2. FILTERING LOGIC: Generate a scoped <style> block.
        # This creates the specific CSS rules needed for this tab set to function,
        # linking each radio button to its corresponding panel. This is more robust
        # than a global stylesheet and avoids complex build events.
        css_rules = []
        for tab_name in self.tab_names:
            radio_id = f"{group_id}-{self._css_escape(tab_name)}"
            # Rule to show the correct panel using the powerful :has() selector.
            css_rules.append(
                f".sft-tab-bar:has(#{radio_id}:checked) ~ .sft-content > .sft-panel[data-filter='{tab_name}'] {{ display: block; }}"
            )
        style_node = nodes.raw(text=f"<style>{''.join(css_rules)}</style>", format="html")
        
        # 3. HTML STRUCTURE: Place radio buttons inside the tab bar for simpler CSS selectors.
        tab_bar = nodes.container(classes=['sft-tab-bar'], role='tablist')
        for tab_name in self.tab_names:
            radio_id = f"{group_id}-{self._css_escape(tab_name)}"
            
            radio = RadioInputNode(type='radio', name=group_id, ids=[radio_id])
            if tab_name == self.default_tab: radio['checked'] = 'checked'
            tab_bar += radio
            
            label = LabelNode(for_id=radio_id, role='tab'); label += nodes.Text(tab_name)
            tab_bar += label
        fieldset += tab_bar

        content_area = nodes.container(classes=['sft-content'])
        
        # 4. CONTENT POPULATION: Use a dictionary for direct lookup.
        # This is efficient and avoids docutils node mutation issues.
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}

        all_tab_names = self.tab_names + ["General"]
        for tab_name in all_tab_names:
            panel = PanelNode(classes=['sft-panel'], **{'data-filter': tab_name, 'role': 'tabpanel'})
            if tab_name in content_map:
                # Use deepcopy to ensure nodes can be safely reused if ever needed.
                panel.extend(copy.deepcopy(content_map[tab_name]))
            content_area += panel
        
        fieldset += content_area
        container.children = [fieldset]
        
        # Return the style block first, then the visible content.
        return [style_node, container]

    def render_fallback(self) -> list[nodes.Node]:
        """
        Renders the content as simple admonitions for non-HTML builders (e.g., LaTeX).
        This ensures the content is still accessible in PDF outputs.
        """
        output_nodes: list[nodes.Node] = []
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}

        if "General" in content_map:
            output_nodes.extend(copy.deepcopy(content_map["General"]))

        for tab_name in self.tab_names:
            if tab_name in content_map:
                admonition = nodes.admonition()
                admonition += nodes.title(text=tab_name)
                admonition.extend(copy.deepcopy(content_map[tab_name]))
                output_nodes.append(admonition)
        return output_nodes

    @staticmethod
    def _css_escape(name: str) -> str:
        """
        Creates a stable, collision-free CSS identifier from a tab name
        using a UUID namespace.
        """
        namespace = uuid.UUID('d1b1b3e8-5e7c-48d6-a235-9a4c14c9b139')
        return str(uuid.uuid5(namespace, name.strip().lower()))

# ... (Directives, Event Handlers, and other functions remain the same) ...
class TabDirective(Directive):
    has_content = True; required_arguments = 1; final_argument_whitespace = True
    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        if not hasattr(env, 'sft_context') or not env.sft_context: raise self.error("`tab` can only be used inside a `filter-tabs` directive.")
        container = nodes.container(classes=['sft-temp-panel']); container['filter-name'] = self.arguments[0].strip()
        self.state.nested_parse(self.content, self.content_offset, container)
        return [container]

class FilterTabsDirective(Directive):
    has_content = True; required_arguments = 1; final_argument_whitespace = True
    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        if hasattr(env, 'sft_context') and env.sft_context: raise self.error("Nesting `filter-tabs` is not supported.")
        if not hasattr(env, 'sft_context'): env.sft_context = []
        env.sft_context.append(True)
        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)
        env.sft_context.pop()
        temp_blocks = temp_container.findall(lambda n: isinstance(n, nodes.Element) and 'sft-temp-panel' in n.get('classes', []))
        if not temp_blocks: return []
        tabs_raw = [t.strip() for t in self.arguments[0].split(',')]
        tab_names_only = [re.sub(r'\s*\(\s*default\s*\)$', '', t, re.IGNORECASE).strip() for t in tabs_raw]
        if len(set(tab_names_only)) != len(tab_names_only): raise self.error(f"Duplicate tab names found: {tab_names_only}")
        default_tab, tab_names = "", []
        for tab in tabs_raw:
            match = re.match(r"^(.*?)\s*\(\s*default\s*\)$", tab, re.IGNORECASE)
            tab_name = match.group(1).strip() if match else tab
            if match and not default_tab: default_tab = tab_name
            tab_names.append(tab_name)
        if not default_tab and tab_names: default_tab = tab_names[0]
        renderer = FilterTabsRenderer(self, tab_names, default_tab, temp_blocks)
        if env.app.builder.name == 'html': return renderer.render_html()
        else: return renderer.render_fallback()

def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str):
    if not app.config.filter_tabs_collapsible_enabled or app.builder.name != 'html': return
    for node in list(doctree.findall(nodes.admonition)):
        if 'collapsible' not in node.get('classes', []): continue
        is_expanded = 'expanded' in node.get('classes', [])
        title_node = next(iter(node.findall(nodes.title)), None)
        summary_text = title_node.astext() if title_node else "Details"
        if title_node: title_node.parent.remove(title_node)
        details_node = DetailsNode(classes=['collapsible-section'])
        if is_expanded: details_node['open'] = 'open'
        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=['custom-arrow']); arrow_span += nodes.Text("►")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node
        content_node = nodes.container(classes=['collapsible-content']); content_node.extend(copy.deepcopy(node.children))
        details_node += content_node
        node.replace_self(details_node)

def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    attrs = node.attributes.copy()
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'): attrs.pop(key, None)
    return attrs

def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None: self.body.append(self.starttag(node, 'fieldset', CLASS='sft-fieldset'))
def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None: self.body.append('</fieldset>')
def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None: self.body.append(self.starttag(node, 'legend', CLASS='sft-legend'))
def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None: self.body.append('</legend>')
def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None: self.body.append(self.starttag(node, 'input', **_get_html_attrs(node)))
def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None: pass
def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node); attrs['for'] = node['for_id']
    self.body.append(self.starttag(node, 'label', **attrs))
def depart_label_node(self: HTML5Translator, node: LabelNode) -> None: self.body.append('</label>')
def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None: self.body.append(self.starttag(node, 'div', CLASS='sft-panel', **_get_html_attrs(node)))
def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None: self.body.append('</div>')
def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None: self.body.append(self.starttag(node, 'details', **_get_html_attrs(node)))
def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None: self.body.append('</details>')
def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None: self.body.append(self.starttag(node, 'summary', **_get_html_attrs(node)))
def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None: self.body.append('</summary>')

def copy_static_files(app: Sphinx):
    if app.builder.name != 'html': return
    source_css = Path(__file__).parent / "static" / "filter_tabs.css"
    dest_dir = Path(app.outdir) / "_static"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_css, dest_dir)

def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_config_value('filter_tabs_tab_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_tab_background_color', '#f0f0f0', 'html', [str])
    app.add_config_value('filter_tabs_tab_font_size', '1em', 'html', [str])
    app.add_config_value('filter_tabs_border_radius', '8px', 'html', [str])
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_enabled', True, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_accent_color', '#17a2b8', 'html', [str])
    app.add_css_file('filter_tabs.css')
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node))
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node))
    app.add_node(RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node))
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node))
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node))
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node))
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node))
    app.add_directive('filter-tabs', FilterTabsDirective)
    app.add_directive('tab', TabDirective)
    app.connect('doctree-resolved', setup_collapsible_admonitions)
    app.connect('builder-inited', copy_static_files)
    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
