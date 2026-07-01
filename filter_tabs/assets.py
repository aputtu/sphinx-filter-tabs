from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx
from sphinx.locale import get_translation
from sphinx.util import logging

from .constants import SFT_DEFAULT_SELECTOR_COUNT, SFT_INTERACTIVE
from .nodes import FilterTabsNode, split_filter_tab_children

logger = logging.getLogger(__name__)
_ = get_translation("sphinx-filter-tabs")

_THEME_HIGHLIGHT_COLOR = (
    "var(--pst-color-primary, var(--color-brand-primary, var(--color-link, LinkText)))"
)
_THEME_TEXT_COLOR = "var(--pst-color-text-base, var(--color-foreground-primary, inherit))"
_THEME_MUTED_TEXT_COLOR = (
    "var(--pst-color-text-muted, var(--color-foreground-muted, var(--sft-text)))"
)
_THEME_BORDER_COLOR = (
    "var(--pst-color-border, "
    "var(--color-background-border, color-mix(in srgb, currentColor 25%, transparent)))"
)
_THEME_HEADER_BACKGROUND = (
    "var(--pst-color-surface, var(--color-background-secondary, transparent))"
)
_CSS_COLOR_VALUE_RE = re.compile(r"^[#a-zA-Z0-9\s,().%+\-/_]+$")
_CSS_COLOR_FORBIDDEN_RE = re.compile(r"[;{}<>\"\\]|url\s*\(", re.IGNORECASE)
_THEME_MODES = frozenset({"native", "opinionated"})
_FLAVORS = frozenset({"default", "minimal"})


def _css_custom_properties(values: dict[str, str]) -> str:
    lines = [":root {"]
    lines.extend(f"    {name}: {value};" for name, value in values.items())
    lines.append("}")
    return "\n".join(lines)


def _css_panel_visibility(selector_count: int) -> str:
    def selector(index: int) -> str:
        return (
            f'.{SFT_INTERACTIVE} input[type="radio"][data-tab-index="{index}"]'
            f':checked ~ .sft-content > .sft-panel[data-tab-index="{index}"]'
        )

    selectors = ",\n".join(selector(i) for i in range(max(selector_count, 1)))
    return f"/* Panel visibility - generated at build time */\n{selectors} {{\n    display: block;\n}}\n"


def register_static_assets(app: Sphinx) -> None:
    """Register CSS filenames with Sphinx during builder-inited."""
    if app.builder.format != "html":
        return

    static_source = Path(__file__).parent / "static"
    add_static_dir = getattr(app, "add_static_dir", None)
    if callable(add_static_dir):
        add_static_dir(str(static_source))
    elif str(static_source) not in app.config.html_static_path:
        app.config.html_static_path.append(str(static_source))

    app.add_css_file("filter_tabs.css")
    app.add_css_file("filter_tabs_theme.css")


def _is_safe_css_color_value(color: str) -> bool:
    return bool(_CSS_COLOR_VALUE_RE.fullmatch(color)) and not _CSS_COLOR_FORBIDDEN_RE.search(color)


def _configured_highlight_color(app: Sphinx) -> str:
    color = getattr(app.config, "filter_tabs_highlight_color", "auto")
    if color is None:
        return _THEME_HIGHLIGHT_COLOR

    color = str(color).strip()
    if color.lower() in {"", "auto", "theme", "native"}:
        return _THEME_HIGHLIGHT_COLOR

    if not _is_safe_css_color_value(color):
        logger.warning(
            _("filter-tabs: invalid highlight color '{color}'. Reverting to theme color.").format(
                color=color
            )
        )
        return _THEME_HIGHLIGHT_COLOR

    return color


def _configured_choice(app: Sphinx, name: str, default: str, choices: frozenset[str]) -> str:
    value = str(getattr(app.config, name, default)).strip().lower()
    if value in choices:
        return value

    choices_text = ", ".join(sorted(choices))
    logger.warning(
        _(
            "filter-tabs: invalid {name} value '{value}'. "
            "Expected one of: {choices}. Reverting to '{default}'."
        ).format(name=name, value=value, choices=choices_text, default=default),
        type="filter-tabs",
        subtype="config",
    )
    return default


def _selector_count_for_build(env: Any) -> int:
    """Return the largest tab-group size present in the current Sphinx build."""
    selector_count = SFT_DEFAULT_SELECTOR_COUNT
    if env is None or not hasattr(env, "found_docs") or not hasattr(env, "get_doctree"):
        return selector_count

    for docname in sorted(env.found_docs):
        try:
            doctree = env.get_doctree(docname)
        except Exception as exc:
            logger.debug("filter-tabs: could not inspect doctree %s: %s", docname, exc)
            continue

        for node in doctree.findall(FilterTabsNode):
            slots, _general_content = split_filter_tab_children(node.children)
            tab_count = len(slots)
            selector_count = max(selector_count, tab_count)

    return selector_count


def _render_theme_css(app: Sphinx, selector_count: int = SFT_DEFAULT_SELECTOR_COUNT) -> str:
    """Return the generated theme CSS for the current Sphinx configuration."""
    variables = {"--sft-highlight-color": _configured_highlight_color(app)}

    theme_mode = _configured_choice(app, "filter_tabs_theme_mode", "native", _THEME_MODES)
    flavor = _configured_choice(app, "filter_tabs_flavor", "default", _FLAVORS)

    if theme_mode == "native":
        # Native mode: inherit the Sphinx theme's colors where themes expose
        # variables, and otherwise fall back to current text/browser link colors.
        variables.update(
            {
                "--sft-text": _THEME_TEXT_COLOR,
                "--sft-text-muted": _THEME_MUTED_TEXT_COLOR,
                "--sft-bg": "transparent",
                "--sft-header-bg": _THEME_HEADER_BACKGROUND,
                "--sft-tab-active-bg": "transparent",
                "--sft-border": _THEME_BORDER_COLOR,
                "--sft-blockquote-bg": "transparent",
                "--sft-summary-bg": "transparent",
                "--sft-collapsible-accent-color": "var(--sft-highlight-color)",
            }
        )
    else:
        # Opinionated mode: use the classic look instead of theme variables.
        variables.update(
            {
                "--sft-text": "#212529",
                "--sft-text-muted": "#343a40",
                "--sft-bg": "#ffffff",
                "--sft-header-bg": "#f8f9fa",
                "--sft-tab-active-bg": "#ffffff",
                "--sft-border": "#e0e0e0",
            }
        )

    if flavor == "minimal":
        variables.update(
            {
                "--sft-border-radius": "0",
                "--sft-tab-font-size": "0.9em",
            }
        )

    return (
        "/* sphinx-filter-tabs: generated theme — do not edit by hand */\n"
        f"{_css_custom_properties(variables)}\n\n"
        f"{_css_panel_visibility(selector_count)}"
    )


def _write_theme_css(app: Sphinx, env: Any) -> None:
    """Write generated theme CSS before Sphinx calculates asset cache hashes."""
    static_dest = Path(app.outdir) / "_static"
    static_dest.mkdir(parents=True, exist_ok=True)
    theme_file = static_dest / "filter_tabs_theme.css"
    theme_file.write_text(
        _render_theme_css(app, selector_count=_selector_count_for_build(env)),
        encoding="utf-8",
    )


def write_theme_css(app: Sphinx, env: Any) -> None:
    """Write the generated theme CSS before HTML pages are rendered."""
    if app.builder.format != "html":
        return
    _write_theme_css(app, env)
