# lifekit

[![CI](https://github.com/lifekit-hq/lifekit/actions/workflows/test.yml/badge.svg)](https://github.com/lifekit-hq/lifekit/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-pre--alpha-orange.svg)](#status)

**A file-based framework for building your own persistent AI collaborator.**

Most "personal AI" projects bundle the assistant *and* the user's data into one runtime. lifekit takes the opposite stance: your knowledge is plain Markdown in a directory, and the AI runtime is replaceable plumbing on top.

```
┌─────────────────────────────────────────────────┐
│ Knowledge (yours):  ~/.life/                    │
├─────────────────────────────────────────────────┤
│ Orchestration:      bring-your-own (LangGraph,  │
│                     LangChain, OpenAI Agents…)  │
├─────────────────────────────────────────────────┤
│ Runtime gateway:    bring-your-own (OpenClaw,   │
│                     custom Telegram bot, …)     │
├─────────────────────────────────────────────────┤
│ Autonomous sandbox: only when needed            │
│                     (NemoClaw, Docker, gVisor…) │
└─────────────────────────────────────────────────┘
```

lifekit owns the **knowledge layer** — schemas, templates, scout, curator, routines — and defines **ports** (interfaces) for everything else. You wire your preferred runtime behind those ports. Nothing locks you in.

## Status

🚧 **Pre-alpha skeleton.** The core schemas and static-portion scripts work; runtime wiring is per-adopter. Not yet released.

## Why now

Most personal-AI tools couple memory to the runtime — your "memory" lives inside whichever chatbot you happen to use this month. Change tools and you start over. lifekit takes the opposite stance: memory is a directory of Markdown files you own, and the runtime is replaceable plumbing on top. The format outlives the tooling.

The other thing personal-AI tools get wrong is reaching for vector RAG as the default. For a *curated* personal context — under 100 MB even after a decade of daily use — RAG is the wrong tool. Direct file reads on a well-organized, hierarchical store outperform similarity search every time. lifekit reserves vector retrieval for one specific case (Tier 3 cold storage of external unstructured corpora) and gets out of the way for everything else. See [`docs/philosophy.md`](docs/philosophy.md) for the full memory-tier argument.

Finally: proactivity needs structure, not just an LLM call on a cron. Daily digests that aren't grounded in pre-committed source curation, adversarial scoring, and outcome ledgers become noise within a week. lifekit codifies the discipline as schemas and conventions, so the *system* enforces what users would otherwise abandon.

## Why this exists

After three rounds of bolting "memory" onto chatbots, three lessons kept repeating:

1. **A chatbot's "memory" is fragile because it's tied to the runtime.** When you change tools, you start over.
2. **Vector RAG is the wrong default for personal context.** Curated Markdown beats similarity search on small, structured corpora — and a person's actual context *is* small (≪100 MB even after a decade).
3. **Proactivity needs structure.** "Send me a digest" routines fall apart without explicit source curation, outcome ledgers, and adversarial scoring.

lifekit codifies those lessons.

## Core ideas

**Two-layer model.** Knowledge (files) vs Behaviors (runtime). They're decoupled — change one without rewriting the other.

**Memory tiers.** Hot context (just read the files), warm (SQLite FTS5 when journals scale), cold (optional vector RAG for *external* corpora only — never the curated layer).

**Goal-directed scout.** A signal filter whose 90%+ job is "what could make THIS system better?" — not generic AI news. Outcome ledger teaches the filter over time.

**Anti-lock-in adapters.** Every replaceable third-party tool sits behind a port (`BuildEngine`, `TradingEngine`, `RuntimeGateway`, `Sandbox`, `LocalLLM`, …). Swap upstream by writing a new adapter.

**Discipline > capability.** Required triggers on watchlists. Adversarial scoring on scout. Outcome follow-ups on every flagged item. The system is only as good as its curation.

## What's in this repo

```
src/lifekit/
├── cli/                CLI entrypoint (lifekit init, run, scout, curator, …)
├── core/               schemas, templates loader, file IO
├── curator/            queue-drain daemon — drains queue.jsonl, calls Claude, updates domain files
└── adapters/           reference adapters (Ollama, etc.)

templates/              what `lifekit init` copies into a new ~/.life/
├── domains/            7 domain skeletons (career, engineering, …)
├── system/             architecture, gaps, proposals, adapters docs
├── scout/              sources.yaml + ledger header
└── routines/           workflows.yaml + prompts/

examples/jane-doe/      a fictional populated instance — anchors the docs

docs/                   philosophy, design decisions, runbooks
tests/                  unit + integration
```

## Quick start (target UX, not yet wired)

```bash
pip install lifekit
lifekit init                       # creates ~/.life/ from templates
lifekit onboard                    # interactive wizard, populates domains
lifekit run morning-brief          # prints brief to stdout
lifekit scout --lens system        # runs scout, writes to ledger + proposals
lifekit refresh                    # updates last_updated + infers gaps
lifekit curator daemon             # start the queue-drain daemon
```

## License

MIT.

## Origin

Extracted from a private personal project. Author: [@dsdevq](https://github.com/dsdevq).
