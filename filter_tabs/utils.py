from __future__ import annotations

from dataclasses import dataclass

from sphinx.locale import get_translation

_ = get_translation("sphinx-filter-tabs")

_CONTENT_TYPE_PATTERNS = (
    (("python", "javascript", "java", "c++", "rust", "go", "ruby", "php"), "programming language"),
    (("windows", "mac", "macos", "linux", "ubuntu", "debian", "fedora"), "operating system"),
    (("pip", "conda", "npm", "yarn", "cargo", "gem", "composer"), "package manager"),
    (("cli", "gui", "terminal", "command", "console", "graphical"), "interface"),
    (("development", "staging", "production", "test", "local"), "environment"),
    (("source", "binary", "docker", "manual", "automatic"), "installation method"),
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

    def label_id(self, index: int) -> str:
        return f"{self.group_id}-label-{index}"

    def legend_id(self) -> str:
        return f"{self.group_id}-legend"


def infer_content_type(tab_names: list[str]) -> str:
    """Infer a meaningful legend from tab names.

    Matching is performed in two passes:
    1. Exact keyword match (first pattern to match wins)
    2. Substring match (first pattern to match wins)
    """
    lower_names = [name.lower() for name in tab_names]
    for keywords, content_type in _CONTENT_TYPE_PATTERNS:
        if any(name in keywords for name in lower_names):
            return _(content_type)
    for keywords, content_type in _CONTENT_TYPE_PATTERNS:
        for name in lower_names:
            if any(keyword in name for keyword in keywords):
                return _(content_type)
    return _("option")
