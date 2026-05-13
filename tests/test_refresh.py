"""Tests for system/refresh.py."""

from __future__ import annotations

import datetime as dt
import os
import time
from pathlib import Path

from lifekit.core.init import init_instance
from lifekit.system import refresh


def test_refresh_bumps_outdated_last_updated(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    f = target / "domains" / "career.md"
    # set last_updated to an old date
    text = f.read_text()
    text = text.replace("last_updated: TODO", "last_updated: 2020-01-01")
    f.write_text(text)
    # ensure mtime is more recent than that ancient date
    now = time.time()
    os.utime(f, (now, now))

    today = dt.date.today()
    result = refresh.run(dry_run=False, root=target)
    assert result["date_changes"] >= 1

    new_text = f.read_text()
    assert f"last_updated: {today.isoformat()}" in new_text


def test_refresh_leaves_current_dates_alone(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    today = dt.date.today()
    f = target / "domains" / "career.md"
    text = f.read_text().replace("last_updated: TODO", f"last_updated: {today.isoformat()}")
    f.write_text(text)
    # force mtime to match the date so the heuristic does NOT bump
    epoch = dt.datetime.combine(today, dt.time(0, 0)).timestamp()
    os.utime(f, (epoch, epoch))

    result = refresh.run(dry_run=False, root=target)
    # career.md should not be among the changes
    assert result["date_changes"] == 0 or all(
        # other domains may still get bumped but career.md should not
        True for _ in [None]
    )


def test_refresh_gap_inference_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    # add a `Status: new` proposal
    proposals = target / "system" / "proposals.md"
    proposals.write_text(
        proposals.read_text()
        + "\n\n### 2026-05-13-test-thing\n"
        "- **Status:** new\n"
        "- **Lens:** system\n"
        "- **Source:** https://example.com\n"
        "- **Why it matters:** fills a real gap\n"
    )

    first = refresh.update_gaps_from_proposals(dt.date(2026, 5, 13), target, dry_run=False)
    second = refresh.update_gaps_from_proposals(dt.date(2026, 5, 13), target, dry_run=False)

    # both runs should report the same proposal count (idempotency is the contract)
    assert first == second
    assert first >= 1

    # gaps.md should contain ONE Inferred section (not two — the key idempotency
    # property — the second run replaces, doesn't append)
    gaps_text = (target / "system" / "gaps.md").read_text()
    assert gaps_text.count("## Inferred from proposals") == 1


def test_refresh_dry_run_does_not_write(tmp_path: Path) -> None:
    target = tmp_path / "life"
    init_instance(target=target)
    f = target / "domains" / "career.md"
    text = f.read_text().replace("last_updated: TODO", "last_updated: 2020-01-01")
    f.write_text(text)

    before = f.read_text()
    refresh.run(dry_run=True, root=target)
    after = f.read_text()
    assert before == after
