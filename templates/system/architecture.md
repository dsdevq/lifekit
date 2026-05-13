# System Architecture — current state

**Last updated:** TODO
**Phase:** TODO

This file is a living snapshot of *your* lifekit instance. Update as you wire things up.

## Layered stack

```
┌─────────────────────────────────────────────────┐
│ Knowledge:  ~/.life/         (this directory)   │
├─────────────────────────────────────────────────┤
│ Orchestration:  TODO  (LangGraph / OpenAI       │
│                 Agents / custom / …)            │
├─────────────────────────────────────────────────┤
│ Runtime gateway:  TODO  (OpenClaw / custom      │
│                   Telegram bot / …)             │
├─────────────────────────────────────────────────┤
│ Autonomous-agent sandbox:  TODO  (NemoClaw /    │
│                            Docker / gVisor / …) │
└─────────────────────────────────────────────────┘
```

## Directory tree

```
~/.life/
├── PLAN.md             your plan, your phases
├── README.md           context for anyone reading the repo
├── domains/            7 files about you
├── journal/            YYYY-MM-DD.md daily entries
├── system/             self-knowledge: this file, gaps.md, proposals.md, adapters.md
├── scout/              sources.yaml + ledger.md
├── routines/           workflows.yaml + prompts/
├── topics.yaml         general news filter
└── queue.jsonl         append-only inbox; curator drains here
```

## Schemas (lifekit-locked)

### Domain file frontmatter
```yaml
---
name: <slug>
summary: <one line>
last_updated: YYYY-MM-DD
tags: [active|scratchpad|...]
---
```

### `queue.jsonl` event
```json
{
  "ts": "YYYY-MM-DDTHH:MM:SSZ",
  "source": "channel|claude|cron|manual",
  "type": "idea|fact|commitment|food|decision|other",
  "content": "raw input",
  "routing_hint": "<domain-slug or null>"
}
```

### Routine (in `routines/workflows.yaml`)
```yaml
- name: <stable id>
  cron: "<5-field crontab>"
  prompt: <orchestrator instruction>
  reads: [paths relative to ~/.life/]
  output: telegram|journal|proposals|silent
  enabled: true|false
```

## What is wired in your instance

_(fill in as you wire each layer — orchestration, runtime, sandbox, MCP integrations, …)_

## Workflow activation procedure

_(document how routines move from `enabled: false` in workflows.yaml to actually firing on schedule. depends on your orchestration choice.)_
