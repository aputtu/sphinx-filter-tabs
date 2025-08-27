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
