Accessibility with Pure CSS Architecture
========================================

``sphinx-filter-tabs`` renders tab-like controls with semantic HTML, a small
set of static ARIA relationships, and CSS. It does not require JavaScript for
the core interaction.

The component intentionally uses a radio group pattern instead of the ARIA
``tablist`` pattern. That keeps the selected state tied to native form controls,
which browsers and assistive technologies already understand.

Semantic HTML Foundation
------------------------

The generated HTML uses:

* native ``<input type="radio">`` controls for selection
* a ``<fieldset>`` and ``<legend>`` to label each tab group
* labels connected to radio inputs with ``for`` and ``id``
* plain content panels referenced by the matching radio controls
* CSS ``:checked`` selectors to show the selected panel

The tab group still works without JavaScript. If CSS is unavailable, the
content remains in the document as normal sequential content.

ARIA Use
--------

The extension does not add ARIA widget roles for the tab group. Radio controls
are grouped by native ``<fieldset>``/``<legend>`` semantics rather than an
explicit ARIA ``radiogroup`` role. Panels are plain content containers rather
than ARIA ``tabpanel`` widgets because the component does not implement the
ARIA ``tablist`` pattern. Static ARIA relationships are generated at build
time. There is no runtime script that updates ARIA state.

ARIA Relationships
------------------

The generated HTML connects controls and content with stable IDs:

* each radio input uses ``aria-controls`` to point to its panel
* each radio input uses ``aria-describedby`` for hidden helper text

The fieldset legend may be visible or visually hidden with ``:hide-legend:``.
In both cases, it remains in the HTML and continues to label the group.

Keyboard Navigation
-------------------

Keyboard behavior comes from native radio buttons:

* ``Tab`` moves focus into and out of the group
* arrow keys move between radio options and update the selected panel
* ``Space`` selects the focused radio option

The exact key behavior can vary slightly by browser and operating system, but
the extension does not replace it with custom JavaScript.

Screen Reader Announcements
---------------------------

Screen readers can use the generated structure to announce:

* the group label from the legend
* each tab option through its radio input and visible label
* optional per-tab context from ``:aria-label:`` and hidden helper text
* the relationship from each control to its panel where ``aria-controls`` is
  exposed by the assistive technology

Use ``:legend:`` when the generated legend is not clear enough. Use
``:aria-label:`` when an individual tab label needs more context than the
visible text provides.

Focus Management
----------------

The extension keeps focus behavior simple:

* the browser manages focus for the radio controls
* CSS focus styles make the active and focused controls visible
* focusable content inside panels keeps its native focus behavior

Because there is no JavaScript focus management, the behavior stays predictable
in restrictive documentation environments.

Pure CSS Architecture Strategy
------------------------------

The HTML and CSS provide the full interaction:

.. code-block:: text

   HTML structure:
   - radio inputs represent choices
   - labels provide clickable tab controls
   - panels contain the tab content

   CSS behavior:
   - the checked radio input determines the active panel
   - generated selectors support the number of tabs used in the build
   - theme variables control colors and spacing

This approach has practical benefits:

* no JavaScript dependency
* compatibility with strict Content Security Policies
* readable fallback output for non-HTML builders
* fewer runtime failure modes

Universal Compatibility
-----------------------

The extension is designed for documentation builds that need to work across
different output formats:

* HTML output renders the interactive radio-based tab group
* LaTeX and PDF output render the content as readable sequential sections
* JavaScript-disabled browsers keep the same tab behavior
* CSS-disabled browsers still expose the content in source order

Design Philosophy
=================

The project favors standard browser behavior over custom interaction code. That
means the component behaves more like a grouped set of choices than a scripted
application widget.

This design is useful for documentation because it:

* keeps examples readable when copied into other Sphinx projects
* avoids JavaScript requirements in locked-down documentation sites
* follows the active Sphinx theme by default
* preserves meaningful output for PDF and other non-HTML builders

There is still an authoring responsibility: keep tab names short, provide a
clear legend, and avoid very large tab groups when a table or separate page
would be easier to scan.

Technical Implementation Details
================================

CSS selector strategy
---------------------

The extension assigns ``data-tab-index`` values to controls and panels. During
the build it writes selectors such as ``[data-tab-index="N"]:checked`` to show
the matching panel. This avoids fragile ``nth-child`` calculations and supports
nested tab groups.

Generated theme CSS
-------------------

The extension writes ``filter_tabs_theme.css`` during the Sphinx build. The
file contains theme variables and panel-visibility selectors sized for the tab
groups in the current build.

Keyboard behavior
-----------------

Keyboard interaction relies on native radio-button behavior. This keeps the
implementation small and avoids browser-specific JavaScript handlers.

Screen reader behavior
----------------------

The output relies on standard form semantics, labels, legends, and ARIA
relationships. The extension does not try to simulate a JavaScript tab widget.

Focus indicators
----------------

The stylesheet uses ``:focus-visible`` and ``:focus-within`` so keyboard users
can see where focus is. These styles use the active theme color unless
``filter_tabs_highlight_color`` is set explicitly.
