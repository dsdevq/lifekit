# Example instance — `jane-doe`

A fictional persona's lifekit instance. **Pure data + config, no code.**

The lifekit engine (scripts, CLI, schemas) lives in the installed `lifekit` package. An instance like this one is just a directory full of Markdown and YAML that lifekit reads.

## Try it

```bash
pip install -e ../..   # install the lifekit package from this repo

# point lifekit at this example instead of ~/.life/
export LIFEKIT_ROOT=$(pwd)

lifekit status
lifekit run morning-brief
lifekit scout --dry-run
lifekit refresh --dry-run
```

## What's NOT here

- Real personal content — domains are skeletons.
- A populated journal.
- Calendar / Telegram wiring — those are runtime concerns.

This example shows **shape + schema**, not a lived-in instance. Your own private repo holds the lived-in version.
