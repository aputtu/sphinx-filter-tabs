Installation
============

Installing the Package
----------------------

First, install the extension package using pip:

.. code-block:: bash

   pip install sphinx-filter-tabs

Or if you're using conda:

.. code-block:: bash

   conda install -c conda-forge sphinx-filter-tabs

Enabling the Extension
----------------------

After installation, you must enable the extension in your Sphinx project's 
``conf.py`` file. Add ``'filter_tabs.extension'`` to your ``extensions`` list:

.. code-block:: python

   # conf.py
   extensions = [
       # ... your other extensions ...
       'filter_tabs.extension',
   ]

Optional Configuration
----------------------

You can customize the extension's appearance by adding these optional settings 
to your ``conf.py``:

.. code-block:: python

   # Theming options
   filter_tabs_tab_highlight_color = '#007bff'  # Active tab highlight
   filter_tabs_tab_background_color = '#f0f0f0'  # Tab bar background
   filter_tabs_tab_font_size = '1em'            # Tab text size
   filter_tabs_border_radius = '8px'            # Container corners
   
   # Accessibility options
   filter_tabs_keyboard_navigation = True       # Enable arrow key navigation
   filter_tabs_announce_changes = True          # Screen reader announcements
   
   # Other options
   filter_tabs_collapsible_enabled = True       # Enable collapsible sections
   filter_tabs_debug_mode = False               # Debug logging

Verifying Installation
----------------------

To verify the extension is properly installed and loaded:

1. Build your documentation:

   .. code-block:: bash

      sphinx-build -b html docs docs/_build/html

2. Check for any errors in the output. If the extension loads correctly, 
   you should see no warnings about ``filter_tabs``.

3. Try using the directive in an RST file:

   .. code-block:: rst

      .. filter-tabs::

          .. tab:: Test

              If you see this, it works!
