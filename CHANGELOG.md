# Changelog

## Unreleased

### Added
- `src/lifekit/curator/` — queue-drain daemon moved from `lifekit-stack` into the framework where it belongs. Exposes `lifekit curator daemon` CLI command and `lifekit.curator.enqueue()` for programmatic use.
- `tests/test_curator.py` — defensive-parsing regression tests (ported from `lifekit-stack/compose/curator/`).
