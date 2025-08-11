# Sphinx Filter Tabs Extension

A robust Sphinx extension for creating accessible, JavaScript-free, filterable content tabs.

This extension provides `filter-tabs` and `tab` directives to create user-friendly, switchable content blocks, ideal for showing code examples in multiple languages or instructions for different platforms.

## Features

- **Intuitive Directives:** Use `.. filter-tabs::` and `.. tab::` to create tabbed sections.
- **No JavaScript:** Pure CSS implementation ensures maximum compatibility, speed, and accessibility.
- **WAI-ARIA Compliant:** The generated HTML follows accessibility best practices for keyboard navigation and screen readers.
- **Highly Customizable:** Easily theme colors, fonts, and sizes directly from your `conf.py` using CSS Custom Properties.
- **Graceful Fallback:** Renders content as simple admonitions in non-HTML outputs like PDF/LaTeX.
- **Debug Mode:** An optional mode to help authors troubleshoot their markup.

## Installation

```bash
pip install sphinx-filter-tabs
