# Getting started

> ⚠️ Pre-alpha. The CLI scaffolds an instance but most runtime commands are stubs. Use the example in `examples/jane-doe/` as a reference until v0.1.

## Install (from source, for now)

```bash
git clone https://github.com/lifekit-hq/lifekit
cd lifekit
pip install -e .
```

## Scaffold an instance

```bash
lifekit init
# creates ~/.life/ from bundled templates

lifekit status
# instance: /home/you/.life
#   domains: 7 file(s)
#   routines config: present
#   scout sources: present
```

## Fill in your domain files

Open `~/.life/domains/*.md`. Each file has a YAML frontmatter block and section headers. Replace the `_(to fill — ...)_` placeholders with your actual content.

Suggested order:
1. `health.md` — fastest to fill, biggest immediate payoff
2. `career.md` — anchors goal-tracking
3. `engineering.md` — projects + active decisions
4. `finance.md`, `learning.md`, `commitments.md`, `ideas.md`

## Wire your runtime

lifekit doesn't ship a runtime — that's your call. Common stacks:

- **LangGraph** + Telegram bot (the reference instance)
- **OpenAI Agents SDK** + iMessage
- **OpenClaw** (multi-channel gateway) + your orchestrator of choice

See `templates/system/architecture.md` for the layered model. Once your runtime can read `~/.life/`, flip a routine in `routines/workflows.yaml` from `enabled: false` to `enabled: true` and wire it into your scheduler.

## Add scout sources

Open `~/.life/scout/sources.yaml`. Add curated subreddits, blogs, GitHub trending filters. Quality > breadth — five great sources beat fifty noisy ones.

## Next steps

- `docs/philosophy.md` — design rationale
- `examples/jane-doe/` — reference scripts (morning brief, scout, refresh)
- `templates/system/adapters.md` — port catalog if you start wrapping third-party tools

## Privacy

Your `~/.life/` instance should typically be a **private** git repo. The framework (this repo) is public; your *contents* are yours.
