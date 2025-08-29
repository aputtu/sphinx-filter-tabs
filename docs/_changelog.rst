Changelog
=========

**Version 1.0.0** (Upcoming, we're still in beta)

* **BREAKING CHANGE**: Simplified directive syntax - ``filter-tabs`` no longer requires tab names as arguments
* Tab names and defaults are now defined directly in ``.. tab::`` directives
* Content outside ``.. tab::`` blocks automatically becomes general content
* Added ``:aria-label:`` option to ``tab`` directive for enhanced accessibility
* Improved screen reader support with customizable ARIA labels
* Fixed CSS selector bug that referenced ``.sft-content`` without using constant
* Major refactoring: Static types, better separation of concerns, etc.

**Version 0.9.3**

* Reintroduce doc deploy requirements, but now caching them (GitHub)

**Version 0.9.2**


* Removed duplicate IDs in HTML and resulting W3 validation errors
* Add dev, export, and improved setup scripts
* Reduced doc deploy requirements from 1GB to 50MB

**Version 0.9.0**

* Full WAI-ARIA compliance implemented
* Added keyboard navigation (arrow keys, Home/End, Enter/Space)
* Enhanced screen reader compatibility
* Progressive JavaScript enhancement for better accessibility
* Improved focus management and ARIA state handling
* Refactored extension.py for readability and maintainability

**Version 0.8.0**

* Added keyboard navigation using tab and arrows
* Allowed for nested tabs and included example usage
* Refactor HTML generation according to WAI-ARIA recommendations
* Extended README.md with build and test instructions for developers

**Version 0.7.0**

* Fixed HTML errors

**Version 0.6.0**

* Initial release
