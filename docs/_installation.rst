Installation
============

Installing the Package
----------------------

First, install the extension package using pip:

.. code-block:: bash

   pip install sphinx-filter-tabs
      

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

   # Essential theming
   filter_tabs_highlight_color = '#007bff'  # Active tab highlight color
   
   # Development option
   filter_tabs_debug_mode = False           # Enable debug logging

.. only:: latex

   .. raw:: latex

      \newpage

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
