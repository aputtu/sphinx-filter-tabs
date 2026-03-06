from __future__ import annotations

from dataclasses import dataclass

from sphinx.config import Config

_SFT_WARN_THRESHOLD = 15
_SFT_HARD_CAP = 20


@dataclass
class FilterTabsConfig:
    """Simplified configuration settings for filter-tabs rendering."""

    highlight_color: str = "#007bff"
    theme_mode: str = "native"
    flavor: str = "default"
    debug_mode: bool = False

    @classmethod
    def from_sphinx_config(cls, app_config: Config) -> FilterTabsConfig:
        return cls(
            highlight_color=getattr(app_config, "filter_tabs_highlight_color", cls.highlight_color),
            # CRITICAL: pull the new values from the user's conf.py
            theme_mode=getattr(app_config, "filter_tabs_theme_mode", cls.theme_mode),
            flavor=getattr(app_config, "filter_tabs_flavor", cls.flavor),
            # ---
            debug_mode=getattr(app_config, "filter_tabs_debug_mode", cls.debug_mode),
        )
