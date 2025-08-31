# filter_tabs/parsers.py
"""
Parsing utilities for the sphinx-filter-tabs extension.

This module extracts and centralizes all parsing logic to make it
testable and maintainable.
"""

import re
from typing import Tuple, List
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class TabArgumentParser:
    """
    Parser for tab directive arguments.
    Handles extraction of tab names and detection of default markers.
    """
    
    DEFAULT_PATTERN = re.compile(r"^(.*?)\s*\(\s*default\s*\)$", re.IGNORECASE)
    
    @classmethod
    def parse(cls, argument: str) -> Tuple[str, bool]:
        """
        Parse a tab argument string to extract name and default status.
        """
        logger.debug(f"Parsing tab argument: '{argument}'") # Correct location for the log
        if not argument:
            raise ValueError("Tab argument cannot be empty")
        
        lines = argument.strip().split('\n')
        first_line = lines[0].strip()
        
        if len(lines) > 1:
            logger.debug(
                f"Tab argument contains multiple lines, using only first: '{first_line}'"
            )
        
        match = cls.DEFAULT_PATTERN.match(first_line)
        if match:
            tab_name = match.group(1).strip()
            if not tab_name:
                raise ValueError("Tab name cannot be empty")
            return tab_name, True
        
        return first_line, False


class ContentTypeInferrer:
    # ... (this class is correct, no changes needed) ...
    PATTERNS = [
        (['python', 'javascript', 'java', 'c++', 'rust', 'go', 'ruby', 'php'], 'programming language'),
        (['windows', 'mac', 'macos', 'linux', 'ubuntu', 'debian', 'fedora'], 'operating system'),
        (['pip', 'conda', 'npm', 'yarn', 'cargo', 'gem', 'composer'], 'package manager'),
        (['cli', 'gui', 'terminal', 'command', 'console', 'graphical'], 'interface'),
        (['development', 'staging', 'production', 'test', 'local'], 'environment'),
        (['source', 'binary', 'docker', 'manual', 'automatic'], 'installation method'),
    ]
    
    @classmethod
    def infer_type(cls, tab_names: List[str]) -> str:
        lower_names = [name.lower() for name in tab_names]
        for keywords, content_type in cls.PATTERNS:
            if any(name in keywords for name in lower_names):
                return content_type
        for keywords, content_type in cls.PATTERNS:
            for name in lower_names:
                if any(keyword in name for keyword in keywords):
                    return content_type
        return 'option'


class TabDataValidator:
    # ... (this class is correct, no changes needed) ...
    @staticmethod
    def validate_tabs(tab_data_list: List, skip_empty_check: bool = False) -> None:
        if not tab_data_list and not skip_empty_check:
            raise ValueError(
                "No tab directives found inside filter-tabs. "
                "Add at least one .. tab:: directive."
            )
        names = []
        for tab in tab_data_list:
            name = tab.name if hasattr(tab, 'name') else tab.get('name', '')
            if name in names:
                raise ValueError(
                    f"Duplicate tab name '{name}'. Each tab must have a unique name."
                )
            names.append(name)
            content = tab.content if hasattr(tab, 'content') else tab.get('content', [])
            if not content:
                logger.warning(f"Tab '{name}' has no content.")    
        
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
        
        if default_count > 1:
            logger.warning(
                f"Multiple tabs marked as default: {', '.join(default_names)}. "
                f"Using first default: '{default_names[0]}'"
            )
