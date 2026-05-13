# Example instance — `jane-doe`

A fictional persona's lifekit instance. **Pure data + config, no code.** The lifekit engine (scripts, CLI, schemas) lives in the installed `lifekit` package. An instance like this one is just a directory of Markdown and YAML that lifekit reads.

## Reproducible quick-start

```bash
# 1. Install lifekit
pip install -e ../..

# 2. Copy this example to a working location
mkdir /tmp/my-lifekit-test
cp -r ./* /tmp/my-lifekit-test/
cd /tmp/my-lifekit-test

# 3. Tell lifekit to use this directory instead of ~/.life/
export LIFEKIT_ROOT=$(pwd)

# 4. Run the CLI commands
lifekit status
lifekit run morning-brief
lifekit refresh --dry-run
lifekit scout --dry-run
```

Each command operates on the directory in `LIFEKIT_ROOT` instead of the default `~/.life/`. Captured outputs in [`docs/examples/jane-doe-run.md`](../../docs/examples/jane-doe-run.md).

## What's here

- **`PLAN.md`** — instance-specific roadmap template
- **`domains/`** — 7 skeleton domain files (career, engineering, learning, health, commitments, ideas, finance)
- **`system/`** — `architecture.md`, `gaps.md`, `proposals.md`, `adapters.md` templates
- **`routines/workflows.yaml`** — cron config with 6 routines, all `enabled: false`
- **`scout/sources.yaml`** + **`scout/ledger.md`** — scout config and outcome tracker
- **`topics.yaml`** — news filter for morning brief
- **`queue.jsonl`** — empty inbox

## What's NOT here

- Real personal content — Jane is a placeholder, her domains are skeletons.
- A populated journal.
- Calendar / Telegram wiring — those are runtime concerns.

The point of this example is to show **shape and schema**, not a lived-in instance.

## Bootstrap from your own context

If you have a `~/.claude/CLAUDE.md` (or equivalent), `lifekit onboard` will draft your domain files from it. Stub-mode works without an API key; LLM-mode requires `pip install lifekit[llm]` plus `ANTHROPIC_API_KEY`.

```bash
export LIFEKIT_ROOT=~/.life
lifekit init
lifekit onboard --dry-run    # see what it would write
lifekit onboard              # actually write
```
