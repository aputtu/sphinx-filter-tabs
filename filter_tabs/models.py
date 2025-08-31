# filter_tabs/models.py
"""
Data models for the sphinx-filter-tabs extension.
Simplified to reduce complexity while maintaining functionality.
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
    Simplified configuration settings for filter-tabs rendering.
    Reduced from 9 options to 2 essential ones.
    """
    # Essential theming - only the highlight color is commonly customized
    highlight_color: str = '#007bff'
    
    # Development option
    debug_mode: bool = False
    
    @classmethod
    def from_sphinx_config(cls, app_config) -> 'FilterTabsConfig':
        """Create a FilterTabsConfig from Sphinx app.config."""
        return cls(
            highlight_color=getattr(
                app_config, 'filter_tabs_highlight_color', cls.highlight_color
            ),
            debug_mode=getattr(
                app_config, 'filter_tabs_debug_mode', cls.debug_mode
            ),
        )
    
    def to_css_properties(self) -> str:
        """Convert config to CSS custom properties string."""
        # Generate CSS variables - the highlight color drives all other colors
        return f"--sft-highlight-color: {self.highlight_color};"


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
