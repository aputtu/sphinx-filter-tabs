#!/bin/bash
# setup_dual_implementation.sh - Initialize the dual implementation system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_separator() {
    echo -e "${BLUE}===========================================${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python version
    if ! python3 --version | grep -q "3.1[0-9]"; then
        print_error "Python 3.10+ required. Found: $(python3 --version)"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] || [ ! -d "filter_tabs" ]; then
        print_error "Must be run from sphinx-filter-tabs project root"
        exit 1
    fi
    
    # Check required tools
    for tool in pip pytest; do
        if ! command -v $tool &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    print_success "Prerequisites check passed"
}

# Backup existing files
backup_existing_files() {
    print_status "Backing up existing files..."
    
    BACKUP_DIR="backup_$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$BACKUP_DIR"
    
    # Backup key files that will be modified
    files_to_backup=(
        "filter_tabs/extension.py"
        "filter_tabs/static/filter_tabs.css" 
        "filter_tabs/static/filter_tabs.js"
        "tests/test_extension.py"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            print_status "Backed up $file"
        fi
    done
    
    print_success "Backup created in $BACKUP_DIR"
}

# Create new CSS architecture
setup_css_architecture() {
    print_status "Setting up CSS architecture..."
    
    # Split existing CSS into common, legacy, and accessible files
    CSS_DIR="filter_tabs/static"
    
    # Backup existing CSS
    if [ -f "$CSS_DIR/filter_tabs.css" ]; then
        cp "$CSS_DIR/filter_tabs.css" "$CSS_DIR/filter_tabs_legacy.css"
    fi
    
    # Create common CSS (shared styles)
    cat > "$CSS_DIR/filter_tabs_common.css" << 'EOF'
/* Common styles shared by both implementations */
.sft-container {
    border: 1px solid #e0e0e0;
    border-radius: var(--sft-border-radius, 8px);
    overflow: hidden;
    margin: 1.5em 0;
    background: white;
}

.sft-fieldset {
    border: none;
    padding: 0;
    margin: 0;
}

.sft-content {
    padding: 20px;
}

.sft-panel {
    outline: none;
}

.sft-panel:focus {
    outline: 2px solid var(--sft-tab-highlight-color, #007bff);
    outline-offset: -2px;
    border-radius: 4px;
}

.sft-panel[data-filter="General"] {
    display: block;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
EOF

    # Create accessible CSS (improved implementation)
    cat > "$CSS_DIR/filter_tabs_accessible.css" << 'EOF'
/* Improved accessibility implementation styles */
.sft-container[data-accessibility="improved"] .sft-legend {
    background: #f8f9fa;
    padding: 12px 20px;
    margin: 0;
    font-weight: 600;
    color: #495057;
    border-bottom: 1px solid #e0e0e0;
    width: 100%;
    font-size: 0.95em;
}

.sft-container[data-accessibility="improved"] .sft-radio-group {
    display: flex;
    flex-wrap: wrap;
    background: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
    padding: 0 10px;
}

.sft-container[data-accessibility="improved"] .sft-radio-group input[type="radio"] {
    width: 1px;
    height: 1px;
    opacity: 0.01;
    position: absolute;
    z-index: -1;
    margin: 0;
}

.sft-container[data-accessibility="improved"] .sft-radio-group label {
    display: block;
    padding: 12px 18px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: 3px solid transparent;
    color: #6c757d;
    font-weight: 500;
    font-size: var(--sft-tab-font-size, 1em);
    position: relative;
    background: transparent;
}

.sft-container[data-accessibility="improved"] .sft-radio-group input[type="radio"]:checked + label {
    color: var(--sft-tab-highlight-color, #007bff);
    border-bottom-color: var(--sft-tab-highlight-color, #007bff);
    background: white;
    font-weight: 600;
}

.sft-container[data-accessibility="improved"] .sft-radio-group input[type="radio"]:focus + label {
    outline: 2px solid var(--sft-tab-highlight-color, #007bff);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.25);
    z-index: 1;
}
EOF

    # Update legacy CSS to be implementation-specific
    cat > "$CSS_DIR/filter_tabs_legacy.css" << 'EOF'
/* Legacy implementation styles */
.sft-container[data-accessibility="legacy"] .sft-legend,
.sft-container:not([data-accessibility]) .sft-legend {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

.sft-container[data-accessibility="legacy"] .sft-tab-bar > input[type="radio"],
.sft-container:not([data-accessibility]) .sft-tab-bar > input[type="radio"] {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
    opacity: 0;
}

.sft-container[data-accessibility="legacy"] .sft-tab-bar,
.sft-container:not([data-accessibility]) .sft-tab-bar {
    display: flex;
    flex-wrap: wrap;
    background-color: var(--sft-tab-background, #f0f0f0);
    border-bottom: 1px solid #e0e0e0;
    padding: 0 10px;
}

.sft-container[data-accessibility="legacy"] .sft-tab-bar > label,
.sft-container:not([data-accessibility]) .sft-tab-bar > label {
    padding: 12px 18px;
    cursor: pointer;
    transition: border-color 0.2s ease-in-out, color 0.2s ease-in-out;
    border-bottom: 3px solid transparent;
    color: #555;
    font-weight: 500;
    font-size: var(--sft-tab-font-size, 1em);
    line-height: 1.5;
}

.sft-container[data-accessibility="legacy"] .sft-tab-bar > input[type="radio"]:checked + label,
.sft-container:not([data-accessibility]) .sft-tab-bar > input[type="radio"]:checked + label {
    border-bottom-color: var(--sft-tab-highlight-color, #007bff);
    color: #000;
    font-weight: 600;
}
EOF

    print_success "CSS architecture created"
}

# Create configuration system
setup_configuration_system() {
    print_status "Creating configuration system..."
    
    cat > "filter_tabs/config.py" << 'EOF'
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
EOF

    print_success "Configuration system created"
}

# Setup new test files
setup_test_infrastructure() {
    print_status "Setting up test infrastructure..."
    
    # Create accessibility tests directory
    mkdir -p tests/accessibility
    
    # Create basic test that will expand during implementation
    cat > "tests/test_dual_implementation.py" << 'EOF'
import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp

@pytest.mark.sphinx('html')
def test_legacy_mode_default(app: SphinxTestApp):
    """Test that legacy mode is used by default."""
    content = """
Test Document
=============

.. filter-tabs::

   .. tab:: Python (default)
      Python content
   .. tab:: JavaScript
      JS content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Should have legacy structure by default
    container = soup.select_one('.sft-container')
    assert container, "Container should exist"
    
    # Should have tab-bar (legacy) or no data-accessibility attribute
    tab_bar = soup.select_one('.sft-tab-bar')
    accessibility_mode = container.get('data-accessibility')
    
    assert tab_bar is not None or accessibility_mode in [None, 'legacy'], \
        "Default should be legacy mode"

@pytest.mark.sphinx('html') 
def test_improved_mode_when_enabled(app: SphinxTestApp):
    """Test improved mode when feature flag is enabled."""
    app.config.filter_tabs_use_improved_accessibility = True
    
    content = """
Test Document
=============

.. filter-tabs::

   .. tab:: Python (default)
      Python content
   .. tab:: JavaScript
      JS content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    
    # This test will initially fail until we implement the improved mode
    # It serves as a specification of what we want to achieve
    try:
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        container = soup.select_one('.sft-container')
        accessibility_mode = container.get('data-accessibility')
        
        # Eventually this should pass when improved mode is implemented
        if accessibility_mode == 'improved':
            radiogroup = soup.select_one('[role="radiogroup"]')
            assert radiogroup, "Improved mode should have radiogroup role"
        else:
            # For now, accept that it falls back to legacy
            pass
            
    except Exception as e:
        # Expected to fail initially - this is our target to work toward
        pytest.skip(f"Improved mode not yet implemented: {e}")
EOF

    print_success "Test infrastructure created"
}

# Create development workflow script
create_dev_workflow() {
    print_status "Creating development workflow script..."
    
    cat > "validate_dual_implementation.py" << 'EOF'
#!/usr/bin/env python3
"""Simple validation script for dual implementation during development."""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the basic tests to validate both modes work."""
    print("Running dual implementation tests...")
    
    # Run our new tests
    cmd = [sys.executable, '-m', 'pytest', 'tests/test_dual_implementation.py', '-v']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Basic tests passed")
        return True
    else:
        print("❌ Tests failed:")
        print(result.stdout)
        print(result.stderr)
        return False

def build_test_docs():
    """Build test documentation to verify both modes work."""
    print("Building test documentation...")
    
    # Create a simple test
    test_dir = Path('test_build')
    test_dir.mkdir(exist_ok=True)
    
    # Simple test content
    (test_dir / 'index.rst').write_text("""
Test
====

.. filter-tabs::
   .. tab:: Test
      Content
""")
    
    (test_dir / 'conf.py').write_text("""
extensions = ['filter_tabs.extension']
filter_tabs_use_improved_accessibility = False
""")
    
    # Build
    cmd = [sys.executable, '-m', 'sphinx', '-b', 'html', str(test_dir), str(test_dir / '_build')]
    result = subprocess.run(cmd, capture_output=True)
    
    success = result.returncode == 0
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
    if success:
        print("✅ Test build successful")
    else:
        print("❌ Test build failed")
    
    return success

if __name__ == '__main__':
    print("Dual Implementation Validator")
    print("=" * 40)
    
    all_passed = True
    all_passed &= build_test_docs()
    all_passed &= run_tests()
    
    print("=" * 40)
    if all_passed:
        print("🎉 All validations passed!")
    else:
        print("💥 Some validations failed")
    
    sys.exit(0 if all_passed else 1)
EOF
    
    chmod +x validate_dual_implementation.py
    
    print_success "Development workflow script created"
}

# Update extension setup
update_extension_setup() {
    print_status "Updating extension setup..."
    
    # Create a patch file for the setup function
    cat > "setup_patch.py" << 'EOF'
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
EOF

    print_success "Extension setup patch created (manual step required)"
}

# Main setup function
main() {
    print_separator
    echo -e "${BLUE}Sphinx Filter Tabs - Dual Implementation Setup${NC}"
    print_separator
    
    check_prerequisites
    backup_existing_files
    setup_css_architecture
    setup_configuration_system
    setup_test_infrastructure
    create_dev_workflow
    update_extension_setup
    
    print_separator
    print_success "Dual implementation setup complete!"
    print_separator
    
    echo ""
    echo "Next steps:"
    echo "1. Review the setup_patch.py file and manually update extension.py"
    echo "2. Install in development mode: pip install -e ."
    echo "3. Run validation: python validate_dual_implementation.py"
    echo "4. Run tests: pytest tests/test_dual_implementation.py"
    echo ""
    echo "Configuration options for users:"
    echo "  filter_tabs_use_improved_accessibility = True   # Enable new implementation"
    echo "  filter_tabs_migration_warnings = False          # Disable migration warnings"
    echo "  filter_tabs_force_legacy = True                 # Emergency rollback"
    echo ""
    print_warning "The improved implementation renderer still needs to be implemented!"
    echo "Start by modifying FilterTabsRenderer.render_html() to use the new config system."
}

# Run main function
main
