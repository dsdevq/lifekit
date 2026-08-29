# lifekit — Claude Context

A file-based framework for building your own persistent AI collaborator. Your knowledge lives as plain Markdown + YAML in a directory you own (`~/.life/` by default); the AI runtime (LangGraph, OpenClaw, a Telegram bot, …) is replaceable plumbing wired behind ports. lifekit owns the **knowledge layer** — schemas, templates, scout, curator, routines — and deliberately nothing else. Pre-alpha (0.0.1, unreleased). Sole developer: Denys.

## Layout

| Path                  | What                                                                                          |
| --------------------- | --------------------------------------------------------------------------------------------- |
| `src/lifekit/cli/`    | `lifekit` click CLI — init, status, onboard, run, scout, refresh, emit, curator               |
| `src/lifekit/core/`   | instance scaffolding (`init`), CLAUDE.md-driven bootstrap (`onboard`), path resolution        |
| `src/lifekit/curator/`| queue-drain daemon — consumes `queue.jsonl`, updates domain files via `claude --print`        |
| `src/lifekit/scout/`  | goal-directed signal filter — fetch sources, score, write ledger + proposals                  |
| `src/lifekit/routines/` · `system/` | morning-brief renderer; `refresh` (date bumps + gap surfacing)                  |
| `src/lifekit/emitters/`| translate canonical `workflows.yaml` to runtime formats (currently LangGraph cron)           |
| `templates/`          | the files `lifekit init` scaffolds — the canonical instance schema                            |
| `examples/jane-doe/`  | a complete, runnable example instance                                                         |
| `docs/`               | getting-started, philosophy (the memory-tier argument), prompt templates                      |

## Commands

```bash
pip install -e ".[dev]"     # or .[dev,llm] for the anthropic-backed onboard path
pytest -q                   # full suite, <1s, offline (all fetchers stubbed)
ruff check .                # lint (rule set in pyproject [tool.ruff.lint])
ruff format --check .       # format gate
python -m build             # sdist + wheel must build
lifekit init && lifekit status   # smoke-test the CLI against a scratch $LIFEKIT_ROOT
```

## Mandatory gates (what `.github/workflows/test.yml` enforces on every PR)

- `pytest -q` green on Python 3.11 / 3.12 / 3.13.
- `ruff check .` and `ruff format --check .` — zero errors, no soft-fail. `PLC0415` is ignored on purpose (lazy imports in the CLI and tests are deliberate); don't "fix" them.
- `python -m build` — packaging metadata must stay buildable.
- Local mirror: `.pre-commit-config.yaml` runs the same three gates (`pip install pre-commit && pre-commit install`).
- Tests are offline by design — scout/curator tests stub every fetcher and the `claude` binary. A test that needs the network or a real LLM is wrong.

## Conventions (ecosystem-standard)

- **Branch**: `<type>/<issue#>-<slug>` (e.g. `feat/3-warm-tier`); create via `gh issue develop <n>`.
- **Commits / PR titles**: conventional commits (`feat(scout): …`, `fix(curator): …`). PR body: what + why + a **Validation** section.
- **Issues**: imperative title, no priority prefix — priority lives in the `P1`/`P2` label. P1 issues carry acceptance criteria; P2/P3 stay one-liners until promoted.
- **Milestones**: `M<n> — <outcome>`, named for the outcome, never a date.
- Main is protected in spirit: all changes land via squash-merged PR, CI green first.
- Only `README.md` and `CLAUDE.md` belong at the repo root — durable docs go to `docs/` (LICENSE and CHANGELOG.md stay).
- Anti-lock-in is the product: every third-party dependency in an instance sits behind a port. Keep the framework itself runtime-agnostic — `anthropic` stays an optional extra, never a hard dependency.

### Gold-standard divergences

- **No release automation (yet).** The repo is pre-alpha, unreleased, and dormant since 2026-05; CHANGELOG.md is hand-maintained. release-please (python type) + the Weekly Release cron get wired when the repo wakes and a publishing target (PyPI) is decided — until then a weekly cron on a dormant repo is noise, not machinery. Conventional commits are already in force so the history will parse cleanly when it lands.
- **No area labels.** With one open issue there is nothing to partition; add them when the backlog justifies it.
