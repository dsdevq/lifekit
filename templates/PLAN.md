# Plan — your instance

This file is yours to shape. lifekit doesn't prescribe a roadmap — only the schemas, scripts, and invariants.

A starter outline:

## Status
_(track which phases are done, in progress, deferred)_

## Phases
_(your own phases — the lifekit author's instance uses something like:)_

- Phase 0 — Local scaffolding
- Phase 1 — Schemas locked
- Phase 3 — Orchestrator wired to ~/.life/
- Phase 4 — Editor (Claude Code / Cursor / VS Code) reads ~/.life/ on session start
- Phase 5 — First proactive routine (morning brief) firing
- Phase 5.3 — System self-knowledge upkeep automated
- Phase 5.5 — Scout running with outcome ledger
- Phase 7.5 — Runtime gateway adopted (OpenClaw or equivalent)
- Phase 8 — Portability (VPS / multi-device)

## Portability invariant

All state in `~/.life/` must remain plain text + POSIX paths. No DB-only state in the knowledge layer. Migration between hosts = `rsync -a ~/.life/ newhost:~/.life/`.

## Memory tier invariant

The curated knowledge layer in `~/.life/` is small, structured, accessed deterministically. **No RAG / vector DB on the curated memory.** Three tiers:

- **Tier 1 — Hot:** ~/.life/domains/*.md, system/*.md, today's journal, recent scout ledger. Just read the files.
- **Tier 2 — Warm:** older journal, full scout ledger. SQLite FTS5 when entry count > ~1000.
- **Tier 3 — Cold:** external corpora (Gmail / Drive / web archive). Vector index OPTIONAL, behind `MemoryRetrieval` port. NEVER applied to the curated layer.

## Adapter invariant

Every replaceable third-party dependency lives behind a port owned by your orchestration code. See `system/adapters.md`.
