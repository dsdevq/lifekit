"""Morning brief generator — composes a brief from a lifekit instance.

Reads from the instance root (default: ~/.life/, override with LIFEKIT_ROOT).
Calendar and Telegram layers are intentionally stubbed — those are runtime
concerns wired by your orchestrator.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml

from ..core.paths import life_root

MAX_NEWS_ITEMS = 3
MAX_SCOUT_ITEMS = 2


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def _section(text: str, header: str, level: int = 2) -> str:
    """Extract a markdown section by header at the given level.

    A section ends at the next header of the same OR shallower level.
    Example: a `## X` section ends at the next `## Y` or top of file; a
    `### Sub` section ends at the next `### Other` or any `## Top`.
    """
    body = _strip_frontmatter(text)
    marker = "#" * level
    m = re.search(rf"(?im)^{marker}\s+{re.escape(header)}\s*$", body)
    if not m:
        return ""
    start = m.end()
    # find next header of level <= current
    levels = "|".join("#" * lv for lv in range(1, level + 1))
    nxt = re.search(rf"(?im)^(?:{levels})\s+", body[start:])
    end = start + nxt.start() if nxt else len(body)
    return body[start:end].strip()


def _non_placeholder_lines(section_body: str) -> list[str]:
    out: list[str] = []
    for line in section_body.splitlines():
        s = line.strip()
        if not s or (s.startswith("_(") and s.endswith(")_")):
            continue
        out.append(s)
    return out


def _calendar_section(today: dt.date, root: Path) -> list[str]:
    return [f"_(calendar stub — wire your runtime's calendar integration for {today.isoformat()})_"]


def _commitments_section(root: Path) -> list[str]:
    text = _read(root / "domains" / "commitments.md")
    items: list[str] = []
    for header in ("Open RSVPs", "Upcoming appointments"):
        items.extend(_non_placeholder_lines(_section(text, header)))
    return items


def _news_section(root: Path) -> list[str]:
    topics_path = root / "topics.yaml"
    if not topics_path.exists():
        return []
    cfg = yaml.safe_load(topics_path.read_text()) or {}
    topics = cfg.get("topics") or {}
    if not topics:
        return []
    out = ["_(news fetch stub — top topics from topics.yaml:)_"]
    ranked = sorted(topics.items(), key=lambda kv: kv[1].get("weight", 0), reverse=True)
    for name, spec in ranked[:MAX_NEWS_ITEMS]:
        kw = ", ".join((spec.get("keywords") or [])[:4])
        out.append(f"- **{name}** — keywords: {kw}")
    return out


def _breakfast_section(root: Path) -> list[str]:
    text = _read(root / "domains" / "health.md")
    if not text:
        return ["_(no health.md found — fill it to enable suggestions)_"]

    nutrition = _section(text, "Nutrition", level=2)
    if not nutrition:
        return ["_(no `## Nutrition` section in health.md)_"]

    out: list[str] = []

    # Goals summary — first line of `### Goals` that mentions Mode
    goals = _section(nutrition, "Goals", level=3)
    mode_match = re.search(r"\*\*Mode:\*\*\s*([^\n]+)", goals)
    if mode_match:
        out.append(f"Mode: {mode_match.group(1).strip()}")
    protein_match = re.search(r"\*\*Protein target:\*\*\s*([^\n]+)", goals)
    if protein_match:
        out.append(f"Protein target: {protein_match.group(1).strip()}")

    # Typical breakfast pattern — first paragraph under `**Breakfast (typical):**`
    prefs = _section(nutrition, "Preferences — what I actually eat", level=3)
    if not prefs:
        prefs = _section(nutrition, "Preferences", level=3)
    if prefs:
        m = re.search(r"\*\*Breakfast[^\*]*\*\*\s*(.*?)(?=\n\*\*|\Z)", prefs, flags=re.DOTALL)
        if m:
            options = [
                ln.strip() for ln in m.group(1).strip().splitlines() if ln.strip().startswith("-")
            ]
            if options:
                out.append("Typical breakfast options:")
                out.extend(f"  {ln}" for ln in options[:3])

    if not out:
        return [
            "_(nutrition profile present but no goals/breakfast captured — fill those subsections)_"
        ]

    out.append("→ Suggestion composed by orchestrator at runtime; static brief stops here.")
    return out


def _scout_section(root: Path) -> list[str]:
    body = _section(_read(root / "scout" / "ledger.md"), "Entries")
    if not body or body.startswith("_("):
        return []
    out: list[str] = []
    for line in body.splitlines():
        if line.startswith("### ") and len(out) < MAX_SCOUT_ITEMS:
            out.append(line.lstrip("# ").strip())
    return out


def render(today: dt.date | None = None, root: Path | None = None) -> str:
    today = today or dt.date.today()
    root = root or life_root()
    lines: list[str] = [f"# Morning brief — {today.strftime('%A, %d %B %Y')}", ""]

    def push(header: str, body: Iterable[str]) -> None:
        body_list = list(body)
        if not body_list:
            return
        lines.append(f"**{header}**")
        lines.extend(body_list)
        lines.append("")

    push("Today", _calendar_section(today, root) + _commitments_section(root))
    push("News", _news_section(root))
    push("Breakfast", _breakfast_section(root))
    push("Scout", _scout_section(root))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    sys.stdout.write(render())


if __name__ == "__main__":
    main()
