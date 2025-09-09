.. only:: html

   .. toctree::
      :maxdepth: 2
      :caption: Contents:
      :hidden:

      installation
      usage
      changelog
      accessibility

.. only:: latex

   .. toctree::
      :maxdepth: 2


======================================
sphinx-filter-tabs: Accessible Filters
======================================

Introduction
============

Welcome to the official documentation for ``sphinx-filter-tabs``.

This Sphinx extension provides a robust, accessible, and JavaScript-free way to create filterable content tabs. It's ideal for documentation that needs to present information for different contexts, such as programming languages, operating systems, or installation methods.

**Key Features:**

**CSS-First Design**: This extension works entirely with CSS and semantic HTML, 
requiring no JavaScript for core functionality. This ensures maximum compatibility,
performance, and reliability across all environments.
* **Accessible:** Full WAI-ARIA compliance
* **Keyboard Navigation:** Arrow keys, Home/End, Enter/Space + Screen reader compatibility
* **Customizable:** Easily theme color directly from your ``conf.py``.
* **Graceful Fallback:** Renders as simple admonitions in non-HTML outputs like PDF/LaTeX.
* **Select default tab:** Choose which tab to show by default.


You can find the project's source code on the `GitHub repository <https://github.com/aputtu/sphinx-filter-tabs>`_.

.. only:: html

   You can also download this documentation as a :download:`PDF file <_downloads/sphinxextension-filtertabs.pdf>`.

.. only:: latex

   Please visit `project webpage for live version <https://aputtu.github.io/sphinx-filter-tabs/>`_.
   In the examples provided in the PDF, all tabs gets listed one by one.

.. only:: latex

   .. include:: installation.rst
   .. include:: usage.rst
   .. include:: changelog.rst
   .. include:: accessibility.rst
