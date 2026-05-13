# Philosophy

The design choices behind lifekit. Read this before extending the project.

## Three lessons that shaped lifekit

After three rounds of bolting "memory" onto chatbots:

1. **A chatbot's memory is fragile because it's tied to the runtime.** When you change tools — new model, new framework, new gateway — you start over. The fix: knowledge lives in plain files. Runtime is replaceable.

2. **Vector RAG is the wrong default for personal context.** Curated Markdown beats similarity search on small, structured corpora. A person's actual *curated* context is small — under 100 MB even after a decade. RAG flattens structure and retrieves worse than direct file reads. Reserve RAG for *external* unstructured corpora.

3. **Proactivity needs structure or it becomes noise.** "Send me a daily digest" routines collapse without explicit source curation, outcome ledgers, and adversarial scoring. Discipline is the actual feature, not the LLM call.

## The two-layer model

| Layer | What | Owner |
|---|---|---|
| Knowledge | Markdown + YAML + JSONL in `~/.life/` | the user |
| Behaviors | Orchestration, runtime gateway, sandbox | replaceable, bring-your-own |

Layers are decoupled by design. Knowledge survives the runtime. Runtime is swappable.

## Memory tiers

```
Tier 1 — Hot (always loaded, no retrieval):
  Domain files, system docs, today's journal, recent scout ledger.
  Fits in <50k tokens. Just read the files.

Tier 2 — Warm (on-demand, structured search):
  Older journal, full scout ledger, queue history.
  SQLite FTS5 when entry count > ~1000.

Tier 3 — Cold (vector index, OPTIONAL, external corpora only):
  Gmail / Drive / web archive / scout source archive.
  Behind a `MemoryRetrieval` port. Never applied to curated layer.
```

## Goal-directed scout

A signal filter whose 90%+ job is **"what could make THIS system better?"** — not generic AI news.

- **System lens (primary):** score against `system/architecture.md` + `system/gaps.md`.
- **Personal-tooling lens (secondary):** score against `domains/engineering.md` + `domains/learning.md`.
- **Adversarial pass:** for each surviving item, write a steelman of "this is hype" before grading.
- **Outcome ledger:** every flagged item gets a 7-day and 30-day follow-up. That's how the filter learns.

General news (engineering / trading / economy / politics) is **separate** — handled by `topics.yaml` and the morning brief. Don't conflate awareness with self-improvement.

## Adapter discipline (anti-lock-in)

Every replaceable third-party dependency lives behind a port owned by your orchestration code. Adapters implement the port. Swap an upstream tool = write a new adapter + flip config.

Applied to: `BuildEngine`, `TradingEngine`, `RuntimeGateway`, `Sandbox`, `LocalLLM`, future `MemoryRetrieval` / `FullTextSearch`.

Not applied to: your own orchestration code, the Markdown/YAML knowledge layer, your primary frontier model.

## Reversibility

Symlinks over code changes when migrating data. Disabled flags over deletions. Git history over silent overwrites. The system should be easy to back out of any change.

## What lifekit explicitly is not

- **Not** a chatbot.
- **Not** a memory plugin for one specific framework.
- **Not** a hosted service.
- **Not** an opinion about which model you should use.

It's a directory structure + a set of invariants. Bring your own runtime.
