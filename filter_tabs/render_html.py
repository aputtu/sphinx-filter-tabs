from __future__ import annotations

from typing import Any

from docutils import nodes
from sphinx.locale import get_translation
from sphinx.writers.html import HTML5Translator

from .constants import SFT_INTERACTIVE, SFT_SR_ONLY
from .nodes import (
    DetailsNode,
    FilterTabNode,
    FilterTabPanelNode,
    FilterTabsContentNode,
    FilterTabSlotNode,
    RenderedFilterTabsNode,
    SummaryNode,
)
from .utils import IDGenerator, infer_content_type

_ = get_translation("sphinx-filter-tabs")


def render_html(
    slots: list[FilterTabSlotNode],
    general_content: list[nodes.Node],
    custom_legend: str | None,
    hide_legend: bool,
    id_gen: IDGenerator,
) -> list[nodes.Node]:
    """Produce the resolved HTML node structure."""
    container = RenderedFilterTabsNode(
        classes=["sft-container"],
    )
    container["group_id"] = id_gen.group_id
    container["legend_id"] = id_gen.legend_id()
    container["hide_legend"] = hide_legend

    # Resolve legend text
    if custom_legend:
        container["legend_text"] = custom_legend
    else:
        tab_names = [s["tab_name"] for s in slots]
        content_type = infer_content_type(tab_names)
        container["legend_text"] = _("Choose {content_type}: {tab_names}").format(
            content_type=content_type, tab_names=", ".join(tab_names)
        )

    default_index = next((i for i, s in enumerate(slots) if s["is_default"]), 0)

    # Add tab marker nodes (radio + label info)
    for i, slot in enumerate(slots):
        tab_node = FilterTabNode(
            tab_name=slot["tab_name"],
            is_default=(i == default_index),
            aria_label=slot.get("aria_label"),
            radio_id=id_gen.radio_id(i),
            label_id=id_gen.label_id(i),
            desc_id=id_gen.desc_id(i),
            panel_id=id_gen.panel_id(i),
            tab_index=str(i),
            group_id=id_gen.group_id,
        )
        container += tab_node

    # Add content container
    content_area = FilterTabsContentNode(classes=["sft-content"])
    container += content_area

    # Add general content panel
    if general_content:
        general_panel = FilterTabPanelNode(
            classes=["sft-panel"],
        )
        general_panel["data-filter"] = "General"
        general_panel.extend(c.deepcopy() for c in general_content)
        content_area += general_panel

    # Add tab panels
    for i, slot in enumerate(slots):
        panel = FilterTabPanelNode(
            classes=["sft-panel"],
            ids=[id_gen.panel_id(i)],
        )
        panel["data-tab"] = slot["tab_name"].lower().replace(" ", "-")
        panel["data-tab-index"] = str(i)
        panel.extend(c.deepcopy() for c in slot.children)
        content_area += panel

    return [container]


# =============================================================================
# HTML Visitor Functions
# =============================================================================


def _get_starttag_attrs(node: nodes.Element, exclude_keys: tuple[str, ...] = ()) -> dict[str, Any]:
    """Helper to extract attributes suitable for self.starttag() kwargs."""
    attrs = {}
    internal_keys = {
        "ids",
        "classes",
        "names",
        "dupnames",
        "backrefs",
        "legend_text",
        "legend_id",
        "hide_legend",
        "group_id",
        "radio_id",
        "label_id",
        "desc_id",
        "panel_id",
        "tab_index",
        "tab_name",
        "is_default",
        "aria_label",
    }
    for key, value in node.attributes.items():
        if key not in internal_keys and key not in exclude_keys:
            attrs[key] = value
    return attrs


def visit_rendered_filter_tabs_node(self: HTML5Translator, node: RenderedFilterTabsNode) -> None:
    # Outer container (div)
    self.body.append(self.starttag(node, "div", **_get_starttag_attrs(node)))

    # Fieldset
    fieldset_proxy = nodes.Element(classes=["sft-fieldset"])
    self.body.append(self.starttag(fieldset_proxy, "fieldset"))

    # Legend
    legend_classes = ["sft-legend"]
    if node.get("hide_legend"):
        legend_classes.append(SFT_SR_ONLY)
    legend_proxy = nodes.Element(classes=legend_classes, ids=[node["legend_id"]])
    self.body.append(self.starttag(legend_proxy, "legend"))
    self.body.append(self.encode(node["legend_text"]))
    self.body.append("</legend>")

    # CSS interaction container. It intentionally wraps controls and panels so
    # :checked sibling selectors can work without JavaScript.
    interactive_proxy = nodes.Element(classes=[SFT_INTERACTIVE])
    self.body.append(self.starttag(interactive_proxy, "div"))


def depart_rendered_filter_tabs_node(self: HTML5Translator, node: RenderedFilterTabsNode) -> None:
    self.body.append("</div></fieldset></div>")


def visit_filter_tab_node(self: HTML5Translator, node: FilterTabNode) -> None:
    """Render the hidden radio input and its visible label."""
    # Radio Input
    radio_proxy = nodes.Element(classes=[SFT_SR_ONLY], ids=[node["radio_id"]])
    radio_attrs = {
        "type": "radio",
        "name": node["group_id"],
        "aria-describedby": node["desc_id"],
        "aria-controls": node["panel_id"],
        "data-tab-index": node["tab_index"],
    }
    if node.get("aria_label"):
        radio_attrs["aria-label"] = node["aria_label"]
    if node["is_default"]:
        radio_attrs["checked"] = "checked"

    self.body.append(self.starttag(radio_proxy, "input", **radio_attrs))

    # Label
    label_proxy = nodes.Element(ids=[node["label_id"]])
    self.body.append(self.starttag(label_proxy, "label", **{"for": node["radio_id"]}))
    self.body.append(self.encode(node["tab_name"]))
    self.body.append("</label>")

    # Screen Reader Description
    desc_proxy = nodes.Element(classes=[SFT_SR_ONLY], ids=[node["desc_id"]])
    self.body.append(self.starttag(desc_proxy, "div"))
    desc_text = _("Show {tab_name} content").format(tab_name=node["tab_name"])
    self.body.append(self.encode(desc_text))
    self.body.append("</div>")


def depart_filter_tab_node(self: HTML5Translator, node: FilterTabNode) -> None:
    pass


def visit_filter_tabs_content_node(self: HTML5Translator, node: FilterTabsContentNode) -> None:
    self.body.append(self.starttag(node, "div", **_get_starttag_attrs(node)))


def depart_filter_tabs_content_node(self: HTML5Translator, node: FilterTabsContentNode) -> None:
    self.body.append("</div>")


def visit_filter_tab_panel_node(self: HTML5Translator, node: FilterTabPanelNode) -> None:
    self.body.append(self.starttag(node, "div", **_get_starttag_attrs(node)))


def depart_filter_tab_panel_node(self: HTML5Translator, node: FilterTabPanelNode) -> None:
    self.body.append("</div>")


def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append(self.starttag(node, "details", **_get_starttag_attrs(node)))


def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append("</details>")


def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, "summary", **_get_starttag_attrs(node)))


def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append("</summary>")
