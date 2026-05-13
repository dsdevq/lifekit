"""`lifekit init` — copy templates into ~/.life/."""

from __future__ import annotations

import shutil
from pathlib import Path

from .paths import life_root, templates_root


def init_instance(target: Path | None = None, force: bool = False) -> Path:
    """Create a fresh lifekit instance at `target` (default: ~/.life/).

    Returns the target path. Raises FileExistsError if it already exists and
    force=False.
    """
    target = target or life_root()
    if target.exists() and any(target.iterdir()):
        if not force:
            raise FileExistsError(
                f"{target} already exists and is not empty. Pass force=True to overwrite."
            )

    src = templates_root()
    if not src.exists():
        raise RuntimeError(f"Bundled templates not found at {src}")

    target.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=force)
        else:
            shutil.copy2(item, dest)

    # ensure journal/ exists (no template file inside)
    (target / "journal").mkdir(exist_ok=True)
    return target
