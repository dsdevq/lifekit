"""Path resolution for lifekit instances."""

from __future__ import annotations

import os
from pathlib import Path


def life_root() -> Path:
    """Return the user's ~/.life/ directory. Override with LIFEKIT_ROOT env var."""
    override = os.environ.get("LIFEKIT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".life"


def templates_root() -> Path:
    """Return the bundled templates directory inside the installed package."""
    # templates/ is shipped at the package level (see pyproject.toml hatch.build)
    here = Path(__file__).resolve().parent.parent.parent.parent / "templates"
    if here.exists():
        return here
    # fallback when installed: templates packaged inside the wheel
    pkg_templates = Path(__file__).resolve().parent.parent / "_templates"
    return pkg_templates
