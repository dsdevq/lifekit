# Lifekit: A file-based framework for personal AI memory

*Draft — first technical post.*

I've been trying to build a "persistent AI collaborator" — a thing that knows my life across domains and gets more useful over time, not less. Three iterations in, the same three lessons kept showing up. They're the shape of lifekit.

## Lesson one: memory dies with the tool

The first version put everything in a chatbot's memory store — vector embeddings, a custom system prompt, the works. It worked for three weeks. Then the framework I'd built on shipped a breaking change to its memory API. Migrating felt worse than starting over, so I started over. Fourth iteration, different framework, same outcome.

The diagnosis was obvious in retrospect: I'd coupled my data to the vendor's runtime. Every time the runtime changed shape — new SDK, new memory format, deprecated endpoint — my memory had to migrate with it. Worse, every framework has opinions about how memory should be structured, and you inherit those opinions whether they fit or not.

The fix is structural. Memory lives in plain files I own. The runtime is plumbing on top. When I change tools — Claude to GPT, LangGraph to OpenAI Agents, dev-agent to OpenClaw — the *plumbing* changes. The files stay where they are.

## Lesson two: vector RAG is the wrong default

The instinct in the "personal AI" space is to reach for vector RAG as the memory layer. Embed everything, retrieve by similarity, let the LLM stitch fragments together. It's an impressive-looking design — and for the wrong use case.

A curated personal context isn't actually that big. Mine, after a decade of daily use, will be under 100MB. That's an entire lifetime of structured knowledge in a few thousand tokens of summaries, with all the depth in linked files. Modern frontier models have 200k-1M token context windows. The right answer isn't "search 100MB intelligently" — it's "load the relevant 50KB directly."

More importantly, curated memory has *structure*. A career fact lives in `career.md` because I put it there. Health context lives in `health.md`. Asking a vector index to find the right chunk *across* those files throws away the hierarchy I deliberately maintained. The retrieval is worse, not better.

There's still a place for RAG. External corpora — email, drive contents, web archives — are huge and unstructured, and that's exactly where vector retrieval earns its keep. lifekit treats this as a strict tier system:

- **Tier 1 (hot):** curated files, always loaded, no retrieval.
- **Tier 2 (warm):** old journal entries, SQLite FTS5 when scale demands.
- **Tier 3 (cold):** external unstructured corpora, vector retrieval allowed.

The discipline matters. The moment you let Tier 3 tools touch your curated layer, you've reintroduced the problem you were trying to avoid.

## Lesson three: proactivity needs discipline, not just an LLM call

I built three different "send me a daily digest" systems before realizing why they all failed. The LLM call wasn't the problem. The problem was that nothing else in the system enforced quality:

- **No source curation.** "Read AI Twitter and tell me what's important" produces hype every time. The LLM has no defense against loud-but-wrong inputs.
- **No outcome tracking.** I'd flag something as worth attention, never re-read the digest, and never learn whether the flag was right. The system stayed at day-one calibration forever.
- **No adversarial pass.** Every digest item passed through a polite "this looks interesting" check. None had to survive "argue why this is actually noise."

lifekit codifies these as schemas, not soft suggestions. The scout subsystem has three explicit requirements: a hand-curated `sources.yaml` (no automatic source discovery), an `outcome ledger` with 7-day and 30-day follow-up fields per finding (so the system can grade itself), and an `adversarial pass` baked into every prompt (steelman the "this is hype" argument before grading). None of those are optional. Without them, scout would be exactly the broken thing it replaces.

## What lifekit actually is

It's a Python package and a directory structure. You run `lifekit init`, you get `~/.life/` with seven domain files, a routines config, a scout subsystem, and system self-knowledge docs. Static-portion scripts (`lifekit run morning-brief`, `lifekit scout`, `lifekit refresh`) work out of the box. The runtime — what actually fires the cron, calls the LLM, posts to your chat channel — is your choice, wired through replaceable ports.

Replaceability is the other thing lifekit insists on. Every swap-eligible third-party tool — SWE engine, runtime gateway, sandbox, local LLM, future vector DB — sits behind a `Protocol` interface. Today my instance uses OpenHands as the `BuildEngine` and Ollama as the `LocalLLM`. Tomorrow it could be Aider and llama.cpp. The orchestration code doesn't care. The catalog of ports + current adapters lives in `system/adapters.md`.

## What lifekit explicitly is not

- Not a chatbot.
- Not a memory plugin for a specific framework.
- Not a hosted service.
- Not an opinion about which model you should use.

It's a directory structure plus a set of invariants. The invariants are the value: portability (POSIX, plain text), separation (knowledge vs runtime), discipline (curation > capability), reversibility (symlinks over rewrites). Without those, you have another half-built memory system. With them, you have something that survives the next three rounds of "the framework I built on shipped a breaking change."

The repo is [github.com/dsdevq/lifekit](https://github.com/dsdevq/lifekit). Pre-alpha. MIT. Ideas/PRs welcome — especially adapters for runtimes I'm not using yet.

---

*Written from a private instance running this exact code. The dogfooding loop turned up a parser bug in the morning brief composer mid-draft; you can see the fix in commit `f0e0088`. That's the loop working.*
