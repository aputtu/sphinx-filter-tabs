Usage Examples
==============

Examples
--------

This example shows the basic ``filter-tabs`` and ``tab`` syntax.

.. filter-tabs::

    This is general content visible regardless of the selected filter.
    Use it for introductory text or instructions that apply to every tab.

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
          filter. Use it for introductory text or instructions that
          apply to every tab.

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
------------------------------------------

Use ``:aria-label:`` when a short visible tab name needs more context for
screen reader users.

The ``:aria-label:`` option does not change the visible tab labels or the
visible legend above the tabs. It is added to each tab's hidden radio input, so
assistive technology can announce a more descriptive control name than the
short label shown on screen.

In the example below, the visible legend is still generated automatically from
the tab names. ``CLI`` and ``GUI`` match the built-in ``interface`` category, so
the extension renders the legend as ``Choose interface: CLI, GUI``. The
``(default)`` marker only selects the initially active tab; it is removed from
the visible tab name before the legend is generated.

.. filter-tabs::

    Choose your preferred installation method below.

    .. tab:: CLI
       :aria-label: Command Line Interface instructions

        Install using the command line:

        .. code-block:: bash

            python -m pip install sphinx-filter-tabs

    .. tab:: GUI (default)
       :aria-label: Graphical interface instructions for an editor or IDE

        Install from your editor or IDE package manager:

        1. Select the Python environment that builds your Sphinx project.
        2. Search PyPI packages for ``sphinx-filter-tabs``.
        3. Install the package.
        4. Rebuild the documentation.

        If your editor opens an integrated terminal, this command is
        equivalent:

        .. code-block:: bash

            python -m pip install sphinx-filter-tabs

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

                  python -m pip install sphinx-filter-tabs

          .. tab:: GUI (default)
             :aria-label: Graphical interface instructions for an editor or IDE

              Install from your editor or IDE package manager:

              1. Select the Python environment that builds your Sphinx project.
              2. Search PyPI packages for ``sphinx-filter-tabs``.
              3. Install the package.
              4. Rebuild the documentation.

              If your editor opens an integrated terminal, this command is
              equivalent:

              .. code-block:: bash

                  python -m pip install sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

Providing a Custom Legend
-------------------------

By default, the extension creates a visible legend from the tab names. For
example, tabs named ``Staging`` and ``Production`` match the built-in
``environment`` category and would produce ``Choose environment: Staging,
Production``.

When that generated text is not the clearest label for the group, provide an
explicit visible legend with the ``:legend:`` option. This is different from
``:aria-label:``: ``:legend:`` changes the visible group label for everyone,
while ``:aria-label:`` changes the accessible name of an individual hidden tab
control.

.. only:: latex

   In PDF output, tab groups are rendered as sequential sections. The live HTML
   documentation shows the interactive tab group.

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

      Use ``:legend:`` when the generated legend is not the clearest label for
      the tab group.



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

Hiding the Visible Legend
-------------------------

Some pages already introduce the tab context in nearby prose or headings. In
those cases, add ``:hide-legend:`` to keep the tab group visually compact while
preserving the semantic ``<legend>`` for assistive technology.

.. filter-tabs::
   :legend: Choose operating system for install commands
   :hide-legend:

   .. tab:: Windows

      Install from PowerShell:

      .. code-block:: powershell

         pip install sphinx-filter-tabs

   .. tab:: macOS

      Install from Terminal:

      .. code-block:: bash

         python3 -m pip install sphinx-filter-tabs

   .. tab:: Linux

      Install from a shell:

      .. code-block:: bash

         python3 -m pip install sphinx-filter-tabs

Source Code for Hidden Legend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following RST markup was used to create the compact tab group above:

.. code-block:: rst
   :class: copyable

   .. filter-tabs::
      :legend: Choose operating system for install commands
      :hide-legend:

      .. tab:: Windows

         Install from PowerShell:

         .. code-block:: powershell

            pip install sphinx-filter-tabs

      .. tab:: macOS

         Install from Terminal:

         .. code-block:: bash

            python3 -m pip install sphinx-filter-tabs

      .. tab:: Linux

         Install from a shell:

         .. code-block:: bash

            python3 -m pip install sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

Nested Tabs
-----------

You can nest ``filter-tabs`` directives to create more complex layouts.
Indent the inner tab group inside a ``tab`` directive of the outer group.

.. filter-tabs::

    .. tab:: Windows (default)

        Windows installation instructions. Choose the command that matches
        your Python launcher:

        .. filter-tabs::

            .. tab:: py launcher (default)

                Install with the Windows ``py`` launcher:

                .. code-block:: powershell

                    py -m pip install sphinx-filter-tabs

            .. tab:: python command

                Install with the active ``python`` command:

                .. code-block:: powershell

                    python -m pip install sphinx-filter-tabs

    .. tab:: macOS

        macOS installation instructions:

        .. code-block:: bash

            # Using Homebrew Python
            python3 -m pip install sphinx-filter-tabs

    .. tab:: Linux

        Linux installation instructions:

        .. code-block:: bash

            python3 -m pip install --user sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

   Source Code for Nested Tabs
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. code-block:: rst
      :class: copyable

      .. filter-tabs::

          .. tab:: Windows (default)

              Windows installation instructions. Choose the command that matches
              your Python launcher:

              .. filter-tabs::

                  .. tab:: py launcher (default)

                      Install with the Windows ``py`` launcher:

                      .. code-block:: powershell

                          py -m pip install sphinx-filter-tabs

                  .. tab:: python command

                      Install with the active ``python`` command:

                      .. code-block:: powershell

                          python -m pip install sphinx-filter-tabs

          .. tab:: macOS

              macOS installation instructions:

              .. code-block:: bash

                  # Using Homebrew Python
                  python3 -m pip install sphinx-filter-tabs

          .. tab:: Linux

              Linux installation instructions:

              .. code-block:: bash

                  python3 -m pip install --user sphinx-filter-tabs

.. only:: latex

   .. raw:: latex

      \newpage

Large Tab Groups
----------------

There is no fixed 10-tab limit. The panel-visibility CSS is generated at build
time and scales to the tab groups used in each build. The following example
shows 12 tabs, which is realistic for a library that ships official clients for
many languages.

.. note::

   Tab groups above 15 will trigger a build warning encouraging you to
   consider restructuring. The generated CSS scales to the largest tab group
   in the build, but for truly large sets of alternatives a :rst:dir:`toctree`
   or a comparison table is usually a better fit.

.. filter-tabs::
   :legend: Install the client library for your language

   .. tab:: Python (default)

      .. code-block:: bash

         pip install acme-client

   .. tab:: JavaScript

      .. code-block:: bash

         npm install acme-client

   .. tab:: TypeScript

      .. code-block:: bash

         npm install acme-client
         # Type declarations are bundled; no @types package needed.

   .. tab:: Go

      .. code-block:: bash

         go get github.com/acme/acme-client-go

   .. tab:: Rust

      .. code-block:: toml

         # Cargo.toml
         [dependencies]
         acme-client = "1.0"

   .. tab:: Java

      .. code-block:: xml

         <!-- pom.xml -->
         <dependency>
           <groupId>com.acme</groupId>
           <artifactId>acme-client</artifactId>
           <version>1.0.0</version>
         </dependency>

   .. tab:: Kotlin

      .. code-block:: kotlin

         // build.gradle.kts
         implementation("com.acme:acme-client:1.0.0")

   .. tab:: C#

      .. code-block:: bash

         dotnet add package Acme.Client

   .. tab:: Ruby

      .. code-block:: bash

         gem install acme-client

   .. tab:: PHP

      .. code-block:: bash

         composer require acme/acme-client

   .. tab:: Swift

      .. code-block:: swift

         // Package.swift
         .package(url: "https://github.com/acme/acme-client-swift", from: "1.0.0")

   .. tab:: Elixir

      .. code-block:: elixir

         # mix.exs
         {:acme_client, "~> 1.0"}

.. only:: latex

   .. raw:: latex

      \newpage

   Source Code for Large Tab Groups
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. code-block:: rst
      :class: copyable

      .. filter-tabs::
         :legend: Install the client library for your language

         .. tab:: Python (default)

            .. code-block:: bash

               pip install acme-client

         .. tab:: JavaScript

            .. code-block:: bash

               npm install acme-client

         .. tab:: TypeScript

            .. code-block:: bash

               npm install acme-client

         .. tab:: Go

            .. code-block:: bash

               go get github.com/acme/acme-client-go

         .. tab:: Rust

            .. code-block:: toml

               [dependencies]
               acme-client = "1.0"

         .. tab:: Java

            .. code-block:: xml

               <dependency>
                 <groupId>com.acme</groupId>
                 <artifactId>acme-client</artifactId>
                 <version>1.0.0</version>
               </dependency>

         .. tab:: Kotlin

            .. code-block:: kotlin

               implementation("com.acme:acme-client:1.0.0")

         .. tab:: C#

            .. code-block:: bash

               dotnet add package Acme.Client

         .. tab:: Ruby

            .. code-block:: bash

               gem install acme-client

         .. tab:: PHP

            .. code-block:: bash

               composer require acme/acme-client

         .. tab:: Swift

            .. code-block:: swift

               .package(url: "https://github.com/acme/acme-client-swift", from: "1.0.0")

         .. tab:: Elixir

            .. code-block:: elixir

               {:acme_client, "~> 1.0"}
