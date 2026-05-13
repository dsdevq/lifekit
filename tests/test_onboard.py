"""Tests for `lifekit onboard`."""

from __future__ import annotations

from pathlib import Path

import pytest

from lifekit.core.init import init_instance
from lifekit.core.onboard import onboard


def test_onboard_refuses_when_source_missing(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    missing = tmp_path / "nonexistent.md"
    with pytest.raises(FileNotFoundError, match="source not found"):
        onboard(target=target, source=missing)


def test_onboard_refuses_when_target_missing(tmp_path: Path) -> None:
    target = tmp_path / "nope"
    src = tmp_path / "ctx.md"
    src.write_text("hello")
    with pytest.raises(FileNotFoundError, match="no lifekit instance"):
        onboard(target=target, source=src)


def test_onboard_refuses_populated_without_force(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    # mark a domain as populated by replacing the TODO sentinel
    f = target / "domains" / "career.md"
    f.write_text(f.read_text().replace("last_updated: TODO", "last_updated: 2026-05-13"))

    src = tmp_path / "ctx.md"
    src.write_text("user context")

    with pytest.raises(FileExistsError, match="already populated"):
        onboard(target=target, source=src)


def test_onboard_dry_run_writes_nothing(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    src = tmp_path / "ctx.md"
    src.write_text("user context")

    before = (target / "domains" / "career.md").read_text()
    result = onboard(target=target, source=src, dry_run=True)
    after = (target / "domains" / "career.md").read_text()

    assert before == after
    assert len(result.domains_written) == 7


def test_onboard_stub_mode_writes_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    target = tmp_path / "life"
    init_instance(target=target)
    src = tmp_path / "ctx.md"
    src.write_text("user context")

    result = onboard(target=target, source=src)
    career = (target / "domains" / "career.md").read_text()

    assert "onboard stub" in career
    assert result.used_llm is False
    assert len(result.domains_written) == 7
    assert any("LLM not configured" in n for n in result.notes)


def test_onboard_force_overwrites(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    target = tmp_path / "life"
    init_instance(target=target)
    f = target / "domains" / "career.md"
    f.write_text(f.read_text().replace("last_updated: TODO", "last_updated: 2026-05-13"))

    src = tmp_path / "ctx.md"
    src.write_text("user context")

    result = onboard(target=target, source=src, force=True)
    assert result.overwritten is True
