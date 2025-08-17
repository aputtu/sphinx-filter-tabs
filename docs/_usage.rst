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
