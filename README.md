# Sphinx Filter Tabs Extension

[![Tests and Docs Deployment](https://github.com/aputtu/sphinx-filter-tabs/actions/workflows/test.yml/badge.svg)](https://github.com/aputtu/sphinx-filter-tabs/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/sphinx-filter-tabs.svg)](https://pypi.org/project/sphinx-filter-tabs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sphinx-filter-tabs.svg)](https://pypi.org/project/sphinx-filter-tabs/)
[![PyPI - License](https://img.shields.io/pypi/l/sphinx-filter-tabs.svg)](https://github.com/aputtu/sphinx-filter-tabs/blob/main/LICENSE)

A robust Sphinx extension for creating accessible, filterable content tabs using pure CSS and semantic HTML.

**📖 View extension and documentation at: https://aputtu.github.io/sphinx-filter-tabs/**

This extension provides `filter-tabs` and `tab` directives to create user-friendly, switchable content blocks. Perfect for showing code examples in multiple languages, installation instructions for different platforms, or any content that benefits from organized, filterable presentation.

## Key Features

- **Pure CSS Implementation:** Zero JavaScript dependencies for maximum compatibility and performance
- **Fully Accessible:** WAI-ARIA compliant with native keyboard navigation and screen reader support
- **Semantic HTML:** Uses standard form controls (radio buttons) for robust, predictable behavior
- **Universal Compatibility:** Works in all environments where CSS is supported, including strict CSP policies
- **Easy Customization:** Theme colors and styling through simple CSS custom properties
- **Multiple Output Formats:** Graceful fallback to sequential content in PDF/LaTeX builds
- **Proven Reliability:** Comprehensive test suite across multiple Python and Sphinx versions

## Quick Start

### Installation

```bash
pip install sphinx-filter-tabs
```

### Enable the Extension

Add to your `conf.py`:

```python
extensions = [
    # ... your other extensions ...
    'filter_tabs.extension',
]
```

### Basic Usage

```rst
.. filter-tabs::

    This content appears above all tabs.

    .. tab:: Python

        Install using pip:

        .. code-block:: bash

            pip install my-package

    .. tab:: Conda (default)

        Install using conda:

        .. code-block:: bash

            conda install my-package

    .. tab:: From Source

        Build from source:

        .. code-block:: bash

            git clone https://github.com/user/repo.git
            cd repo
            pip install -e .
```

## Configuration Options

Add these optional settings to your `conf.py`:

```python
# Customize the active tab highlight color
filter_tabs_highlight_color = '#007bff'  # Default: '#007bff'

# Enable debug logging during development
filter_tabs_debug_mode = False           # Default: False
```

## Advanced Usage

### Custom Legend

Override the auto-generated legend:

```rst
.. filter-tabs::
   :legend: Select Your Installation Method

   .. tab:: Quick Install
      Content here...
```

### ARIA Labels for Accessibility

Provide descriptive labels for screen readers:

```rst
.. filter-tabs::

   .. tab:: CLI
      :aria-label: Command line installation instructions
      
      Content for command line users...
```

### Nested Tabs

Create complex layouts with nested tab groups:

```rst
.. filter-tabs::

   .. tab:: Windows

      Choose your package manager:

      .. filter-tabs::

         .. tab:: Chocolatey
            choco install my-package

         .. tab:: Scoop  
            scoop install my-package
```

## How It Works

This extension uses a **pure CSS architecture** with semantic HTML:

- **Radio buttons** provide the selection mechanism (hidden but accessible)
- **CSS `:checked` selectors** control panel visibility
- **Fieldset/legend** structure provides semantic grouping
- **ARIA attributes** enhance screen reader support
- **Native keyboard navigation** works through standard form controls

This approach ensures:
- **Maximum compatibility** across all browsers and assistive technologies
- **Better performance** with no JavaScript parsing or execution
- **Enhanced security** for environments with strict Content Security Policies
- **Simplified maintenance** with fewer dependencies and potential conflicts

## Browser Support

Works in all modern browsers that support:
- CSS3 selectors (`:checked`, attribute selectors)
- Basic ARIA attributes
- HTML5 form elements

This includes all browsers from the last 10+ years.

## Development

### Quick Setup

```bash
git clone https://github.com/aputtu/sphinx-filter-tabs.git
cd sphinx-filter-tabs
./scripts/setup_dev.sh
```

This creates a virtual environment and builds the documentation.

### Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Build documentation
./scripts/dev.sh html

# Run tests across multiple Sphinx versions
tox

# Clean build and start fresh
./scripts/dev.sh clean-all

# Export project structure for analysis
./scripts/export-project.sh
```

### Testing

The project includes comprehensive tests covering:
- Basic tab functionality and content visibility
- Accessibility features and ARIA compliance
- Nested tabs and complex layouts
- Multiple output formats (HTML, LaTeX)
- Cross-browser compatibility

Tests run automatically on:
- Python 3.10, 3.12
- Sphinx 7.0, 7.4, 8.0, 8.2
- Multiple operating systems via GitHub Actions

## Architecture

The extension consists of three main components:

- **`extension.py`** - Sphinx integration, directives, and node definitions
- **`renderer.py`** - HTML generation and output formatting  
- **`static/filter_tabs.css`** - Pure CSS styling and functionality

This clean separation makes the code easy to understand, test, and maintain.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Submit a pull request

## License

GNU General Public License v3.0. See [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](docs/changelog.rst) for version history and migration notes.

## Support

- **Documentation**: https://aputtu.github.io/sphinx-filter-tabs/
- **Issues**: https://github.com/aputtu/sphinx-filter-tabs/issues
- **PyPI**: https://pypi.org/project/sphinx-filter-tabs/
