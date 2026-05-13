#!/usr/bin/env python3
"""Morning brief generator — static portion (Phase 5).

Reads ~/.life/ files and prints a fully-formed brief to stdout.
Calendar and Telegram layers are stubbed (documented inline) — they'll be
wired in by dev-agent at activation time.

Usage:
    python3 ~/.life/routines/morning_brief.py
    python3 ~/.life/routines/morning_brief.py --date 2026-05-13
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not installed. Run: pip install pyyaml")

LIFE = Path.home() / ".life"
DOMAINS = LIFE / "domains"
SCOUT = LIFE / "scout"
TOPICS = LIFE / "topics.yaml"

MAX_NEWS_ITEMS = 3
MAX_SCOUT_ITEMS = 2


# ---------- file readers ----------

def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def _section(text: str, header: str) -> str:
    """Extract a markdown section by its `## Header` (case-insensitive)."""
    body = _strip_frontmatter(text)
    pattern = rf"(?im)^##\s+{re.escape(header)}\s*$"
    m = re.search(pattern, body)
    if not m:
        return ""
    start = m.end()
    next_m = re.search(r"(?im)^##\s+", body[start:])
    end = start + next_m.start() if next_m else len(body)
    return body[start:end].strip()


def _non_placeholder_lines(section_body: str) -> list[str]:
    """Strip placeholder italic-only lines like `_(to fill — ...)_`."""
    out: list[str] = []
    for line in section_body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("_(") and stripped.endswith(")_"):
            continue
        out.append(stripped)
    return out


# ---------- section composers ----------

def calendar_section(today: dt.date) -> list[str]:
    """STUB: real implementation queries Google Calendar via MCP from dev-agent."""
    return [
        f"_(calendar stub — wire MCP query in dev-agent for {today.isoformat()})_",
    ]


def commitments_section() -> list[str]:
    text = _read(DOMAINS / "commitments.md")
    items: list[str] = []
    for header in ("Open RSVPs", "Upcoming appointments"):
        body = _section(text, header)
        for line in _non_placeholder_lines(body):
            items.append(line)
    return items


def news_section() -> list[str]:
    """STUB: real implementation runs news_fetch routine and reads scratch.

    Here we just print the configured topics so the brief is informative
    until the fetcher is wired.
    """
    if not TOPICS.exists():
        return []
    cfg = yaml.safe_load(TOPICS.read_text()) or {}
    topics = cfg.get("topics") or {}
    out = ["_(news fetch stub — top topics from topics.yaml:)_"]
    ranked = sorted(topics.items(), key=lambda kv: kv[1].get("weight", 0), reverse=True)
    for name, spec in ranked[:MAX_NEWS_ITEMS]:
        kw = ", ".join(spec.get("keywords", [])[:4])
        out.append(f"- **{name}** — keywords: {kw}")
    return out


def breakfast_section() -> list[str]:
    text = _read(DOMAINS / "health.md")
    nutrition = _section(text, "Nutrition")
    lines = _non_placeholder_lines(nutrition)
    if not lines:
        return ["_(no nutrition profile yet — fill health.md `## Nutrition` to enable suggestions)_"]
    return [
        "Based on profile in health.md:",
        *(f"  {line}" for line in lines[:3]),
        "→ Suggestion: see profile and choose accordingly (LLM suggestion lands here at activation).",
    ]


def scout_section() -> list[str]:
    ledger = _read(SCOUT / "ledger.md")
    body = _section(ledger, "Entries")
    if not body or body.startswith("_("):
        return []
    out: list[str] = []
    for line in body.splitlines():
        if line.startswith("### ") and len(out) < MAX_SCOUT_ITEMS:
            out.append(line.lstrip("# ").strip())
    return out


# ---------- assembly ----------

def render(today: dt.date) -> str:
    lines: list[str] = [f"# Morning brief — {today.strftime('%A, %d %B %Y')}", ""]

    def push(header: str, body: Iterable[str]) -> None:
        body_list = list(body)
        if not body_list:
            return
        lines.append(f"**{header}**")
        lines.extend(body_list)
        lines.append("")

    push("Today", calendar_section(today) + commitments_section())
    push("News", news_section())
    push("Breakfast", breakfast_section())
    push("Scout", scout_section())

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", help="YYYY-MM-DD (default: today)", default=None)
    args = p.parse_args()
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    sys.stdout.write(render(today))


if __name__ == "__main__":
    main()
