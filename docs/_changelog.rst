Changelog
=========


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

Changed
^^^^^^^
* Majorly refactored the entire codebase for simplicity and maintainability.
* Simplified configuration options down to the essentials.
* Improved error messages for missing tabs.

Added
^^^^^
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
