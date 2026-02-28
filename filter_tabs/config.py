from __future__ import annotations

from dataclasses import dataclass

from sphinx.config import Config

_SFT_WARN_THRESHOLD = 15
_SFT_HARD_CAP = 20


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
