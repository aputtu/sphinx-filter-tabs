#!/usr/bin/env python3
"""
Development validation script for sphinx-filter-tabs dual implementation.
Run this to validate both implementations work correctly during development.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import argparse


def run_command(cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        cwd=cwd
    )
    return result


def create_test_project(test_dir: Path, implementation_mode: str) -> None:
    """Create a test project with the specified implementation mode."""
    # Create directories
    (test_dir / 'docs').mkdir(parents=True)
    (test_dir / 'docs' / '_static').mkdir()
    
    # Create conf.py
    conf_content = f"""
project = 'Filter Tabs Test'
extensions = ['filter_tabs.extension']

# Test configuration
filter_tabs_use_improved_accessibility = {implementation_mode == 'improved'}
filter_tabs_migration_warnings = False
filter_tabs_debug_mode = True
filter_tabs_tab_highlight_color = '#007bff'
"""
    (test_dir / 'docs' / 'conf.py').write_text(conf_content)
    
    # Create test RST content
    rst_content = """
Filter Tabs Test
===============

Basic Example
-------------

.. filter-tabs::

    This is general content visible to all tabs.

    .. tab:: Python (default)
    
        Python-specific content:
        
        .. code-block:: python
        
            def hello():
                print("Hello from Python!")

    .. tab:: JavaScript
       :aria-label: JavaScript programming language examples
    
        JavaScript-specific content:
        
        .. code-block:: javascript
        
            function hello() {
                console.log("Hello from JavaScript!");
            }

    .. tab:: Rust
    
        Rust-specific content:
        
        .. code-block:: rust
        
            fn hello() {
                println!("Hello from Rust!");
            }

Nested Example
--------------

.. filter-tabs::

    .. tab:: Windows (default)
    
        Windows installation:
        
        .. filter-tabs::
        
            .. tab:: Pip
                Use pip to install
            .. tab:: Conda
                Use conda to install
                
    .. tab:: macOS
    
        macOS installation instructions.

Mixed Content Example
--------------------

.. filter-tabs::

    General instructions that apply to all platforms.
    
    .. note::
        This is a general note visible to all tabs.

    .. tab:: Platform A
        Specific to Platform A
        
    More general content here.
    
    .. tab:: Platform B (default)
        Specific to Platform B
"""
    (test_dir / 'docs' / 'index.rst').write_text(rst_content)


def validate_html_output(html_file: Path, implementation_mode: str) -> List[str]:
    """Validate the HTML output and return any issues found."""
    issues = []
    
    if not html_file.exists():
        issues.append(f"HTML file does not exist: {html_file}")
        return issues
    
    html_content = html_file.read_text()
    
    # Import BeautifulSoup for parsing
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        issues.append("BeautifulSoup not available for HTML validation")
        return issues
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check basic structure
    containers = soup.select('.sft-container')
    if not containers:
        issues.append("No .sft-container elements found")
        return issues
    
    # Check implementation-specific features
    if implementation_mode == 'improved':
        # Check for improved accessibility features
        radiogroups = soup.select('[role="radiogroup"]')
        if not radiogroups:
            issues.append("Improved mode: Missing role='radiogroup'")
        
        # Check for visible legend
        legends = soup.select('.sft-legend')
        for legend in legends:
            if 'sr-only' in legend.get('class', []):
                issues.append("Improved mode: Legend should be visible, not sr-only")
        
        # Check for radio-group structure
        radio_groups = soup.select('.sft-radio-group')
        if not radio_groups:
            issues.append("Improved mode: Missing .sft-radio-group structure")
        
        # Check for region roles on panels
        regions = soup.select('.sft-panel[role="region"]')
        if not regions:
            issues.append("Improved mode: Panels should have role='region'")
        
        # Check for screen reader descriptions
        sr_descriptions = soup.select('.sr-only')
        if len(sr_descriptions) < 3:  # Should have descriptions for tabs
            issues.append("Improved mode: Missing screen reader descriptions")
    
    else:  # legacy mode
        # Check for legacy structure
        tab_bars = soup.select('.sft-tab-bar')
        if not tab_bars:
            issues.append("Legacy mode: Missing .sft-tab-bar structure")
        
        # Check for tabpanel roles
        tabpanels = soup.select('.sft-panel[role="tabpanel"]')
        if not tabpanels:
            issues.append("Legacy mode: Missing role='tabpanel' on panels")
    
    # Check common requirements
    radios = soup.select('input[type="radio"]')
    if len(radios) < 3:
        issues.append(f"Expected at least 3 radio buttons, found {len(radios)}")
    
    # Check for unique IDs
    all_ids = [elem.get('id') for elem in soup.select('[id]') if elem.get('id')]
    duplicate_ids = [id_val for id_val in set(all_ids) if all_ids.count(id_val) > 1]
    if duplicate_ids:
        issues.append(f"Duplicate IDs found: {duplicate_ids}")
    
    # Validate ARIA relationships
    for attr in ['aria-labelledby', 'aria-describedby']:
        elements = soup.select(f'[{attr}]')
        for element in elements:
            referenced_ids = element.get(attr, '').split()
            for ref_id in referenced_ids:
                if ref_id and not soup.select_one(f'#{ref_id}'):
                    issues.append(f"ARIA attribute {attr} references missing ID: {ref_id}")
    
    return issues


def test_implementation_mode(mode: str, verbose: bool = False) -> bool:
    """Test a specific implementation mode and return success status."""
    print(f"\nTesting {mode} implementation...")
    
    # Create temporary test project
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_project(test_dir, mode)
        
        # Build the documentation
        build_cmd = [
            sys.executable, '-m', 'sphinx',
            '-b', 'html',
            str(test_dir / 'docs'),
            str(test_dir / 'docs' / '_build' / 'html')
        ]
        
        if verbose:
            print(f"Running: {' '.join(build_cmd)}")
        
        result = run_command(build_cmd)
        
        if result.returncode != 0:
            print(f"❌ Build failed for {mode} mode")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Validate HTML output
        html_file = test_dir / 'docs' / '_build' / 'html' / 'index.html'
        issues = validate_html_output(html_file, mode)
        
        if issues:
            print(f"❌ Validation failed for {mode} mode:")
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        print(f"✅ {mode} implementation passed all tests")
        
        if verbose:
            # Show some sample HTML
            html_content = html_file.read_text()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            container = soup.select_one('.sft-container')
            print(f"Sample HTML structure for {mode}:")
            print(container.prettify()[:500] + "..." if len(str(container)) > 500 else container.prettify())
        
        return True


def run_pytest_tests(test_files: List[str] = None, verbose: bool = False) -> bool:
    """Run pytest tests and return success status."""
    print("\nRunning pytest tests...")
    
    cmd = [sys.executable, '-m', 'pytest']
    
    if test_files:
        cmd.extend(test_files)
    else:
        cmd.extend(['tests/', '-k', 'test_accessibility or test_dual'])
    
    if verbose:
        cmd.append('-v')
    
    result = run_command(cmd)
    
    if result.returncode != 0:
        print("❌ pytest tests failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("✅ All pytest tests passed")
    return True


def check_css_files() -> bool:
    """Check that required CSS files exist."""
    print("\nChecking CSS files...")
    
    css_files = [
        'filter_tabs/static/filter_tabs_common.css',
        'filter_tabs/static/filter_tabs_legacy.css',
        'filter_tabs/static/filter_tabs_accessible.css'
    ]
    
    missing_files = []
    for css_file in css_files:
        if not Path(css_file).exists():
            missing_files.append(css_file)
    
    if missing_files:
        print("❌ Missing CSS files:")
        for file in missing_files:
            print(f"  • {file}")
        return False
    
    print("✅ All required CSS files exist")
    return True


def main():
    parser = argparse.ArgumentParser(description='Validate sphinx-filter-tabs dual implementation')
    parser.add_argument('--mode', choices=['legacy', 'improved', 'both'], default='both',
                      help='Which implementation mode to test')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Verbose output')
    parser.add_argument('--skip-pytest', action='store_true',
                      help='Skip running pytest tests')
    parser.add_argument('--skip-css-check', action='store_true',
                      help='Skip checking CSS files')
    
    args = parser.parse_args()
    
    print("Sphinx Filter Tabs - Dual Implementation Validator")
    print("=" * 50)
    
    success = True
    
    # Check CSS files
    if not args.skip_css_check:
        success &= check_css_files()
    
    # Test implementation modes
    modes_to_test = ['both'] if args.mode == 'both' else [args.mode]
    if 'both' in modes_to_test:
        modes_to_test = ['legacy', 'improved']
    
    for mode in modes_to_test:
        success &= test_implementation_mode(mode, args.verbose)
    
    # Run pytest tests
    if not args.skip_pytest:
        success &= run_pytest_tests(verbose=args.verbose)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All validations passed! Both implementations are working correctly.")
        return 0
    else:
        print("💥 Some validations failed. Please check the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
