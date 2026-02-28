from __future__ import annotations

import re
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging

from .config import _SFT_HARD_CAP

logger = logging.getLogger(__name__)


def register_static_assets(app: Sphinx) -> None:
    """Register CSS filenames with Sphinx during builder-inited."""
    if app.builder.format != "html":
        return

    # Let Sphinx handle copying by adding the static dir to html_static_path
    # Since assets.py is now inside filter_tabs/, the static folder is its parent's sibling
    # actually wait, it's still in filter_tabs/static if the package is structured right.
    static_source = Path(__file__).parent / "static"
    if str(static_source) not in app.config.html_static_path:
        app.config.html_static_path.append(str(static_source))

    app.add_css_file("filter_tabs.css")
    app.add_css_file("filter_tabs_theme.css")


def write_theme_css(app: Sphinx, exception: Exception | None) -> None:
    """Write the generated theme CSS file after the build completes."""
    if exception is not None:
        return
    if app.builder.format != "html":
        return

    def _selector(i: int) -> str:
        return (
            f'.sft-radio-group input[type="radio"][data-tab-index="{i}"]'
            f':checked ~ .sft-content > .sft-panel[data-tab-index="{i}"]'
        )

    selectors = ",\n".join(_selector(i) for i in range(_SFT_HARD_CAP))
    visibility_block = (
        "/* Panel visibility — generated at build time, scoped with child\n"
        " * combinator (>) to isolate nested tab groups. */\n"
        f"{selectors} {{\n"
        "    display: block;\n"
        "}\n"
    )

    color = app.config.filter_tabs_highlight_color
    # Basic CSS color validation to prevent injection
    if not re.match(r"^#?[a-zA-Z0-9\s,().%]+$", color) or ";" in color or "}" in color:
        logger.warning(
            f"filter-tabs: invalid highlight color '{color}'. "
            "Reverting to default '#007bff' to prevent CSS injection."
        )
        color = "#007bff"

    theme_css = (
        "/* sphinx-filter-tabs: generated theme — do not edit by hand */\n"
        f":root {{ --sft-highlight-color: {color}; }}\n"
        "\n"
        f"{visibility_block}"
    )
    static_dest = Path(app.outdir) / "_static"
    static_dest.mkdir(parents=True, exist_ok=True)
    theme_file = static_dest / "filter_tabs_theme.css"
    theme_file.write_text(theme_css, encoding="utf-8")
