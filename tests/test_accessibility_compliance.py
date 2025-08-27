# tests/test_accessibility_compliance.py
"""
Comprehensive accessibility testing for sphinx-filter-tabs extension.
These tests establish baseline behavior and ensure accessibility improvements
don't break existing functionality.
"""

import pytest
import re
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestCurrentAccessibility:
    """Test the current implementation to establish baseline behavior."""
    
    @pytest.mark.sphinx('html')
    def test_current_structure_baseline(self, app: SphinxTestApp):
        """Document current HTML structure for regression testing."""
        content = """
Test Document
=============

.. filter-tabs::

    This is general content.
    
    .. tab:: Python (default)
    
        Python specific content.
        
    .. tab:: JavaScript
    
        JavaScript specific content.
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Document current structure
        container = soup.select_one('.sft-container')
        assert container, "Main container exists"
        
        fieldset = soup.select_one('.sft-fieldset')
        assert fieldset, "Fieldset exists"
        
        legend = soup.select_one('.sft-legend')
        assert legend, "Legend exists"
        
        radios = soup.select('.sft-tab-bar input[type="radio"]')
        assert len(radios) == 2, "Two radio buttons exist"
        
        labels = soup.select('.sft-tab-bar label')
        assert len(labels) == 2, "Two labels exist"
        
        panels = soup.select('.sft-panel[role="tabpanel"]')
        assert len(panels) == 2, "Two panels exist"
        
        # Store baseline for comparison after refactoring
        return {
            'radio_count': len(radios),
            'panel_count': len(panels),
            'has_general_content': bool(soup.select_one('.sft-panel[data-filter="General"]')),
            'default_checked': bool(soup.select_one('input[checked]'))
        }

    @pytest.mark.sphinx('html')
    def test_current_aria_attributes(self, app: SphinxTestApp):
        """Document current ARIA implementation."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: CLI
       :aria-label: Command line instructions
       
        CLI content.
        
    .. tab:: GUI
       
        GUI content.
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Test current ARIA label implementation
        radios = soup.select('input[type="radio"]')
        aria_labels = [r.get('aria-label') for r in radios]
        
        assert aria_labels[0] == "Command line instructions", "Custom ARIA label preserved"
        assert aria_labels[1] is None, "No ARIA label when not specified"
        
        # Test panel ARIA
        panels = soup.select('.sft-panel[role="tabpanel"]')
        for panel in panels:
            assert panel.get('aria-labelledby'), "Panel has aria-labelledby"
            assert panel.get('tabindex') == '0', "Panel is focusable"

    @pytest.mark.sphinx('html')
    def test_keyboard_accessibility_baseline(self, app: SphinxTestApp):
        """Test current keyboard accessibility features."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Tab1
        Content 1
    .. tab:: Tab2
        Content 2
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Check radio buttons are keyboard accessible
        radios = soup.select('input[type="radio"]')
        for radio in radios:
            # Radio buttons should not have tabindex (default behavior)
            assert radio.get('tabindex') is None
            
        # Check panels are focusable
        panels = soup.select('.sft-panel[role="tabpanel"]')
        for panel in panels:
            assert panel.get('tabindex') == '0', "Panels should be focusable"


class TestProposedImprovements:
    """Test improved accessibility implementation (when feature flag enabled)."""
    
    @pytest.mark.sphinx('html')
    def test_proper_radiogroup_semantics(self, app: SphinxTestApp):
        """Test that improved version uses proper radiogroup semantics."""
        # This test will initially fail - it defines our target
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Option A
        Content A
    .. tab:: Option B
        Content B
"""
        
        # Set feature flag for improved accessibility
        app.config.filter_tabs_use_improved_accessibility = True
        
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Test for proper radiogroup role
        radiogroup = soup.select_one('[role="radiogroup"]')
        assert radiogroup is not None, "Should have role='radiogroup'"
        
        # Test legend is visible and meaningful
        legend = soup.select_one('.sft-legend')
        assert legend, "Legend should exist"
        
        # Legend should NOT have sr-only class in improved version
        legend_classes = legend.get('class', [])
        assert 'sr-only' not in legend_classes, "Legend should be visible in improved version"
        
        # Test for proper descriptions
        radios = soup.select('input[type="radio"]')
        for radio in radios:
            describedby = radio.get('aria-describedby')
            if describedby:
                desc_element = soup.select_one(f'#{describedby}')
                assert desc_element, f"Description element {describedby} should exist"

    @pytest.mark.sphinx('html') 
    def test_screen_reader_descriptions(self, app: SphinxTestApp):
        """Test that screen reader descriptions are meaningful."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python
        Python code
    .. tab:: JavaScript  
        JS code
"""
        
        app.config.filter_tabs_use_improved_accessibility = True
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Check for screen reader descriptions
        sr_descriptions = soup.select('.sr-only')
        description_texts = [desc.get_text().strip() for desc in sr_descriptions]
        
        # Should have meaningful descriptions like "Show Python content"
        assert any('python' in desc.lower() for desc in description_texts), \
            "Should have Python description"
        assert any('javascript' in desc.lower() for desc in description_texts), \
            "Should have JavaScript description"

    @pytest.mark.sphinx('html')
    def test_focus_management_improved(self, app: SphinxTestApp):
        """Test improved focus management."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Tab1
        Content 1
    .. tab:: Tab2
        Content 2
"""
        
        app.config.filter_tabs_use_improved_accessibility = True
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # In improved version, panels should still be focusable
        panels = soup.select('.sft-panel[role="region"]')  # Changed from tabpanel to region
        for panel in panels:
            assert panel.get('tabindex') == '0', "Panels should remain focusable"


class TestBackwardCompatibility:
    """Ensure changes don't break existing functionality."""
    
    @pytest.mark.sphinx('html')
    def test_existing_syntax_still_works(self, app: SphinxTestApp):
        """Test that all existing syntax patterns continue to work."""
        test_cases = [
            # Basic tabs
            """
.. filter-tabs::

    .. tab:: Python
        Python content
    .. tab:: JavaScript
        JS content
""",
            # Tabs with default
            """
.. filter-tabs::

    .. tab:: Python (default)
        Python content
    .. tab:: JavaScript
        JS content
""",
            # Tabs with ARIA labels
            """
.. filter-tabs::

    .. tab:: CLI
       :aria-label: Command line interface
       CLI content
    .. tab:: GUI
       GUI content
""",
            # Mixed general and tab content
            """
.. filter-tabs::

    General content here.
    
    .. tab:: Option1
        Tab content
    .. tab:: Option2
        More tab content
        
    More general content.
"""
        ]
        
        for i, content in enumerate(test_cases):
            test_content = f"Test {i}\n{'=' * 10}\n{content}"
            app.srcdir.joinpath(f'test{i}.rst').write_text(test_content)
        
        app.build()
        
        # Each test file should build without errors
        for i in range(len(test_cases)):
            html_file = app.outdir / f'test{i}.html'
            assert html_file.exists(), f"Test case {i} should build successfully"
            
            soup = BeautifulSoup(html_file.read_text(), 'html.parser')
            container = soup.select_one('.sft-container')
            assert container, f"Test case {i} should have filter-tabs container"

    @pytest.mark.sphinx('html')
    def test_nested_tabs_compatibility(self, app: SphinxTestApp):
        """Test that nested tabs continue to work."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Windows
    
        Windows instructions:
        
        .. filter-tabs::
        
            .. tab:: Pip
                pip install package
            .. tab:: Conda  
                conda install package
                
    .. tab:: Mac
    
        Mac instructions here.
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Should have multiple filter-tabs containers
        containers = soup.select('.sft-container')
        assert len(containers) >= 2, "Should have nested containers"
        
        # Each should have their own radio groups
        radio_groups = soup.select('input[type="radio"]')
        assert len(radio_groups) >= 3, "Should have radios from both levels"

    @pytest.mark.sphinx('latex')
    def test_pdf_fallback_unchanged(self, app: SphinxTestApp):
        """Test that PDF/LaTeX fallback behavior is preserved."""
        content = """
Test Document
=============

.. filter-tabs::

    General content.

    .. tab:: Python
        Python content
    .. tab:: JavaScript
        JS content
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        # In LaTeX mode, should render as admonitions
        latex_content = (app.outdir / 'test.tex').read_text()
        
        # Should contain admonition-like structures for each tab
        assert 'Python' in latex_content, "Python tab should appear in LaTeX"
        assert 'JavaScript' in latex_content, "JavaScript tab should appear in LaTeX"
        assert 'General content' in latex_content, "General content should appear in LaTeX"


class TestConfigurationOptions:
    """Test that configuration options work as expected."""
    
    @pytest.mark.sphinx('html')
    def test_theming_options(self, app: SphinxTestApp):
        """Test that CSS custom properties are applied."""
        app.config.filter_tabs_tab_highlight_color = '#ff0000'
        app.config.filter_tabs_border_radius = '12px'
        
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        container = soup.select_one('.sft-container')
        
        style = container.get('style', '')
        assert '#ff0000' in style, "Custom highlight color should be applied"
        assert '12px' in style, "Custom border radius should be applied"

    @pytest.mark.sphinx('html')
    def test_accessibility_feature_flag(self, app: SphinxTestApp):
        """Test the accessibility improvement feature flag."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
        
        # Test with flag disabled (should use legacy behavior)
        app.config.filter_tabs_use_improved_accessibility = False
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Should NOT have radiogroup role in legacy mode
        radiogroup = soup.select_one('[role="radiogroup"]')
        assert radiogroup is None, "Legacy mode should not have radiogroup role"
        
        # Legend should be hidden in legacy mode
        legend = soup.select_one('.sft-legend')
        # This test will need updating once we implement the feature flag


# Helper functions for testing
def extract_text_content(element):
    """Extract readable text content from HTML element."""
    if not element:
        return ""
    return ' '.join(element.stripped_strings)


def find_associated_elements(soup, element_id):
    """Find all elements associated with a given ID via ARIA attributes."""
    associated = []
    
    # Find elements that reference this ID
    for attr in ['aria-labelledby', 'aria-describedby', 'aria-controls']:
        referencing = soup.select(f'[{attr}*="{element_id}"]')
        associated.extend(referencing)
    
    return associated


def validate_aria_relationships(soup):
    """Validate that all ARIA relationships point to existing elements."""
    errors = []
    
    for attr in ['aria-labelledby', 'aria-describedby', 'aria-controls']:
        elements = soup.select(f'[{attr}]')
        for element in elements:
            referenced_ids = element.get(attr, '').split()
            for ref_id in referenced_ids:
                if ref_id and not soup.select_one(f'#{ref_id}'):
                    errors.append(f"ARIA attribute {attr} references missing ID: {ref_id}")
    
    return errors


class TestARIARelationships:
    """Test ARIA relationship validity."""
    
    @pytest.mark.sphinx('html')
    def test_aria_relationships_valid(self, app: SphinxTestApp):
        """Test that all ARIA relationships point to existing elements."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python
       :aria-label: Python programming language
       Python content
    .. tab:: JavaScript
       JS content
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Validate all ARIA relationships
        errors = validate_aria_relationships(soup)
        assert not errors, f"ARIA relationship errors: {errors}"

    @pytest.mark.sphinx('html')
    def test_unique_ids(self, app: SphinxTestApp):
        """Test that all IDs are unique across multiple tab groups."""
        content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python
        Python 1
    .. tab:: JavaScript
        JS 1

.. filter-tabs::

    .. tab:: Python  
        Python 2
    .. tab:: JavaScript
        JS 2
"""
        app.srcdir.joinpath('index.rst').write_text(content)
        app.build()
        
        soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
        
        # Collect all IDs
        all_elements_with_ids = soup.select('[id]')
        all_ids = [elem.get('id') for elem in all_elements_with_ids]
        
        # Check for duplicates
        duplicates = [id_val for id_val in set(all_ids) if all_ids.count(id_val) > 1]
        assert not duplicates, f"Duplicate IDs found: {duplicates}"


if __name__ == "__main__":
    # Run specific test categories
    pytest.main([__file__ + "::TestCurrentAccessibility", "-v"])
