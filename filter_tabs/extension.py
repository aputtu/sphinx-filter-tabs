#
# extension.py: The core logic for the sphinx-filter-tabs Sphinx extension.
#

# --- Imports ---
from __future__ import annotations

import re
import uuid
import copy
import shutil
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.writers.html import HTML5Translator

from typing import TYPE_CHECKING, Any, Dict, List
from . import __version__

if TYPE_CHECKING:
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

# --- Constants ---
_CSS_NAMESPACE = uuid.UUID('d1b1b3e8-5e7c-48d6-a235-9a4c14c9b139')

SFT_CONTAINER = "sft-container"
SFT_FIELDSET = "sft-fieldset"
SFT_LEGEND = "sft-legend"
SFT_TAB_BAR = "sft-tab-bar"
SFT_CONTENT = "sft-content"
SFT_PANEL = "sft-panel"
SFT_TEMP_PANEL = "sft-temp-panel"
COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"

logger = logging.getLogger(__name__)

# --- Custom Nodes ---
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

class DetailsNode(nodes.General, nodes.Element): 
    pass

class SummaryNode(nodes.General, nodes.Element): 
    pass


# --- Renderer Class ---
class FilterTabsRenderer:
    """
    Handles the primary logic of converting the parsed directive content
    into a final node structure for both HTML and fallback formats (like LaTeX).
    """
    def __init__(self, directive: Directive, tab_names: list[str], default_tab: str, temp_blocks: list[nodes.Node]):
        """Initializes the renderer with all necessary context from the directive."""
        self.directive: Directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.tab_names: list[str] = tab_names
        self.default_tab: str = default_tab
        self.temp_blocks: list[nodes.Node] = temp_blocks

    def render_html(self) -> list[nodes.Node]:
        """Constructs the complete, W3C valid, and ARIA-compliant docutils node tree."""
        # Ensure a unique ID for each filter-tabs instance on a page.
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        group_id = f"filter-group-{self.env.filter_tabs_counter}"

        config = self.env.app.config

        # Create a dictionary of CSS Custom Properties from conf.py settings.
        style_vars = {
            "--sft-border-radius": str(config.filter_tabs_border_radius),
            "--sft-tab-background": str(config.filter_tabs_tab_background_color),
            "--sft-tab-font-size": str(config.filter_tabs_tab_font_size),
            "--sft-tab-highlight-color": str(config.filter_tabs_tab_highlight_color),
            "--sft-collapsible-accent-color": str(config.filter_tabs_collapsible_accent_color),
        }
        style_string = "; ".join([f"{key}: {value}" for key, value in style_vars.items()])

        # If debug mode is on, log the generated ID and styles.
        if config.filter_tabs_debug_mode:
            logger.info(f"[sphinx-filter-tabs] ID: {group_id}, Styles: '{style_string}'")

        # Create the main container node with the inline style for theming.
        container = ContainerNode(classes=[SFT_CONTAINER], style=style_string)

        # Build the semantic structure using fieldset and a hidden legend.
        fieldset = FieldsetNode()
        legend = LegendNode()
        legend += nodes.Text(f"Filter by: {', '.join(self.tab_names)}")
        fieldset += legend
        
        # --- CSS Generation ---
        css_rules = []
        for i, tab_name in enumerate(self.tab_names):
            # FIX 1: Use position-based IDs instead of hash-based
            radio_id = f"{group_id}-tab-{i}"
            panel_id = f"{radio_id}-panel"
            css_rules.append(
                f".{SFT_TAB_BAR}:has(#{radio_id}:checked) ~ .sft-content > #{panel_id} {{ display: block; }}"
            )
        
        # Write the dynamic CSS to a temporary file and add it to the build.
        css_content = ''.join(css_rules)
        static_dir = Path(self.env.app.outdir) / '_static'
        static_dir.mkdir(parents=True, exist_ok=True)
        css_filename = f"dynamic-filter-tabs-{group_id}.css"
        (static_dir / css_filename).write_text(css_content, encoding='utf-8')
        self.env.app.add_css_file(css_filename)

        # The tab bar container - NO ARIA attributes here
        tab_bar = ContainerNode(classes=[SFT_TAB_BAR])
        fieldset += tab_bar

        # The content area holds all the panels
        content_area = ContainerNode(classes=[SFT_CONTENT])
        fieldset += content_area

        # Map tab names to their content blocks for easy lookup.
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}
        
        # 1. Create all radio buttons and labels - NO ARIA on labels
        for i, tab_name in enumerate(self.tab_names):
            # FIX 1: Use position-based IDs
            radio_id = f"{group_id}-tab-{i}"
            panel_id = f"{radio_id}-panel"
            
            # The radio button is for state management.
            radio = RadioInputNode(type='radio', name=group_id, ids=[radio_id])
            
            is_default = (self.default_tab == tab_name) or (i == 0 and not self.default_tab)
            if is_default:
                radio['checked'] = 'checked'
            tab_bar += radio

            # FIX 2: Remove ALL ARIA attributes from labels - just use for_id
            # FIX 3: Don't add IDs to labels - they don't need them
            label = LabelNode(for_id=radio_id)
            label += nodes.Text(tab_name)
            tab_bar += label

        # 2. Create all tab panels - panels can have ARIA attributes
        all_tab_names = ["General"] + self.tab_names
        for i, tab_name in enumerate(all_tab_names):
            if tab_name == "General":
                # General panel doesn't correspond to a specific tab control
                panel = PanelNode(
                    classes=[SFT_PANEL], 
                    **{'data-filter': tab_name}
                )
            else:
                # FIX 1: Use position-based IDs for panels too
                tab_index = self.tab_names.index(tab_name)
                radio_id = f"{group_id}-tab-{tab_index}"
                panel_id = f"{radio_id}-panel"
                
                # Panels can have ARIA attributes for screen readers
                panel_attrs = {
                    'classes': [SFT_PANEL],
                    'ids': [panel_id],
                    'role': 'tabpanel',
                    'aria-labelledby': radio_id,
                    'tabindex': '0'
                }
                panel = PanelNode(**panel_attrs)

            if tab_name in content_map:
                panel.extend(copy.deepcopy(content_map[tab_name]))
            content_area += panel

        container.children = [fieldset]
        return [container]

    def render_fallback(self) -> list[nodes.Node]:
        """Renders content as a series of simple admonitions for non-HTML builders (e.g., LaTeX/PDF)."""
        output_nodes: list[nodes.Node] = []
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}
        # "General" content is rendered first, without a title.
        if "General" in content_map:
            output_nodes.extend(copy.deepcopy(content_map["General"]))
        # Each specific tab's content is placed inside a titled admonition block.
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
        Generates a deterministic, CSS-safe identifier from any given tab name string.
        """
        return str(uuid.uuid5(_CSS_NAMESPACE, name.strip().lower()))


class TabDirective(Directive):
    """Handles the `.. tab::` directive, capturing its content."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """
        Parses the content of a tab and stores it in a temporary container.
        """
        env = self.state.document.settings.env
        # Ensure `tab` is only used inside `filter-tabs`.
        if not hasattr(env, 'sft_context') or not env.sft_context:
            raise self.error("`tab` can only be used inside a `filter-tabs` directive.")
        # Store the tab name and parsed content in a temporary node.
        container = nodes.container(classes=[SFT_TEMP_PANEL])
        container['filter-name'] = self.arguments[0].strip()
        self.state.nested_parse(self.content, self.content_offset, container)
        return [container]


class FilterTabsDirective(Directive):
    """Handles the main `.. filter-tabs::` directive."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """
        Parses the list of tabs, manages the parsing context for its content,
        and delegates the final rendering to the FilterTabsRenderer.
        """
        env = self.state.document.settings.env
        
        # Set a context flag to indicate that we are inside a filter-tabs block.
        if not hasattr(env, 'sft_context'):
            env.sft_context = []
        env.sft_context.append(True)

        # Parse the content of the directive to find all `.. tab::` blocks.
        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)
        env.sft_context.pop()

        # Find all the temporary panel nodes created by the TabDirective.
        temp_blocks = temp_container.findall(lambda n: isinstance(n, nodes.Element) and SFT_TEMP_PANEL in n.get('classes', []))
        if not temp_blocks:
            self.error("No `.. tab::` directives found inside `filter-tabs`. Content will not be rendered.")
            return []

        # Parse the tab names from the directive's arguments.
        tabs_raw = [t.strip() for t in self.arguments[0].split(',')]
        tab_names_only = [re.sub(r'\s*\(\s*default\s*\)$', '', t, re.IGNORECASE).strip() for t in tabs_raw]

        if len(set(tab_names_only)) != len(tab_names_only):
            raise self.error(f"Duplicate tab names found: {tab_names_only}")

        # Identify the default tab.
        default_tab, tab_names = "", []
        for tab in tabs_raw:
            match = re.match(r"^(.*?)\s*\(\s*default\s*\)$", tab, re.IGNORECASE)
            tab_name = match.group(1).strip() if match else tab
            if match and not default_tab:
                default_tab = tab_name
            tab_names.append(tab_name)

        # If no default is specified, the first tab becomes the default.
        if not default_tab and tab_names:
            default_tab = tab_names[0]

        # Instantiate the renderer and call the appropriate render method based on the builder.
        renderer = FilterTabsRenderer(self, tab_names, default_tab, temp_blocks)
        if env.app.builder.name == 'html':
            return renderer.render_html()
        else:
            return renderer.render_fallback()


def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str):
    """
    Finds any admonition with the `:class: collapsible` option and transforms it
    into an HTML `<details>`/`<summary>` element for a native collapsible effect.
    """
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

        # Create the new <details> node.
        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node['open'] = 'open'

        # Create the new <summary> node with a custom arrow.
        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node

        # Move the original content of the admonition into a new container.
        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        content_node.extend(copy.deepcopy(node.children))
        details_node += content_node
        # Replace the original admonition node with the new details node.
        node.replace_self(details_node)

def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    """Helper to get a clean dictionary of HTML attributes from a docutils node."""
    attrs = node.attributes.copy()
    # Remove docutils-internal attributes to avoid rendering them in the HTML.
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'):
        attrs.pop(key, None)
    return attrs

# --- HTML Visitor Functions ---
def visit_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append(self.starttag(node, 'div', **_get_html_attrs(node)))
def depart_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append('</div>')

def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append(self.starttag(node, 'fieldset', CLASS=SFT_FIELDSET))
def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append('</fieldset>')

def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append(self.starttag(node, 'legend', CLASS=SFT_LEGEND))
def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append('</legend>')

def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    attrs = _get_html_attrs(node)
    # Don't manually add 'id' - starttag handles 'ids' automatically
    # Include other important attributes
    for key in ['type', 'name', 'checked']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'input', **attrs))

def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    pass

def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    # Ensure the 'for' attribute is set correctly
    if 'for_id' in node.attributes:
        attrs['for'] = node['for_id']
    # FIX: Don't add any ARIA attributes or IDs to labels
    self.body.append(self.starttag(node, 'label', **attrs))

def depart_label_node(self: HTML5Translator, node: LabelNode) -> None:
    self.body.append('</label>')

def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    attrs = _get_html_attrs(node)
    # Panels can have ARIA attributes
    for key in ['role', 'aria-labelledby', 'tabindex']:
        if key in node.attributes:
            attrs[key] = node[key]
    # Handle data attributes
    if 'data-filter' in node.attributes:
        attrs['data-filter'] = node['data-filter']
    self.body.append(self.starttag(node, 'div', CLASS=SFT_PANEL, **attrs))

def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append('</div>')

def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    attrs = {}
    if 'open' in node.attributes:
        attrs['open'] = node['open']
    self.body.append(self.starttag(node, 'details', **attrs))

def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append('</details>')

def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, 'summary'))

def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append('</summary>')


def copy_static_files(app: Sphinx):
    """
    Copies the extension's static CSS and JS files to the build output directory.
    """
    if app.builder.name != 'html':
        return
    
    static_source_dir = Path(__file__).parent / "static"
    dest_dir = Path(app.outdir) / "_static"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy both CSS and JS files
    for file_pattern in ["*.css", "*.js"]:
        for file_path in static_source_dir.glob(file_pattern):
            shutil.copy(file_path, dest_dir)


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    The main entry point for the Sphinx extension.
    """
    # Register custom configuration values
    app.add_config_value('filter_tabs_tab_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_tab_background_color', '#f0f0f0', 'html', [str])
    app.add_config_value('filter_tabs_tab_font_size', '1em', 'html', [str])
    app.add_config_value('filter_tabs_border_radius', '8px', 'html', [str])
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_enabled', True, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_accent_color', '#17a2b8', 'html', [str])
    
    # NEW: Add accessibility configuration options
    app.add_config_value('filter_tabs_keyboard_navigation', True, 'html', [bool])
    app.add_config_value('filter_tabs_announce_changes', True, 'html', [bool])

    # Add the main stylesheet and JavaScript to the HTML output.
    app.add_css_file('filter_tabs.css')
    app.add_js_file('filter_tabs.js')

    # Register all custom nodes and their HTML visitor/depart functions.
    app.add_node(ContainerNode, html=(visit_container_node, depart_container_node))
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node))
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node))
    app.add_node(RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node))
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node))
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node))
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node))
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node))

    # Register the RST directives.
    app.add_directive('filter-tabs', FilterTabsDirective)
    app.add_directive('tab', TabDirective)

    # Connect to Sphinx events
    app.connect('doctree-resolved', setup_collapsible_admonitions)
    app.connect('builder-inited', copy_static_files)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
