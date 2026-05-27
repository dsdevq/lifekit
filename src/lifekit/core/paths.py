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


def state_dir() -> Path:
    """Return the lifekit runtime-state directory (queue.jsonl, orchestrator.sqlite, etc.).

    Knowledge (domains, journal, system, sources) lives under life_root(); runtime state
    is XDG-separated so the knowledge vault stays clean. Resolution order:
      1. LIFEKIT_STATE_DIR env var
      2. $XDG_STATE_HOME/lifekit
      3. ~/.local/state/lifekit
    """
    override = os.environ.get("LIFEKIT_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / "lifekit"
    return Path.home() / ".local" / "state" / "lifekit"


def templates_root() -> Path:
    """Return the bundled templates directory inside the installed package."""
    # templates/ is shipped at the package level (see pyproject.toml hatch.build)
    here = Path(__file__).resolve().parent.parent.parent.parent / "templates"
    if here.exists():
        return here
    # fallback when installed: templates packaged inside the wheel
    pkg_templates = Path(__file__).resolve().parent.parent / "_templates"
    return pkg_templates
