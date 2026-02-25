# filter_tabs/extension.py
"""
Core extension module for sphinx-filter-tabs.
Consolidated version containing directives, data models, nodes, and Sphinx integration.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging
from sphinx.writers.html import HTML5Translator

from . import __version__

__all__ = ["setup"]

# Type alias for the generic visitor/depart functions used as safety-net skips.
# Normal HTML visitors are typed with their specific node class; only the
# builder-agnostic skip helpers need the broad Any signature.
NodeVisitorFunc = Any  # Callable[[Any, nodes.Element], None]

# =============================================================================
# Custom Docutils Nodes
# =============================================================================


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


class FilterTabsNode(nodes.General, nodes.Element):
    """Neutral container emitted by the directive at parse time.

    Children are a mix of ``FilterTabSlotNode`` (one per ``.. tab::``) and
    any general content nodes that appeared before the tabs.  All child nodes
    live in the real document tree so every Sphinx transform — including
    ``OnlyNodeTransform`` — operates on them normally.

    The ``custom_legend`` option is stored as a plain string attribute.

    ``process_filter_tabs_nodes`` (connected to ``doctree-resolved``) walks
    the tree at *write* time, reads the children, and replaces this node with
    builder-appropriate output.  Because ``doctree-resolved`` fires after
    doctree unpickling, the correct builder is always used, making shared
    ``.doctrees`` directories safe.
    """

    pass


class FilterTabSlotNode(nodes.General, nodes.Element):
    """Marks one tab's content inside a ``FilterTabsNode``.

    Attributes stored on the node:
    - ``tab_name``   – display name of the tab
    - ``is_default`` – whether this tab is initially selected
    - ``aria_label`` – optional ARIA label override

    Children are the tab's body content, fully part of the live tree.
    """

    pass


# =============================================================================
# Data Models and Configuration
# =============================================================================


@dataclass
class FilterTabsConfig:
    """Simplified configuration settings for filter-tabs rendering."""

    highlight_color: str = "#007bff"
    debug_mode: bool = False

    @classmethod
    def from_sphinx_config(cls, app_config: Config) -> FilterTabsConfig:
        return cls(
            highlight_color=getattr(app_config, "filter_tabs_highlight_color", cls.highlight_color),
            debug_mode=getattr(app_config, "filter_tabs_debug_mode", cls.debug_mode),
        )


@dataclass
class IDGenerator:
    """Centralized ID generation for consistent element identification."""

    group_id: str

    def radio_id(self, index: int) -> str:
        return f"{self.group_id}-radio-{index}"

    def panel_id(self, index: int) -> str:
        return f"{self.group_id}-panel-{index}"

    def desc_id(self, index: int) -> str:
        return f"{self.group_id}-desc-{index}"

    def legend_id(self) -> str:
        return f"{self.group_id}-legend"

    def label_id(self, index: int) -> str:
        return f"{self.group_id}-label-{index}"


# =============================================================================
# Directive Classes
# =============================================================================

COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"

logger = logging.getLogger(__name__)


class TabDirective(Directive):
    """Handles the ``.. tab::`` directive, capturing its content and options."""

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {"aria-label": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env

        if not hasattr(env, "sft_context") or not env.sft_context:
            raise self.error("`tab` can only be used inside a `filter-tabs` directive.")

        try:
            tab_name, is_default = self._parse_tab_argument(self.arguments[0])
        except ValueError as e:
            raise self.error(f"Invalid tab argument: {e}") from e

        slot = FilterTabSlotNode()
        slot["tab_name"] = tab_name
        slot["is_default"] = is_default
        slot["aria_label"] = self.options.get("aria-label", None)

        self.state.nested_parse(self.content, self.content_offset, slot)

        return [slot]

    def _parse_tab_argument(self, argument: str) -> tuple[str, bool]:
        if not argument:
            raise ValueError("Tab argument cannot be empty")

        first_line = argument.strip().split("\n")[0].strip()
        match = re.match(r"^(.*?)\s*\(\s*default\s*\)$", first_line, re.IGNORECASE)
        if match:
            tab_name = match.group(1).strip()
            if not tab_name:
                raise ValueError("Tab name cannot be empty")
            return tab_name, True

        return first_line, False


class FilterTabsDirective(Directive):
    """Handles the main ``.. filter-tabs::`` directive.

    Emits a single ``FilterTabsNode`` whose children are the parsed
    ``FilterTabSlotNode`` instances (one per ``.. tab::``) plus any general
    content that appeared before the tabs.  All content is part of the live
    document tree so Sphinx transforms (e.g. ``OnlyNodeTransform``) process it
    before ``process_filter_tabs_nodes`` runs at write time.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {"legend": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env

        if not hasattr(env, "sft_context"):
            env.sft_context = []
        env.sft_context.append(True)

        # Parse content into a temporary container; TabDirective will produce
        # FilterTabSlotNode instances and everything else is general content.
        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)

        env.sft_context.pop()

        slots = [c for c in temp_container.children if isinstance(c, FilterTabSlotNode)]
        general_content = [
            c for c in temp_container.children if not isinstance(c, FilterTabSlotNode)
        ]

        if not slots:
            msg = (
                "No `.. tab::` directives found inside `.. filter-tabs::`.\n"
                "You must include at least one tab."
            )
            if general_content:
                msg += " Some content was found, but it was not part of a `.. tab::` block."
            raise self.error(msg)

        self._validate_slots(slots)

        if not any(s["is_default"] for s in slots):
            slots[0]["is_default"] = True

        ft_node = FilterTabsNode()
        ft_node["custom_legend"] = self.options.get("legend")

        # Add general content first, then tab slots — all as real children.
        for child in general_content:
            ft_node += child
        for slot in slots:
            ft_node += slot

        return [ft_node]

    def _validate_slots(self, slots: list[FilterTabSlotNode]) -> None:
        names: list[str] = []
        for slot in slots:
            name = slot["tab_name"]
            if name in names:
                raise self.error(f"Duplicate tab name '{name}'. Each tab must have a unique name.")
            names.append(name)
            if not slot.children:
                logger.warning(f"Tab '{name}' has no content.")

        defaults = [s for s in slots if s["is_default"]]
        if len(defaults) > 1:
            default_names = [s["tab_name"] for s in defaults]
            logger.warning(
                f"Multiple tabs marked as default: {', '.join(default_names)}. "
                f"Using first default: '{default_names[0]}'"
            )


# =============================================================================
# doctree-resolved handler: resolves FilterTabsNode to builder-specific output
# =============================================================================


def process_filter_tabs_nodes(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace each FilterTabsNode with builder-appropriate output.

    Connected to the ``doctree-resolved`` event, which fires at *write* time
    for each document — after the doctree has been unpickled from the cache
    and before it is passed to the builder's writer.  This means:

    - The node type stored in ``.doctrees`` is always the neutral
      ``FilterTabsNode`` / ``FilterTabSlotNode`` pair.  No builder-specific
      structure is ever pickled.
    - When LaTeX and HTML builders share a ``.doctrees`` directory (the
      default Sphinx layout), each builder independently resolves
      ``FilterTabsNode`` to the correct output for *its* format.
    - Because the tab content lives as real children of ``FilterTabsNode``,
      all Sphinx transforms (including ``OnlyNodeTransform``) have already
      processed ``.. only::`` directives inside tabs before this handler runs.

    This is structurally equivalent to how ``sphinx.ext.todo`` and
    ``sphinx.ext.ifconfig`` perform their builder-dispatch.
    """
    config = FilterTabsConfig.from_sphinx_config(app.config)
    is_html = app.builder.format == "html"

    # Per-document counter stored on the doctree node itself so parallel
    # writes don't share state.
    doc_counter_key = "_filter_tabs_counter"

    for ft_node in reversed(list(doctree.findall(FilterTabsNode))):
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
            replacement = _render_html(
                slots,
                general_content,
                custom_legend,
                id_gen,
                config,
                app.env,
            )
        else:
            replacement = _render_fallback(slots, general_content)

        ft_node.replace_self(replacement)


# =============================================================================
# Rendering functions
# =============================================================================


def _render_html(
    slots: list[FilterTabSlotNode],
    general_content: list[nodes.Node],
    custom_legend: str | None,
    id_gen: IDGenerator,
    config: FilterTabsConfig,
    env: Any,
) -> list[nodes.Node]:
    """Produce sft-container/fieldset/panel HTML nodes."""
    container = ContainerNode(
        classes=["sft-container"],
        role="region",
        **{"aria-labelledby": id_gen.legend_id()},
    )

    fieldset = FieldsetNode(role="radiogroup")

    # Legend
    if custom_legend:
        legend_text = custom_legend
    else:
        tab_names = [s["tab_name"] for s in slots]
        content_type = _infer_content_type(tab_names)
        legend_text = f"Choose {content_type}: {', '.join(tab_names)}"
    legend = LegendNode(classes=["sft-legend"], ids=[id_gen.legend_id()])
    legend += nodes.Text(legend_text)
    fieldset += legend

    n = len(slots)
    current_max = getattr(env, "filter_tabs_max_tab_count", 0)
    env.filter_tabs_max_tab_count = max(current_max, n)

    default_index = next((i for i, s in enumerate(slots) if s["is_default"]), 0)

    radio_group = ContainerNode(classes=["sft-radio-group"])

    for i, slot in enumerate(slots):
        tab_name = slot["tab_name"]
        radio = RadioInputNode(
            classes=["sr-only"],
            type="radio",
            name=id_gen.group_id,
            ids=[id_gen.radio_id(i)],
            **{
                "aria-describedby": id_gen.desc_id(i),
                "data-tab-index": str(i),
            },
        )
        if slot.get("aria_label"):
            radio["aria-label"] = slot["aria_label"]
        if i == default_index:
            radio["checked"] = "checked"
        radio_group += radio

        label = LabelNode(for_id=id_gen.radio_id(i))
        label += nodes.Text(tab_name)
        radio_group += label

        desc = ContainerNode(classes=["sr-only"], ids=[id_gen.desc_id(i)])
        desc += nodes.Text(f"Show content for {tab_name}")
        radio_group += desc

    content_area = ContainerNode(classes=["sft-content"])

    if general_content:
        general_panel = PanelNode(
            classes=["sft-panel"],
            **{"data-filter": "General", "aria-label": "General information", "role": "region"},
        )
        general_panel.extend(c.deepcopy() for c in general_content)
        content_area += general_panel

    for i, slot in enumerate(slots):
        tab_name = slot["tab_name"]
        panel = PanelNode(
            classes=["sft-panel"],
            ids=[id_gen.panel_id(i)],
            role="tabpanel",
            **{
                "aria-labelledby": id_gen.radio_id(i),
                "tabindex": "0",
                "data-tab": tab_name.lower().replace(" ", "-"),
                "data-tab-index": str(i),
            },
        )
        panel.extend(c.deepcopy() for c in slot.children)
        content_area += panel

    radio_group += content_area
    fieldset += radio_group
    container += fieldset
    return [container]


def _render_fallback(
    slots: list[FilterTabSlotNode],
    general_content: list[nodes.Node],
) -> list[nodes.Node]:
    """Produce plain admonition nodes for LaTeX and other non-HTML builders."""
    output: list[nodes.Node] = []
    if general_content:
        output.extend(c.deepcopy() for c in general_content)
    for slot in slots:
        admonition = nodes.admonition()
        admonition += nodes.title(text=slot["tab_name"])
        admonition.extend(c.deepcopy() for c in slot.children)
        output.append(admonition)
    return output


def _infer_content_type(tab_names: list[str]) -> str:
    """Infer a meaningful legend from tab names."""
    PATTERNS = [
        (
            ["python", "javascript", "java", "c++", "rust", "go", "ruby", "php"],
            "programming language",
        ),
        (["windows", "mac", "macos", "linux", "ubuntu", "debian", "fedora"], "operating system"),
        (["pip", "conda", "npm", "yarn", "cargo", "gem", "composer"], "package manager"),
        (["cli", "gui", "terminal", "command", "console", "graphical"], "interface"),
        (["development", "staging", "production", "test", "local"], "environment"),
        (["source", "binary", "docker", "manual", "automatic"], "installation method"),
    ]
    lower_names = [name.lower() for name in tab_names]
    for keywords, content_type in PATTERNS:
        if any(name in keywords for name in lower_names):
            return content_type
    for keywords, content_type in PATTERNS:
        for name in lower_names:
            if any(keyword in name for keyword in keywords):
                return content_type
    return "option"


# =============================================================================
# Collapsible Admonitions Support
# =============================================================================


def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Convert admonitions with 'collapsible' class to details/summary elements."""
    if app.builder.name != "html":
        return

    for node in list(doctree.findall(nodes.admonition)):
        if "collapsible" not in node.get("classes", []):
            continue

        is_expanded = "expanded" in node.get("classes", [])
        title_node = next(iter(node.findall(nodes.title)), None)
        summary_text = title_node.astext() if title_node else "Details"

        if title_node:
            title_node.parent.remove(title_node)

        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node["open"] = "open"

        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node

        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        content_node.extend(c.deepcopy() for c in node.children)
        details_node += content_node

        node.replace_self(details_node)


# =============================================================================
# HTML Visitor Functions
# =============================================================================


def _get_html_attrs(node: nodes.Element) -> dict[str, Any]:
    """Extract HTML attributes from a docutils node, excluding internal attributes."""
    attrs = node.attributes.copy()
    for key in ("ids", "backrefs", "dupnames", "names", "classes", "id", "for_id"):
        attrs.pop(key, None)
    return attrs


def visit_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append(self.starttag(node, "div", **_get_html_attrs(node)))


def depart_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append("</div>")


def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    attrs = _get_html_attrs(node)
    if "role" in node.attributes:
        attrs["role"] = node["role"]
    self.body.append(self.starttag(node, "fieldset", CLASS="sft-fieldset", **attrs))


def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append("</fieldset>")


def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append(self.starttag(node, "legend", CLASS="sft-legend"))


def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append("</legend>")


def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ["type", "name", "checked", "aria-label"]:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, "input", **attrs))


def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    pass  # Self-closing tag


def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    if "for_id" in node.attributes:
        attrs["for"] = node["for_id"]
    self.body.append(self.starttag(node, "label", **attrs))


def depart_label_node(self: HTML5Translator, node: LabelNode) -> None:
    self.body.append("</label>")


def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ["role", "aria-labelledby", "tabindex"]:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, "div", CLASS="sft-panel", **attrs))


def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append("</div>")


def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    attrs = _get_html_attrs(node)
    if "open" in node.attributes:
        attrs["open"] = "open"
    self.body.append(self.starttag(node, "details", **attrs))


def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append("</details>")


def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, "summary", **_get_html_attrs(node)))


def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append("</summary>")


def _visit_skip_node(self: NodeVisitorFunc, node: nodes.Element) -> None:
    """Safety-net visitor for intermediate nodes: skip entirely."""
    raise nodes.SkipNode


def _depart_noop(self: NodeVisitorFunc, node: nodes.Element) -> None:
    pass


# =============================================================================
# Static File Handling
# =============================================================================


def _register_static_assets(app: Sphinx) -> None:
    """Register CSS filenames with Sphinx during builder-inited."""
    if app.builder.format != "html":
        return

    static_source = Path(__file__).parent / "static"
    static_dest = Path(app.outdir) / "_static"
    static_dest.mkdir(parents=True, exist_ok=True)

    css_file = static_source / "filter_tabs.css"
    if css_file.exists():
        shutil.copy(css_file, static_dest)

    app.add_css_file("filter_tabs.css")
    app.add_css_file("filter_tabs_theme.css")


def _write_theme_css(app: Sphinx, exception: Exception | None) -> None:
    """Write the generated theme CSS file after the build completes."""
    if exception is not None:
        return
    if app.builder.format != "html":
        return

    WARN_THRESHOLD = 15
    HARD_CAP = 20

    max_tabs = getattr(app.env, "filter_tabs_max_tab_count", 0)

    if max_tabs > HARD_CAP:
        logger.error(
            f"filter-tabs: a tab group with {max_tabs} tabs was found. "
            f"Tab groups are capped at {HARD_CAP} to prevent unusable output. "
            f"Selectors will be generated for indices 0–{HARD_CAP - 1} only."
        )
        max_tabs = HARD_CAP
    elif max_tabs > WARN_THRESHOLD:
        logger.warning(
            f"filter-tabs: a tab group with {max_tabs} tabs was found. "
            f"Tab groups this large are hard to navigate; consider restructuring the content."
        )

    def _selector(i: int) -> str:
        return (
            f'.sft-radio-group input[type="radio"][data-tab-index="{i}"]'
            f':checked ~ .sft-content > .sft-panel[data-tab-index="{i}"]'
        )

    if max_tabs > 0:
        selectors = ",\n".join(_selector(i) for i in range(max_tabs))
        visibility_block = (
            "/* Panel visibility — generated at build time, scoped with child\n"
            " * combinator (>) to isolate nested tab groups. */\n"
            f"{selectors} {{\n"
            "    display: block;\n"
            "}\n"
        )
    else:
        visibility_block = "/* No filter-tabs groups found in this build. */\n"

    color = app.config.filter_tabs_highlight_color
    theme_css = (
        "/* sphinx-filter-tabs: generated theme — do not edit by hand */\n"
        f":root {{ --sft-highlight-color: {color}; }}\n"
        "\n"
        f"{visibility_block}"
    )
    static_dest = Path(app.outdir) / "_static"
    static_dest.mkdir(parents=True, exist_ok=True)
    theme_file = static_dest / "filter_tabs_theme.css"
    theme_file.write_text(theme_css, encoding="utf-8")


# =============================================================================
# Extension Setup
# =============================================================================


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the sphinx-filter-tabs extension."""

    app.add_config_value("filter_tabs_highlight_color", "#007bff", "html", [str])
    app.add_config_value("filter_tabs_debug_mode", False, "html", [bool])

    # Intermediate nodes — stored in .doctrees, replaced at write time.
    # Safety-net visitors skip them if process_filter_tabs_nodes somehow
    # doesn't replace them (should never happen in practice).
    VisitorPair = tuple[NodeVisitorFunc, NodeVisitorFunc]
    _skip: VisitorPair = (_visit_skip_node, _depart_noop)
    _skip_builders = ("latex", "text", "man", "texinfo", "xml", "epub", "rinoh", "dummy")
    _skip_kwargs: dict[str, VisitorPair] = {b: _skip for b in _skip_builders}
    app.add_node(FilterTabsNode, html=_skip, **_skip_kwargs)
    app.add_node(FilterTabSlotNode, html=_skip, **_skip_kwargs)

    # Builder-specific output nodes — only appear after doctree-resolved.
    # All non-HTML builders get _skip because process_filter_tabs_nodes
    # replaces FilterTabsNode with plain admonitions (via _render_fallback)
    # before the writer ever visits these nodes.
    app.add_node(ContainerNode, html=(visit_container_node, depart_container_node), **_skip_kwargs)
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node), **_skip_kwargs)
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node), **_skip_kwargs)
    app.add_node(
        RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node), **_skip_kwargs
    )
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node), **_skip_kwargs)
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node), **_skip_kwargs)
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node), **_skip_kwargs)
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node), **_skip_kwargs)

    app.add_directive("filter-tabs", FilterTabsDirective)
    app.add_directive("tab", TabDirective)

    app.connect("builder-inited", _register_static_assets)
    # process_filter_tabs_nodes runs at write time (after doctree unpickling),
    # so FilterTabsNode is always resolved to the correct output for the active
    # builder — even when LaTeX and HTML builds share a .doctrees directory.
    # Tab content lives as real children of FilterTabsNode/FilterTabSlotNode,
    # so all transforms (including OnlyNodeTransform) run on it normally first.
    app.connect("doctree-resolved", process_filter_tabs_nodes)
    app.connect("doctree-resolved", setup_collapsible_admonitions)
    app.connect("build-finished", _write_theme_css)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
