# Adapters — swap-eligible third-party boundaries

**Principle:** every replaceable third-party dependency lives behind an interface (a "port") that your orchestration code owns. Adapters implement the port. Swap a tool = write a new adapter + flip config.

**Invariant:** never call a third-party SDK directly from orchestration code. Always go through an owned port.

## Ports

### `BuildEngine`
Autonomous SWE engine — takes a spec, opens a PR.

- **Current adapter:** TODO (e.g. OpenHands, Aider, Cline, Devin, custom)
- **Candidate alternatives:** _(track them so swaps are easy)_
- **Swap criteria:** _(what would trigger a swap — benchmark, abandonment risk, pricing)_

### `TradingEngine`
Multi-agent trading framework — produces signals/orders (paper or live).

- **Current adapter:** TODO
- **Candidate alternatives:** _(TauricResearch/TradingAgents, QuantConnect Lean, …)_
- **Swap criteria:** TODO

### `RuntimeGateway`
Multi-channel personal-assistant runtime (channels, voice, daemon).

- **Current adapter:** TODO (e.g. OpenClaw, custom Telegram bot)
- **Candidate alternatives:** TODO
- **Swap criteria:** TODO

### `Sandbox`
Isolated execution environment for autonomous agents.

- **Current adapter:** TODO (e.g. NemoClaw, plain Docker, gVisor, Firecracker)
- **Candidate alternatives:** TODO
- **Swap criteria:** TODO

### `LocalLLM`
Local model for routing / classification / cheap inference.

- **Current adapter:** TODO (e.g. Ollama:gemma, llama.cpp, mlx-lm)
- **Candidate alternatives:** TODO
- **Swap criteria:** TODO

### `MemoryRetrieval` (Tier 3 — external corpora only)
Vector-search retrieval over external unstructured corpora (email, drive, web archive). **Never applied to the curated `~/.life/` layer** — see memory tier invariant.

- **Current adapter:** none until needed
- **Candidate adapters:** pgvector, Qdrant, Chroma, sqlite-vec

### `FullTextSearch` (Tier 2 — older journal/ledger)
Exact-match / FTS over older Tier 2 memory when it scales past hot-context fit.

- **Current adapter:** none until needed
- **Candidate adapters:** SQLite FTS5 (default), ripgrep (zero-dep fallback)

---

## Out-of-scope for porting

Some lock-in is acceptable. These are **not** behind owned interfaces by default:

- **Your own orchestration code** (LangGraph / whatever) — it's substrate, not dependency.
- **`~/.life/` Markdown + YAML** — plain text, nothing to abstract.
- **Your primary frontier model** (Claude / GPT / etc.) — abstracting it commoditizes the model's specific strengths. Skipping abstraction here is a deliberate bet.

## Audit cadence

Scout reads this file when proposing new tools. When scout flags an alternative for a port, it lands in `system/proposals.md` with the port name in the entry. Quarterly: re-evaluate the "Swap criteria" lines.
