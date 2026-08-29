"""Tests for the scout module — offline (fetchers stubbed via monkeypatch)."""

from __future__ import annotations

from pathlib import Path

from lifekit.core.init import init_instance
from lifekit.scout import run_scout


def _fake_items() -> list[run_scout.Item]:
    return [
        run_scout.Item(
            title="LangGraph 0.9 ships",
            url="https://example.com/lg",
            source="test",
            summary="langgraph python langchain agent improvements",
        ),
        run_scout.Item(
            title="Some random meme",
            url="https://example.com/meme",
            source="test",
            summary="cat doing things",
        ),
    ]


def test_scout_run_dry_run_does_not_write(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    monkeypatch.setattr(run_scout, "_fetch_hn", lambda **kw: _fake_items())
    monkeypatch.setattr(run_scout, "_fetch_rss", lambda *a, **kw: [])
    monkeypatch.setattr(run_scout, "_fetch_reddit", lambda *a, **kw: [])

    ledger_before = (target / "scout" / "ledger.md").read_text()
    proposals_before = (target / "system" / "proposals.md").read_text()

    result = run_scout.run(limit=10, dry_run=True, root=target)

    assert result["items"] >= 1
    assert (target / "scout" / "ledger.md").read_text() == ledger_before
    assert (target / "system" / "proposals.md").read_text() == proposals_before


def test_scout_writes_ledger_and_proposals(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    monkeypatch.setattr(run_scout, "_fetch_hn", lambda **kw: _fake_items())
    monkeypatch.setattr(run_scout, "_fetch_rss", lambda *a, **kw: [])
    monkeypatch.setattr(run_scout, "_fetch_reddit", lambda *a, **kw: [])

    result = run_scout.run(limit=10, dry_run=False, root=target)
    assert result["items"] == 2

    ledger = (target / "scout" / "ledger.md").read_text()
    assert "LangGraph 0.9 ships" in ledger
    assert "https://example.com/lg" in ledger


def test_scout_dedups_against_existing_ledger(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    # pre-seed ledger with one of the URLs
    ledger = target / "scout" / "ledger.md"
    ledger.write_text(
        ledger.read_text()
        + "\n\n### 2026-05-13 — LangGraph 0.9 ships\nSource: https://example.com/lg\n"
    )

    monkeypatch.setattr(run_scout, "_fetch_hn", lambda **kw: _fake_items())
    monkeypatch.setattr(run_scout, "_fetch_rss", lambda *a, **kw: [])
    monkeypatch.setattr(run_scout, "_fetch_reddit", lambda *a, **kw: [])

    result = run_scout.run(limit=10, dry_run=False, root=target)

    # only the new (non-duplicate) item should land — the langgraph URL is in existing
    assert result["items"] == 2
    # the second fake item ("cat doing things") gets graded probably-noise so
    # may or may not land; what matters is the langgraph one is NOT duplicated
    text = ledger.read_text()
    assert text.count("https://example.com/lg") == 1


def test_scout_grade_assignment(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    # write some content into engineering.md so personal-tooling keywords exist
    (target / "domains" / "engineering.md").write_text(
        "---\nname: engineering\nsummary: x\nlast_updated: 2026-05-13\ntags: []\n---\n"
        "## Notes\nlanggraph langchain agent python typescript angular\n"
    )
    monkeypatch.setattr(run_scout, "_fetch_hn", lambda **kw: _fake_items())
    monkeypatch.setattr(run_scout, "_fetch_rss", lambda *a, **kw: [])
    monkeypatch.setattr(run_scout, "_fetch_reddit", lambda *a, **kw: [])

    result = run_scout.run(limit=10, dry_run=True, root=target)
    # at least one item should be classified — the grades dict has at least one entry
    assert sum(result["grades"].values()) == result["items"]
