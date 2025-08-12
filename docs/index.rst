#####################################
sphinx-filter-tabs: Accessible Filters
#####################################

Welcome to the official documentation for ``sphinx-filter-tabs``.

This Sphinx extension provides a robust, accessible, and JavaScript-free way to create filterable content tabs. It's ideal for documentation that needs to present information for different contexts, such as programming languages, operating systems, or installation methods.

**Key Features:**

* **No JavaScript:** The filtering is achieved with pure CSS for maximum speed and compatibility.
* **Accessible:** Follows WAI-ARIA best practices for keyboard navigation and screen readers.
* **Customizable:** Easily theme colors and styles directly from your ``conf.py``.
* **Graceful Fallback:** Renders as simple admonitions in non-HTML outputs like PDF/LaTeX.

You can find the project's source code on the `GitHub repository <https://github.com/aputtu/sphinx-filter-tabs>`_.
You can also download this documentation as a :download:`PDF file <sphinx-filter-tabs.pdf>`.

.. _installation:

Installation
============

Install the extension using ``pip``:

.. code-block:: bash

   pip install sphinx-filter-tabs

Then, add it to your Sphinx project's ``conf.py`` file:

.. code-block:: python

   extensions = [
       'filter_tabs.extension',
   ]

.. _usage-example:

Usage Example
=============

Here is a live demonstration of the extension.

.. filter-tabs:: Python (default), C++, JavaScript

    .. tab:: General

        This is general content visible regardless of the selected filter. It's perfect for introductory text or information that applies to all tabs.

    .. tab:: Python

        This panel shows content specific to **Python**.

        .. code-block:: python

           def hello_world():
               print("Hello from Python!")

    .. tab:: C++

        This panel shows content specific to **C++**.

        .. code-block:: cpp

           #include <iostream>

           int main() {
               std::cout << "Hello from C++!" << std::endl;
               return 0;
           }

    .. tab:: JavaScript

        This panel shows content specific to **JavaScript**.

        .. code-block:: javascript

           function helloWorld() {
               console.log("Hello from JavaScript!");
           }

You can also create filters for other contexts, like operating systems:

.. filter-tabs:: Windows (default), macOS, Linux

    .. tab:: Windows

        Instructions for **Windows** users.

    .. tab:: macOS

        Instructions for **macOS** users.

    .. tab:: Linux

        Instructions for **Linux** users.
