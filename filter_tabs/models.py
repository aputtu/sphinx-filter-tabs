# filter_tabs/models.py
"""
Data models for the sphinx-filter-tabs extension.

This module provides type-safe data structures to replace dictionaries
and improve code maintainability.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from docutils import nodes


@dataclass
class TabData:
    """
    Represents a single tab's data within a filter-tabs directive.
    
    Attributes:
        name: Display name of the tab
        is_default: Whether this tab should be selected by default
        aria_label: Optional ARIA label for accessibility
        content: List of docutils nodes containing the tab's content
    """
    name: str
    is_default: bool = False
    aria_label: Optional[str] = None
    content: List[nodes.Node] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate tab data after initialization."""
        if not self.name:
            raise ValueError("Tab name cannot be empty")
        
        # Ensure content is a list
        if self.content is None:
            self.content = []


@dataclass
class FilterTabsConfig:
    """
    Configuration settings for filter-tabs rendering.
    
    This centralizes all configuration access and provides defaults.
    """
    # Theming
    tab_highlight_color: str = '#007bff'
    tab_background_color: str = '#f0f0f0' 
    tab_font_size: str = '1em'
    border_radius: str = '8px'
    
    # Features
    debug_mode: bool = False
    collapsible_enabled: bool = True
    collapsible_accent_color: str = '#17a2b8'
    
    # Accessibility
    keyboard_navigation: bool = True
    announce_changes: bool = True
    
    @classmethod
    def from_sphinx_config(cls, app_config) -> 'FilterTabsConfig':
        """
        Create a FilterTabsConfig from Sphinx app.config.
        
        Args:
            app_config: Sphinx application config object
            
        Returns:
            FilterTabsConfig instance with values from Sphinx config
        """
        return cls(
            tab_highlight_color=getattr(
                app_config, 'filter_tabs_tab_highlight_color', cls.tab_highlight_color
            ),
            tab_background_color=getattr(
                app_config, 'filter_tabs_tab_background_color', cls.tab_background_color
            ),
            tab_font_size=getattr(
                app_config, 'filter_tabs_tab_font_size', cls.tab_font_size
            ),
            border_radius=getattr(
                app_config, 'filter_tabs_border_radius', cls.border_radius
            ),
            debug_mode=getattr(
                app_config, 'filter_tabs_debug_mode', cls.debug_mode
            ),
            collapsible_enabled=getattr(
                app_config, 'filter_tabs_collapsible_enabled', cls.collapsible_enabled
            ),
            collapsible_accent_color=getattr(
                app_config, 'filter_tabs_collapsible_accent_color', cls.collapsible_accent_color
            ),
            keyboard_navigation=getattr(
                app_config, 'filter_tabs_keyboard_navigation', cls.keyboard_navigation
            ),
            announce_changes=getattr(
                app_config, 'filter_tabs_announce_changes', cls.announce_changes
            ),
        )
    
    def to_css_properties(self) -> str:
        """
        Convert config to CSS custom properties string.
        
        Returns:
            CSS custom properties as a style attribute value
        """
        properties = {
            "--sft-border-radius": self.border_radius,
            "--sft-tab-background": self.tab_background_color,
            "--sft-tab-font-size": self.tab_font_size,
            "--sft-tab-highlight-color": self.tab_highlight_color,
            "--sft-collapsible-accent-color": self.collapsible_accent_color,
        }
        
        return "; ".join([f"{key}: {value}" for key, value in properties.items()])


@dataclass
class IDGenerator:
    """
    Centralized ID generation for consistent element identification.
    
    This ensures all IDs follow a consistent pattern and are unique
    within their filter-tabs group.
    """
    group_id: str
    
    def radio_id(self, index: int) -> str:
        """Generate ID for a radio button."""
        return f"{self.group_id}-radio-{index}"
    
    def panel_id(self, index: int) -> str:
        """Generate ID for a content panel."""
        return f"{self.group_id}-panel-{index}"
    
    def desc_id(self, index: int) -> str:
        """Generate ID for a screen reader description."""
        return f"{self.group_id}-desc-{index}"
    
    def legend_id(self) -> str:
        """Generate ID for the fieldset legend."""
        return f"{self.group_id}-legend"
    
    def label_id(self, index: int) -> str:
        """Generate ID for a label (if needed)."""
        return f"{self.group_id}-label-{index}"
