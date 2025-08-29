# filter_tabs/parsers.py
"""
Parsing utilities for the sphinx-filter-tabs extension.

This module extracts and centralizes all parsing logic to make it
testable and maintainable.
"""

import re
from typing import Tuple, Optional, List
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class TabArgumentParser:
    """
    Parser for tab directive arguments.
    
    Handles extraction of tab names and detection of default markers.
    """
    
    # Pattern to match "(default)" marker in any case
    DEFAULT_PATTERN = re.compile(r"^(.*?)\s*\(\s*default\s*\)$", re.IGNORECASE)
    
    @classmethod
    def parse(cls, argument: str) -> Tuple[str, bool]:
        """
        Parse a tab argument string to extract name and default status.
        
        Args:
            argument: The raw argument string from the tab directive
            
        Returns:
            Tuple of (tab_name, is_default)
            
        Examples:
            >>> TabArgumentParser.parse("Python")
            ('Python', False)
            >>> TabArgumentParser.parse("JavaScript (default)")
            ('JavaScript', True)
            >>> TabArgumentParser.parse("C++ (DEFAULT)")
            ('C++', True)
        """
        if not argument:
            raise ValueError("Tab argument cannot be empty")
        
        # Handle multi-line arguments (only use first line)
        lines = argument.strip().split('\n')
        first_line = lines[0].strip()
        
        if len(lines) > 1:
            logger.debug(
                f"Tab argument contains multiple lines, using only first: '{first_line}'"
            )
        
        # Check for default marker
        match = cls.DEFAULT_PATTERN.match(first_line)
        if match:
            tab_name = match.group(1).strip()
            if not tab_name:
                raise ValueError("Tab name cannot be empty")
            return tab_name, True
        
        # No default marker found
        return first_line, False


class ContentTypeInferrer:
    """
    Infers content type from tab names for better accessibility labels.
    
    This helps generate more meaningful legend text based on common patterns.
    """
    
    # Common patterns and their content types
    PATTERNS = [
        # Programming languages
        (['python', 'javascript', 'java', 'c++', 'rust', 'go', 'ruby', 'php'],
         'programming language'),
        
        # Operating systems
        (['windows', 'mac', 'macos', 'linux', 'ubuntu', 'debian', 'fedora'],
         'operating system'),
        
        # Package managers
        (['pip', 'conda', 'npm', 'yarn', 'cargo', 'gem', 'composer'],
         'package manager'),
        
        # Interface types
        (['cli', 'gui', 'terminal', 'command', 'console', 'graphical'],
         'interface'),
        
        # Environments
        (['development', 'staging', 'production', 'test', 'local'],
         'environment'),
        
        # Installation methods
        (['source', 'binary', 'docker', 'manual', 'automatic'],
         'installation method'),
    ]
    
    @classmethod
    def infer_type(cls, tab_names: List[str]) -> str:
        """
        Infer the content type from tab names.
        
        Args:
            tab_names: List of tab names to analyze
            
        Returns:
            A descriptive content type string
        """
        # Convert all names to lowercase for comparison
        lower_names = [name.lower() for name in tab_names]
        
        # Check each pattern
        for keywords, content_type in cls.PATTERNS:
            if any(name in keywords for name in lower_names):
                return content_type
        
        # Check for partial matches
        for keywords, content_type in cls.PATTERNS:
            for name in lower_names:
                if any(keyword in name for keyword in keywords):
                    return content_type
        
        # Default fallback
        return 'option'


class TabDataValidator:
    """
    Validates tab data to ensure consistency and catch errors early.
    """
    
    @staticmethod
    def validate_tabs(tab_data_list: List) -> None:
        """
        Validate a list of tab data.
        
        Args:
            tab_data_list: List of TabData objects or dictionaries
            
        Raises:
            ValueError: If validation fails
        """
        if not tab_data_list:
            raise ValueError(
                "No tab directives found inside filter-tabs. "
                "Add at least one .. tab:: directive."
            )
        
        # Check for duplicate names
        names = []
        for tab in tab_data_list:
            name = tab.name if hasattr(tab, 'name') else tab.get('name', '')
            if name in names:
                raise ValueError(
                    f"Duplicate tab name '{name}'. "
                    "Each tab must have a unique name."
                )
            names.append(name)

            content = tab.content if hasattr(tab, 'content') else tab.get('content', [])
            if not content:
                logger.warning(f"Tab '{name}' has no content.")    
        
        # Count defaults
        default_count = 0
        default_names = []
        for tab in tab_data_list:
            is_default = (
                tab.is_default if hasattr(tab, 'is_default') 
                else tab.get('is_default', False)
            )
            if is_default:
                default_count += 1
                name = tab.name if hasattr(tab, 'name') else tab.get('name', '')
                default_names.append(name)
        
        # Warn about multiple defaults (don't error, just use first)
        if default_count > 1:
            logger.warning(
                f"Multiple tabs marked as default: {', '.join(default_names)}. "
                f"Using first default: '{default_names[0]}'"
            )
