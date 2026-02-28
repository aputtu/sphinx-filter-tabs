from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

from .nodes import FilterTabSlotNode, FilterTabsNode

logger = logging.getLogger(__name__)


class TabDirective(Directive):
    """Handles the ``.. tab::`` directive, capturing its content and options."""

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {"aria-label": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env

        sft_context = getattr(env, "sft_context", 0)
        if not isinstance(sft_context, int) or sft_context <= 0:
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

        if not hasattr(env, "sft_context") or not isinstance(env.sft_context, int):
            env.sft_context = 0

        env.sft_context += 1
        try:
            # Parse content into a temporary container; TabDirective will produce
            # FilterTabSlotNode instances and everything else is general content.
            temp_container = nodes.container()
            self.state.nested_parse(self.content, self.content_offset, temp_container)
        finally:
            env.sft_context -= 1

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
