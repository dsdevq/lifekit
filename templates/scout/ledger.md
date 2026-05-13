# Scout Ledger

Outcome tracker for scout findings. The ledger is how the system learns whether its judgment is calibrated.

## Schema

Each entry:

```
### YYYY-MM-DD — <title>
- **Lens:** system | personal-tooling
- **Source:** <url or source name>
- **Initial grade:** worth-looking-at | maybe | probably-noise
- **Why flagged:** <one line — which gap / which workflow / which capability>
- **Proposal id:** <proposals.md anchor, if promoted>
- **Followup (7d):** <was this still alive? did you act?>
- **Followup (30d):** <did it pan out? validated / dead / still uncertain>
```

Scout revisits entries at 7-day and 30-day marks to fill the follow-up fields. This is what teaches the filter.

---

## Entries
_(empty until first scout run)_
