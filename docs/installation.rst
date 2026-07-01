Installation
============

Installing the Package
----------------------

Install the extension into the same Python environment that runs Sphinx:

.. code-block:: bash

   pip install sphinx-filter-tabs

Enabling the Extension
----------------------

Enable the extension in your Sphinx project's ``conf.py`` file by adding
``"filter_tabs"`` to the ``extensions`` list:

.. code-block:: python

   # conf.py
   extensions = [
       # ... your other extensions ...
       "filter_tabs",
   ]

Optional Configuration
----------------------

The defaults follow the active Sphinx theme. Add these settings to ``conf.py``
only when you want to override that behavior:

.. code-block:: python

   # Theming
   filter_tabs_highlight_color = "auto"     # Use theme colors, or set a CSS color
   filter_tabs_theme_mode = "native"        # Use the active Sphinx theme scheme
   filter_tabs_flavor = "default"           # Use "default" or "minimal"

   # Features
   filter_tabs_enable_collapsible_admonitions = False

   # Development
   filter_tabs_debug_mode = False           # Set True for extension debug logs

``filter_tabs_highlight_color`` accepts ``"auto"`` or a valid CSS color such as
``"#0b5fff"``, ``"rebeccapurple"``, or ``"rgb(0 90 180)"``. Keep ``"auto"`` if
you want the tabs to inherit the theme's default link or brand color.

When ``filter_tabs_enable_collapsible_admonitions`` is set to ``True``,
admonitions with ``:class: sft-collapsible`` render as ``details``/``summary``.
Add ``sft-expanded`` when the section should be open initially.

.. only:: latex

   .. raw:: latex

      \newpage

Verifying Installation
----------------------

To verify that Sphinx can load the extension:

1. Build your documentation from the project root. Replace ``docs`` with your
   source directory if your project uses a different layout:

   .. code-block:: bash

      sphinx-build -b html docs docs/_build/html

2. Check the build output. If the extension is installed and enabled correctly,
   there should be no import warnings for ``filter_tabs``.

3. Add a small tab group to an RST file:

   .. code-block:: rst

      .. filter-tabs::

          .. tab:: Test

              If you see this, it works!

4. Rebuild the docs and open the generated HTML page. The example should render
   as a tab group.
