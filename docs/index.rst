#########################################
Welcome to Sphinx Extension - Filter Tabs
#########################################

This is a demonstration of the ``sphinx-filter-tabs`` extension.

.. filter-tabs:: Windows, macOS(default), Linux

    .. tab:: General

        This is general content visible on all platforms.

    .. tab:: Windows

        This is content specific to **Windows**.

    .. tab:: macOS

        This is content specific to **macOS**.

    .. tab:: Linux

        This is content specific to **Linux**.

.. admonition:: This is a collapsible section
   :class: collapsible

   You can put any content inside a collapsible admonition.

.. admonition:: This one is expanded by default
   :class: collapsible, expanded

   This content is visible immediately on page load.
