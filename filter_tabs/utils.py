from __future__ import annotations

from dataclasses import dataclass

from sphinx.locale import _


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


def infer_content_type(tab_names: list[str]) -> str:
    """Infer a meaningful legend from tab names.

    Matching is performed in two passes over the predefined PATTERNS list:
    1. Exact keyword match (first pattern to match wins)
    2. Substring match (first pattern to match wins)
    """
    PATTERNS = [
        (
            ["python", "javascript", "java", "c++", "rust", "go", "ruby", "php"],
            _("programming language"),
        ),
        (["windows", "mac", "macos", "linux", "ubuntu", "debian", "fedora"], _("operating system")),
        (["pip", "conda", "npm", "yarn", "cargo", "gem", "composer"], _("package manager")),
        (["cli", "gui", "terminal", "command", "console", "graphical"], _("interface")),
        (["development", "staging", "production", "test", "local"], _("environment")),
        (["source", "binary", "docker", "manual", "automatic"], _("installation method")),
    ]
    lower_names = [name.lower() for name in tab_names]
    for keywords, content_type in PATTERNS:
        if any(name in keywords for name in lower_names):
            return content_type
    for keywords, content_type in PATTERNS:
        for name in lower_names:
            if any(keyword in name for keyword in keywords):
                return content_type
    return _("option")
