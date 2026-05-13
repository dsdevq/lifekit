"""Tests for the morning brief composer."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from lifekit.core.init import init_instance
from lifekit.routines.morning_brief import _section, render


def test_section_finds_h2(tmp_path: Path) -> None:
    text = "## A\nbody A\n\n## B\nbody B"
    assert _section(text, "A", level=2) == "body A"
    assert _section(text, "B", level=2) == "body B"


def test_section_finds_h3_stops_at_h2(tmp_path: Path) -> None:
    text = "## Top\n### Sub1\nbody1\n### Sub2\nbody2\n## Other\nz"
    top = _section(text, "Top", level=2)
    assert "### Sub1" in top
    assert "## Other" not in top
    sub1 = _section(top, "Sub1", level=3)
    assert sub1 == "body1"
    sub2 = _section(top, "Sub2", level=3)
    assert sub2 == "body2"


def test_section_h3_does_not_leak_into_sibling(tmp_path: Path) -> None:
    text = "### A\naaa\n### B\nbbb"
    assert _section(text, "A", level=3) == "aaa"
    assert _section(text, "B", level=3) == "bbb"


def test_render_uses_real_template(tmp_path: Path) -> None:
    """Initialised instance produces a non-empty brief with no raw `###` leaks."""
    target = tmp_path / "life"
    init_instance(target=target)
    out = render(today=dt.date(2026, 5, 13), root=target)
    assert out.startswith("# Morning brief")
    # the templates have placeholder content, so the brief should mention it
    # without leaking raw markdown subheaders
    assert "### Goals" not in out
    assert "### Preferences" not in out
