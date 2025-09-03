Usage Example
=============

Examples
--------

Here is a live demonstration of the extension with the new simplified syntax.

.. filter-tabs::

    This is general content visible regardless of the selected filter.
    It's perfect for introductory text or information that applies to
    all tabs.

    .. tab:: Python (default)

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

.. only:: latex

   .. raw:: latex

      \newpage

   Source Code for Examples
   ~~~~~~~~~~~~~~~~~~~~~~~~

   The following RST markup was used to create the above example:

   .. code-block:: rst
      :class: copyable

      .. filter-tabs::

          This is general content visible regardless of the selected
          filter. It's perfect for introductory text or information
          that applies to all tabs.

          .. tab:: Python (default)

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

.. only:: latex

   .. raw:: latex

      \newpage

Using ARIA Labels for Better Accessibility
-------------------------------------------

For improved screen reader support, you can provide descriptive ARIA labels
that give more context than the short visual tab names:

.. filter-tabs::

    Choose your preferred installation method below.

    .. tab:: CLI
       :aria-label: Command Line Interface instructions

        Install using the command line:

        .. code-block:: bash

            # Using pip
            pip install sphinx-filter-tabs

            # Or using pipx for isolated installation
            pipx install sphinx-filter-tabs

    .. tab:: GUI (default)
       :aria-label: Graphical Interface via Anaconda

        Install using **Anaconda Navigator**:

        1. Open Anaconda Navigator
        2. Go to Environments → base (root)
        3. Change dropdown from "Installed" to "All"
        4. Search for ``sphinx-filter-tabs``
        5. Check the checkbox and click "Apply"

        Alternatively, use the Anaconda Prompt:

        .. code-block:: bash

            conda install -c conda-forge sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

   Source Code for ARIA Labels
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   The following RST markup demonstrates the ``:aria-label:`` option:

   .. code-block:: rst
      :class: copyable

      .. filter-tabs::

          Choose your preferred installation method below.

          .. tab:: CLI
             :aria-label: Command Line Interface instructions

              Install using the command line:

              .. code-block:: bash

                  # Using pip
                  pip install sphinx-filter-tabs

                  # Or using pipx for isolated installation
                  pipx install sphinx-filter-tabs

          .. tab:: GUI (default)
             :aria-label: Graphical Interface via Anaconda

              Install using **Anaconda Navigator**:

              1. Open Anaconda Navigator
              2. Go to Environments → base (root)
              3. Change dropdown from "Installed" to "All"
              4. Search for ``sphinx-filter-tabs``
              5. Check the checkbox and click "Apply"

              Alternatively, use the Anaconda Prompt:

              .. code-block:: bash

                  conda install -c conda-forge sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

Providing a Custom Legend
-------------------------

For cases where the auto-generated legend (e.g., "Choose programming language...")
is not specific enough, you can provide a custom title for the entire tab group
using the ``:legend:`` option.

.. only:: latex

   See home page for illustration purposes. 
   This PDF version  does not show output from filter-tab, but tab only.

.. filter-tabs::
   :legend: Select Your Deployment Environment

   .. tab:: Staging (default)

      This panel shows configuration for the **staging** environment.
      It's used for testing before release.

   .. tab:: Production

      This panel shows configuration for the **production** environment.
      This is the live, user-facing setup.


Source Code for Custom Legend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. only:: html
      
      The following RST markup was used to create the above example:

   .. only:: latex

      It is possible to use :legend: to control output instead of
      having tab names included automatically.



   .. code-block:: rst
      :class: copyable

      .. filter-tabs::
         :legend: Select Your Deployment Environment

         .. tab:: Staging (default)

            This panel shows configuration for the **staging** environment.
            It's used for testing before release.

         .. tab:: Production

            This panel shows configuration for the **production** environment.
            This is the live, user-facing setup.

.. only:: latex

   .. raw:: latex

      \newpage

Nested Tabs
-----------

You can nest ``filter-tabs`` directives to create more complex layouts.
Simply indent the inner tab set within a ``tab`` directive of the outer set.

.. filter-tabs::

    .. tab:: Windows (default)

        Windows installation instructions.
        Choose your package manager
        below:

        .. filter-tabs::

            .. tab:: Pip (default)

                Install with **pip** on Windows:

                .. code-block:: powershell

                    # Basic installation
                    pip install sphinx-filter-tabs

                    # Or install with documentation dependencies
                    pip install sphinx-filter-tabs[docs]

            .. tab:: Conda

                Install with **Conda** on Windows:

                .. code-block:: powershell

                    # Install from conda-forge channel
                    conda install -c conda-forge sphinx-filter-tabs

                    # Or using mamba for faster resolution
                    mamba install -c conda-forge sphinx-filter-tabs

    .. tab:: macOS

        macOS installation instructions:

        .. code-block:: bash

            # Using Homebrew Python
            pip3 install sphinx-filter-tabs

            # Or using MacPorts
            sudo port install py-sphinx-filter-tabs

    .. tab:: Linux

        Linux installation instructions:

        .. code-block:: bash

            # Debian/Ubuntu
            sudo apt install python3-sphinx-filter-tabs

            # Or using pip
            pip install --user sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

   Source Code for Nested Tabs
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. code-block:: rst
      :class: copyable

      .. filter-tabs::

          .. tab:: Windows (default)

              Windows installation instructions. Choose your package manager below:

              .. filter-tabs::

                  .. tab:: Pip (default)

                      Install with **pip** on Windows:

                      .. code-block:: powershell

                          # Basic installation
                          pip install sphinx-filter-tabs

                          # Or install with documentation dependencies
                          pip install sphinx-filter-tabs[docs]

                  .. tab:: Conda

                      Install with **Conda** on Windows:

                      .. code-block:: powershell

                          # Install from conda-forge channel
                          conda install -c conda-forge sphinx-filter-tabs

                          # Or using mamba for faster resolution
                          mamba install -c conda-forge sphinx-filter-tabs

          .. tab:: macOS

              macOS installation instructions:

              .. code-block:: bash

                  # Using Homebrew Python
                  pip3 install sphinx-filter-tabs

                  # Or using MacPorts
                  sudo port install py-sphinx-filter-tabs

          .. tab:: Linux

              Linux installation instructions:

              .. code-block:: bash

                  # Debian/Ubuntu
                  sudo apt install python3-sphinx-filter-tabs

                  # Or using pip
                  pip install --user sphinx-filter-tabs
