Changelog
=========

Version 1.4.0 (2026-02-25)
---------------------------

**Code quality & tooling**

* Deleted dead ``renderer.py`` module. ``FilterTabsRenderer`` was never
  instantiated and imported a non-existent ``TabData`` class. All rendering
  logic lives in ``extension.py``.
* Modernised type annotations throughout ``extension.py``: replaced
  ``typing.List``/``Dict``/``Optional`` with built-in generics (PEP 585)
  and ``X | None`` (PEP 604); annotated the previously bare ``app_config``
  parameter with ``sphinx.config.Config``; added missing ``-> None`` return
  annotation on ``setup_collapsible_admonitions``; moved ``import re`` to
  module level; fixed ``raise ... from e`` (B904) in ``TabDirective.run``.
* Added ``mypy`` static type checking. Configuration lives in
  ``[tool.mypy]`` in ``pyproject.toml`` with targeted overrides for
  Sphinx's incomplete stubs. A ``mypy`` tox environment and CI step are
  included.
* Added ``ruff`` for linting and formatting. Configuration lives in
  ``[tool.ruff]`` in ``pyproject.toml``. A ``lint`` tox environment runs
  ``ruff check`` and ``ruff format --check``. A ``.pre-commit-config.yaml``
  is provided for local use. The ``lint`` CI job gates the test matrix.
* Expanded test suite from 16 to 31 tests, covering: ``_parse_tab_argument``
  edge cases, ``_validate_slots`` warnings (duplicate names, empty content,
  multiple defaults), ``tab``-outside-context error, all three
  ``_infer_content_type`` paths, collapsible admonitions (collapsed,
  expanded, no-title, non-HTML builder), and ``_write_theme_css`` warn/cap
  thresholds.
* Replaced ``black`` with ``ruff`` + ``mypy`` + ``types-docutils`` in
  ``requirements/dev.txt``; pinned docs Sphinx to ``>=9.1`` in
  ``requirements/docs.txt``; consolidated CI dependency installation to
  use requirements files.
* Fixed ``docs/conf.py``: use ``Path``-based ``sys.path`` manipulation,
  read ``release`` from ``importlib.metadata``, add ``intersphinx``
  mappings for Python and Sphinx, set ``filter_tabs_debug_mode = False``
  for production docs.
* Added ``NodeVisitorFunc`` type alias; applied to ``_visit_skip_node``,
  ``_depart_noop``, and the ``VisitorPair`` tuple in ``setup()``.

Version 1.3.1 (2026-02-19)
---------------------------

**Bug fixes**

* Removed ``improve_inline_formatting`` event handler, which incorrectly added
  redundant ``aria-label`` attributes to every ``<strong>`` and ``<em>`` element
  sitewide, causing screen readers to double-announce text.
* Fixed the CSS panel-visibility selectors to use the child combinator (``>``)
  between ``.sft-content`` and ``.sft-panel``. The previous descendant combinator
  caused outer group ``checked`` selectors to bleed into nested groups, showing
  inner panels regardless of their own radio state.

**Improvements**

* Removed the hard 10-tab limit. The panel-visibility selector block is now
  generated at build time, sized exactly to the maximum tab count used in the
  build. Groups above 15 tabs emit a warning; groups above 20 emit an error and
  are capped.
* Replaced per-container inline ``style`` attributes with a generated
  ``filter_tabs_theme.css`` file, keeping ``--sft-highlight-color`` as a proper
  ``:root`` CSS custom property rather than per-element inline style.
* Moved ``app.add_css_file()`` inside the ``builder-inited`` event behind a
  format check, so CSS is never registered for LaTeX and other non-HTML builders.
* Replaced deprecated ``env.app`` access in directives with a builder name
  cached in ``env`` during ``builder-inited``, eliminating the
  ``RemovedInSphinx11Warning`` suppression workaround.
* Added explicit LaTeX skip-visitors for all custom nodes, preventing silent
  failures if they appear outside expected code paths.
* Fixed hover and focus tints to use ``color-mix()`` against
  ``--sft-highlight-color`` rather than hardcoded ``rgba(0, 123, 255, …)``
  values that did not follow user colour customisation.
* Added ``__all__ = ['setup']`` to ``extension.py`` to declare the public API.

**Documentation**

* Added a 12-tab *Large Tab Groups* example to the usage page demonstrating
  realistic many-language SDK installation instructions.

Version 1.3.0 (2026-02-06)
--------------------------

**Compatibility & Infrastructure**

* **Added Official Support for Sphinx 9.0 and 9.1**: Updated dependency constraints and testing matrix to ensure full compatibility with the latest Sphinx releases.
* **Added Python 3.13 Support**: Verified compatibility and updated package classifiers.
* **Future-Proofing**: Resolves `RemovedInSphinx11Warning` by refactoring configuration access to use `env.config` and safely handling builder checks.

**Development**

* Optimized `tox` configuration for parallel testing.
* Improved `export-project.sh` script to robustly exclude virtual environments and build artifacts.


Version 1.2.6 (2025-09-09)
---------------------------

**Architecture Change**: Transition to CSS-Only Implementation

- **BREAKING**: Removed JavaScript file and all JS-dependent functionality
- Fixed panel visibility issues through improved CSS selector approach
- Enhanced accessibility with native form control behavior
- Simplified maintenance by eliminating JavaScript dependencies
- Improved compatibility with restrictive environments (CSP, JS-disabled)


Version 1.2.5 (2025-09-04)
--------------------------

Bump version

Version 1.2.4 (2025-09-03)
--------------------------

Configuration to automate and simplify release process.


Version 1.2.3 (2025-09-03)
--------------------------
This commit addresses several issues found during accessibility audit.

* ARIA Role Correction: The role for content panels has been corrected
  from `region` to the more accurate `tabpanel` to better align with
  WAI-ARIA patterns for tabbed interfaces.
* Native Keyboard Navigation: Custom JavaScript keyboard handlers for*
  arrow keys have been removed. The component now relies entirely on the 
  native, predictable browser behavior for `radiogroup` navigation, 
  simplifying the code and improving the user experience.
* Valid HTML Output: Dynamic CSS generation has been refactored to 
  resolve W3C validation errors. Inline `<style>` blocks are no longer
  injected into the body. Instead, CSS rules are collected and added to
  the document `<head>` via the `html-page-context` Sphinx event.
* Accessibility Documentation: A new document, `_accessibility.rst`, has
  been added. This file details the extension's accessibility
  implementation strategy and explains the conscious design choice
  to use the robust `radiogroup` pattern to ensure CSS-first functionality.

Version 1.2.2 (2025-09-01)
--------------------------

* Remove obsolete scripts complete_cleanup.sh and test_cleanup.sh
* Improve export-project.sh, which now exclude dist and .pytest_cache


Version 1.2.1 (2025-09-01)
--------------------------

Fixes multiple issues from code review, improving test 
robustness, documentation accuracy, and CI stability.


Version 1.2.0 (2025-08-31)
--------------------------

First Production/Stable release.

* No-breaking refactoring for easier maintainability
* Consolidated six Python files into two, and reduced lines of code
* extension.py: All Sphinx integration and output generation in one place
* static/: UI functionality unchanged


Version 1.1.0b (2025-08-30)
---------------------------

**Changed**

* Majorly refactored the entire codebase for simplicity and maintainability.
* Simplified configuration options down to the essentials.
* Improved error messages for missing tabs.

**Added**

* Added focus management to panels via JavaScript for better accessibility.
* Added more detailed debug logging.


Version 1.0.0b (2025-08-27)
---------------------------

* **BREAKING CHANGE**: Simplified directive syntax - ``filter-tabs`` no longer requires tab names as arguments
* Tab names and defaults are now defined directly in ``.. tab::`` directives
* Content outside ``.. tab::`` blocks automatically becomes general content
* Added ``:aria-label:`` option to ``tab`` directive for enhanced accessibility
* Improved screen reader support with customizable ARIA labels
* Fixed CSS selector bug that referenced ``.sft-content`` without using constant
* Major refactoring: Static types, better separation of concerns, etc.


Version 0.9.3b (2025-08-22)
---------------------------

* Reintroduce doc deploy requirements, but now caching them (GitHub)


Version 0.9.2b (2025-08-21)
---------------------------

* Removed duplicate IDs in HTML and resulting W3 validation errors
* Add dev, export, and improved setup scripts
* Reduced doc deploy requirements from 1GB to 50MB


Version 0.9.0b (2025-08-20)
---------------------------

* Full WAI-ARIA compliance implemented
* Added keyboard navigation (arrow keys, Home/End, Enter/Space)
* Enhanced screen reader compatibility
* Progressive JavaScript enhancement for better accessibility
* Improved focus management and ARIA state handling
* Refactored extension.py for readability and maintainability


Version 0.8.0b (2025-08-15)
---------------------------

* Added keyboard navigation using tab and arrows
* Allowed for nested tabs and included example usage
* Refactor HTML generation according to WAI-ARIA recommendations
* Extended README.md with build and test instructions for developers


Version 0.7.0b (2025-08-13)
---------------------------

* Fixed HTML errors


Version 0.6.0b (2025-08-11)
---------------------------

* Initial release
