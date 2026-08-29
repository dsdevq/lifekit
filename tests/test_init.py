"""Smoke test for `lifekit init`."""

from __future__ import annotations

from pathlib import Path

from lifekit.core.init import init_instance


def test_init_creates_expected_tree(tmp_path: Path) -> None:
    target = tmp_path / "life"
    created = init_instance(target=target)
    assert created == target
    assert (created / "domains" / "career.md").exists()
    assert (created / "system" / "architecture.md").exists()
    assert (created / "scout" / "sources.yaml").exists()
    assert (created / "routines" / "workflows.yaml").exists()
    assert (created / "journal").is_dir()
    assert (created / "PLAN.md").exists()


def test_init_refuses_nonempty(tmp_path: Path) -> None:
    target = tmp_path / "life"
    target.mkdir()
    (target / "stuff.md").write_text("nonempty")
    try:
        init_instance(target=target)
    except FileExistsError:
        return
    raise AssertionError("expected FileExistsError")


def test_init_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "life"
    target.mkdir()
    (target / "stuff.md").write_text("nonempty")
    init_instance(target=target, force=True)
    assert (target / "domains" / "career.md").exists()


def test_lifekit_root_env_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LIFEKIT_ROOT", str(tmp_path / "custom"))
    from lifekit.core.paths import life_root

    assert life_root() == (tmp_path / "custom").resolve()


def test_state_dir_env_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LIFEKIT_STATE_DIR", str(tmp_path / "state"))
    from lifekit.core.paths import state_dir

    assert state_dir() == (tmp_path / "state").resolve()


def test_state_dir_xdg_fallback(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("LIFEKIT_STATE_DIR", raising=False)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg"))
    from lifekit.core.paths import state_dir

    assert state_dir() == (tmp_path / "xdg").resolve() / "lifekit"


def test_state_dir_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("LIFEKIT_STATE_DIR", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    from lifekit.core.paths import state_dir

    assert state_dir() == tmp_path / ".local" / "state" / "lifekit"
