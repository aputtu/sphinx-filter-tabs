"""
Patch to update the setup() function in extension.py to support dual implementation.
This adds the new configuration values needed for the feature flags.
"""

# Add these lines to the setup() function in extension.py:

new_config_values = '''
    # New migration and feature flag options
    app.add_config_value('filter_tabs_use_improved_accessibility', False, 'html', [bool])
    app.add_config_value('filter_tabs_migration_warnings', True, 'html', [bool])
    app.add_config_value('filter_tabs_force_legacy', False, 'html', [bool])
'''

print("Add these configuration values to your setup() function:")
print(new_config_values)
print("\nAlso import the new config system:")
print("from .config import FilterTabsConfig")
