.. only:: html

   .. toctree::
      :maxdepth: 2
      :caption: Contents:
      :hidden:

      installation
      usage
      accessibility
      release-checklist
      changelog

.. only:: latex

   .. toctree::
      :maxdepth: 2


======================================
sphinx-filter-tabs: Accessible Filters
======================================

Introduction
============

``sphinx-filter-tabs`` adds accessible, filterable content groups to Sphinx
documentation.

Use it when one topic needs short alternatives for different contexts, such as
programming languages, operating systems, deployment environments, or
installation methods.

Key features:

* **CSS-first design:** Uses semantic HTML and CSS; no JavaScript is required
  for the core tab behavior.
* **Accessible structure:** Uses native form controls, legends, labels, and
  ARIA relationships.
* **Keyboard navigation:** Uses browser-native radio button behavior.
* **Theme integration:** Follows the active Sphinx theme by default, with
  optional color and layout settings in ``conf.py``.
* **Opt-in collapsible admonitions:** Can render admonitions marked with
  ``sft-collapsible`` as ``details``/``summary`` when
  ``filter_tabs_enable_collapsible_admonitions`` is enabled.
* **Fallback output:** Renders readable sequential content in non-HTML outputs
  such as PDF and LaTeX.
* **Default tab selection:** Use ``(default)`` in a tab title to choose the
  initially selected tab.


You can find the project's source code on the `GitHub repository <https://github.com/aputtu/sphinx-filter-tabs>`_.

.. only:: html

   You can also download this documentation as a :download:`PDF file <_downloads/sphinxextension-filtertabs.pdf>`.

.. only:: latex

   .. note::

      This PDF is a readable fallback for the HTML documentation. The tab
      groups are listed as sequential sections, so the display is sub-par
      compared with the live HTML version. Visit the
      `project webpage <https://aputtu.github.io/sphinx-filter-tabs/>`_ to see
      the interactive tab controls.

   The HTML extension renders a group of choices and shows one matching content
   panel at a time. This static preview shows the shape of that interface:

   .. raw:: latex

      \begin{center}
      \setlength{\fboxsep}{8pt}
      \fbox{%
      \begin{minipage}{0.88\linewidth}
      \textbf{Choose programming language: Python, C++, JavaScript}\\[0.8em]
      \fbox{\strut \textbf{Python (selected)}}\quad
      \fbox{\strut C++}\quad
      \fbox{\strut JavaScript}\\[0.8em]
      \hrule
      \vspace{0.8em}
      \textbf{Python panel}\\[0.3em]
      \texttt{def hello\_world():}\\
      \hspace*{1.5em}\texttt{print("Hello from Python!")}
      \end{minipage}}
      \end{center}

.. only:: latex

   .. include:: installation.rst
   .. include:: usage.rst
   .. include:: accessibility.rst
   .. include:: release-checklist.rst
   .. include:: changelog.rst
