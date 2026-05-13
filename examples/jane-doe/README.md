# Example instance — `jane-doe`

A fictional persona's lifekit instance. Use as a reference when setting up your own.

## What's here

- Domain skeletons identical to `templates/` — Jane hasn't filled hers in either.
- The three reference scripts copied from the author's private instance:
  - `routines/morning_brief.py` — composes a brief from domain + topics + scout files
  - `scout/run_scout.py` — fetches sources, two-lens scores, writes to ledger + proposals
  - `system/refresh.py` — updates last_updated, infers gaps from proposals
  - `routines/translate.py` — bridges canonical workflows.yaml into a target runtime's format

## Run them against this directory

The scripts default to reading from `~/.life/`. To point them at this example instead:

```bash
cd examples/jane-doe
# scripts currently read Path.home() / ".life" — adapt the constants or
# symlink: ln -sf $(pwd) ~/.life-jane  and edit LIFE = ~/.life-jane
```

(Cleaning these up to honour `LIFEKIT_ROOT` env var is a planned improvement.)

## What's missing

- Actual content in Jane's domain files (it's a skeleton — she's new too).
- A populated journal.
- Calendar/Telegram wiring — those are runtime concerns.

The point of this example is to show **shape and schema**, not a fully-lived-in instance.
