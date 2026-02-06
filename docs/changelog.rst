Changelog
=========

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
* Consolidated six Python files into three, and reduced lines of code
* extension.py: All Sphinx integration concerns in one place
* renderer.py: All output generation logic consolidated
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
