# lifekit

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
├── cli/                CLI entrypoint (lifekit init, run, scout, …)
├── core/               schemas, templates loader, file IO
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
```

## License

MIT.

## Origin

Extracted from a private personal project. Author: [@dsdevq](https://github.com/dsdevq).
