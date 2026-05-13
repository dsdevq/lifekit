# Example run — `examples/jane-doe/`

Verbatim output of running each lifekit CLI command against the bundled example instance. Reproducible via the command sequence in `examples/jane-doe/README.md`.

## Setup

```bash
cd /tmp && rm -rf jane-doe-test && mkdir jane-doe-test
cp -r ~/projects/lifekit/examples/jane-doe/* /tmp/jane-doe-test/
cd /tmp/jane-doe-test
export LIFEKIT_ROOT=$(pwd)
```

## `lifekit status`

```
instance: /tmp/jane-doe-test
  domains: 7 file(s)
  routines config: present
  scout sources: present
```

## `lifekit run morning-brief`

```
# Morning brief — Wednesday, 13 May 2026

**Today**
_(calendar stub — wire your runtime's calendar integration for 2026-05-13)_

**News**
_(news fetch stub — top topics from topics.yaml:)_
- **example_topic** — keywords:

**Breakfast**
_(nutrition profile present but no goals/breakfast captured — fill those subsections)_
```

The brief is informative-by-default: it tells you exactly what's missing in the data layer rather than silently producing nonsense.

## `lifekit refresh --dry-run`

```
date updates: 7
inferred gaps in gaps.md: 1
```

Dry-run shows what *would* change. Drop `--dry-run` to actually update `last_updated` fields and append inferred gaps.

## `lifekit scout --dry-run`

(Requires network access — skipped in offline test environment. See `tests/test_scout.py` for offline fetcher stubbing.)

## Takeaway

A fresh lifekit instance with no curation produces honest, useful output that *guides* the user toward what to fill in. No hallucination, no silent placeholder soup.
