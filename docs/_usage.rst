Usage Example
=============

Here is a live demonstration of the extension.

.. filter-tabs:: Python (default), C++, JavaScript

    ... (rest of your usage example content) ...

Nested Tabs
-----------

You can nest ``filter-tabs`` directives to create more complex layouts. Simply indent the inner tab set within a ``tab`` directive of the outer set.

.. filter-tabs:: Windows (default), macOS, Linux

    .. tab:: Windows

        This is the content for Windows. Here are some platform-specific installation instructions:

        .. filter-tabs:: Pip (default), Conda

            .. tab:: Pip

                Instructions for installing with **Pip** on Windows.

            .. tab:: Conda

                Instructions for installing with **Conda** on Windows.

    .. tab:: macOS

        This is the content for macOS.

    .. tab:: Linux

        This is the content for Linux.
