"""Configuration management for sphinx-filter-tabs with feature flags."""

from typing import Dict, Any
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

class FilterTabsConfig:
    """Manages configuration with migration support."""
    
    def __init__(self, app: Sphinx):
        self.app = app
        self.config = app.config
        
    @property
    def use_improved_accessibility(self) -> bool:
        return getattr(self.config, 'filter_tabs_use_improved_accessibility', False)
    
    @property
    def show_migration_warnings(self) -> bool:
        return getattr(self.config, 'filter_tabs_migration_warnings', True)
    
    @property
    def force_legacy_mode(self) -> bool:
        return getattr(self.config, 'filter_tabs_force_legacy', False)
    
    def get_implementation_mode(self) -> str:
        if self.force_legacy_mode:
            if self.show_migration_warnings:
                logger.warning("filter_tabs_force_legacy enabled - using legacy implementation")
            return "legacy"
        elif self.use_improved_accessibility:
            return "improved"
        else:
            if self.show_migration_warnings:
                logger.info("Using legacy implementation. Set filter_tabs_use_improved_accessibility=True for better accessibility")
            return "legacy"
    
    def get_css_files(self) -> list[str]:
        mode = self.get_implementation_mode()
        css_files = ['filter_tabs_common.css']
        
        if mode == "improved":
            css_files.append('filter_tabs_accessible.css')
        else:
            css_files.append('filter_tabs_legacy.css')
            
        return css_files
    
    def get_js_files(self) -> list[str]:
        """Get list of JavaScript files to include."""
        # JavaScript enhancement works with both implementations
        return ['filter_tabs.js']
    
    def get_container_attributes(self, group_id: str) -> Dict[str, Any]:
        mode = self.get_implementation_mode()
        
        attrs = {
            'classes': ['sft-container'],
            'data-accessibility': mode,
            'style': self._get_css_custom_properties()
        }
        
        if mode == "improved":
            attrs['role'] = 'region'
            attrs['aria-labelledby'] = f'{group_id}-legend'
        
        return attrs
    
    def _get_css_custom_properties(self) -> str:
        properties = {
            "--sft-border-radius": getattr(self.config, 'filter_tabs_border_radius', '8px'),
            "--sft-tab-background": getattr(self.config, 'filter_tabs_tab_background_color', '#f0f0f0'),
            "--sft-tab-font-size": getattr(self.config, 'filter_tabs_tab_font_size', '1em'),
            "--sft-tab-highlight-color": getattr(self.config, 'filter_tabs_tab_highlight_color', '#007bff'),
            "--sft-collapsible-accent-color": getattr(self.config, 'filter_tabs_collapsible_accent_color', '#17a2b8'),
        }
        
        return "; ".join([f"{key}: {value}" for key, value in properties.items()])

def setup_filter_tabs_config(app: Sphinx) -> None:
    """Register configuration values for filter-tabs extension."""
    
    # Existing configuration options
    app.add_config_value('filter_tabs_tab_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_tab_background_color', '#f0f0f0', 'html', [str])
    app.add_config_value('filter_tabs_tab_font_size', '1em', 'html', [str])
    app.add_config_value('filter_tabs_border_radius', '8px', 'html', [str])
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_enabled', True, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_accent_color', '#17a2b8', 'html', [str])
    
    # Accessibility configuration options
    app.add_config_value('filter_tabs_keyboard_navigation', True, 'html', [bool])
    app.add_config_value('filter_tabs_announce_changes', True, 'html', [bool])
    
    # New migration and feature flag options
    app.add_config_value('filter_tabs_use_improved_accessibility', False, 'html', [bool])
    app.add_config_value('filter_tabs_migration_warnings', True, 'html', [bool])
    app.add_config_value('filter_tabs_force_legacy', False, 'html', [bool])
    
    # Validation options for development
    app.add_config_value('filter_tabs_validate_aria', False, 'html', [bool])
    app.add_config_value('filter_tabs_strict_validation', False, 'html', [bool])