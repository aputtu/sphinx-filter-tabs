WAI-ARIA Implementation with CSS-First Approach
================================================

Here's how the codebase implements key WAI-ARIA specifications while
maintaining HTML/CSS functionality without JavaScript:

1. **Semantic HTML Foundation**
--------------------------------
* **Uses native form controls** (``<input type="radio">``) that have built-in accessibility
* **Fieldset/Legend structure** provides semantic grouping that screen readers understand natively
* **CSS-only tab switching** via ``:checked`` pseudo-class and sibling selectors - no JS required for core functionality

2. **ARIA Roles (Semantic Clarity)**
------------------------------------
* ``role="radiogroup"`` on fieldset - accurately describes the selection mechanism
* ``role="tabpanel"`` on content panels - correctly identifies them as switchable content views
* ``role="region"`` on container - establishes it as a landmark for easy navigation
* **CSS-first benefit**: These roles are static HTML attributes, work without JS

3. **ARIA Relationships (Connected Experience)**
------------------------------------------------
* ``aria-labelledby`` links panels to their controlling radios
* ``aria-describedby`` connects radios to hidden descriptive text
* Container's ``aria-labelledby`` points to the visible legend
* **CSS-first benefit**: All relationships defined in HTML, no dynamic updates needed

4. **Keyboard Navigation (Native Browser Behavior)**
----------------------------------------------------
* After removing custom JS handlers, uses **native radio button keyboard behavior**:

  * Tab enters/exits the group
  * Arrow keys navigate AND select (native browser handling)

* **CSS-first benefit**: Works entirely through browser's built-in form control behavior

5. **Screen Reader Announcements**
----------------------------------
* Visible, meaningful legend announces the choice context
* Hidden descriptions (``sr-only``) provide additional context per option
* Progressive enhancement: Optional JS adds live region announcements
* **CSS-first benefit**: Core announcements work through HTML structure alone

6. **Focus Management**
-----------------------
* ``tabindex="0"`` on panels makes them focusable
* Visual focus indicators via CSS ``:focus`` pseudo-class
* Optional JS enhancement moves focus to newly visible panel
* **CSS-first benefit**: Focus indicators and tabbability work without JS

7. **Progressive Enhancement Strategy**
---------------------------------------
.. code-block:: text

   Base Layer (HTML/CSS only):
   - Full tab switching functionality
   - Native keyboard navigation
   - Basic screen reader support

   Enhancement Layer (Optional JS):
   - Focus moves to panel after selection
   - Live region announcements
   - NO modification of core behavior

8. **Graceful Degradation**
---------------------------
* Without CSS: Content displays linearly with radio buttons
* Without JS: All core functionality remains intact
* Non-HTML output (LaTeX/PDF): Renders as readable sequential content

Key Design Decision
===================

The implementation makes a conscious trade-off: it uses **radiogroup semantics**
(which some might consider non-standard for tabs) to achieve **perfect
CSS-only functionality**. This prioritizes:

#. **Robustness** over semantic purity
#. **Universal compatibility** over following the exact ARIA tab pattern
#. **Progressive enhancement** over JavaScript dependency

The result is an accessible component that works everywhere, degrades
gracefully, and still provides a good experience for all users including
those with assistive technologies. The semantic "impurity" (using radiogroup
for tab-like behavior) is a reasonable price for bulletproof functionality.