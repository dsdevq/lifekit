#!/usr/bin/env python3
"""Scout dry-run — fetches sources, scores via two lenses, writes to ledger + proposals.

Static portion (Phase 5.5):
  - Fetches RSS/HN/Reddit-JSON/GitHub for sources defined in sources.yaml.
  - Applies heuristic two-lens scoring (system + personal-tooling).
  - Appends new entries to scout/ledger.md.
  - Appends qualifying items (grade=worth-looking-at) to system/proposals.md.

LLM-driven adversarial scoring (the real value) is stubbed: items get a
heuristic grade based on keyword overlap with gaps.md + engineering.md +
learning.md. dev-agent's orchestrator replaces this stub at activation.

Usage:
  python3 ~/.life/scout/run_scout.py
  python3 ~/.life/scout/run_scout.py --dry-run     # don't write files
  python3 ~/.life/scout/run_scout.py --limit 5     # cap items
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not installed. Run: pip install pyyaml")

LIFE = Path.home() / ".life"
SOURCES = LIFE / "scout" / "sources.yaml"
LEDGER = LIFE / "scout" / "ledger.md"
PROPOSALS = LIFE / "system" / "proposals.md"
GAPS = LIFE / "system" / "gaps.md"
ARCH = LIFE / "system" / "architecture.md"
ENGINEERING = LIFE / "domains" / "engineering.md"
LEARNING = LIFE / "domains" / "learning.md"

UA = "Mozilla/5.0 (compatible; LifeScout/0.1; +personal-use)"
HTTP_TIMEOUT = 10


@dataclass
class Item:
    title: str
    url: str
    source: str
    summary: str = ""
    score_system: float = 0.0
    score_personal: float = 0.0
    grade: str = "probably-noise"
    lens: str = "system"

    @property
    def best_score(self) -> float:
        return max(self.score_system, self.score_personal)


# ---------- fetchers ----------

def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def fetch_hn(limit: int = 15) -> list[Item]:
    try:
        ids = json.loads(_http_get("https://hacker-news.firebaseio.com/v0/topstories.json"))[:limit]
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"  ! hn topstories failed: {e}", file=sys.stderr)
        return []
    items: list[Item] = []
    for sid in ids:
        try:
            story = json.loads(_http_get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"))
        except Exception:
            continue
        if not story:
            continue
        if story.get("score", 0) < 100:
            continue
        url = story.get("url") or f"https://news.ycombinator.com/item?id={sid}"
        items.append(
            Item(
                title=story.get("title", "(no title)"),
                url=url,
                source="hackernews",
                summary=story.get("text", "")[:200],
            )
        )
    return items


def fetch_rss(url: str, source_name: str, limit: int = 10) -> list[Item]:
    try:
        raw = _http_get(url)
    except Exception as e:
        print(f"  ! rss {source_name} failed: {e}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  ! rss parse {source_name}: {e}", file=sys.stderr)
        return []
    items: list[Item] = []
    # Try RSS 2.0
    for it in root.iter("item"):
        title_el = it.find("title")
        link_el = it.find("link")
        desc_el = it.find("description")
        if title_el is None or link_el is None:
            continue
        items.append(
            Item(
                title=(title_el.text or "").strip(),
                url=(link_el.text or "").strip(),
                source=source_name,
                summary=((desc_el.text or "") if desc_el is not None else "")[:200],
            )
        )
        if len(items) >= limit:
            break
    # Try Atom
    if not items:
        ns = "{http://www.w3.org/2005/Atom}"
        for it in root.iter(f"{ns}entry"):
            title_el = it.find(f"{ns}title")
            link_el = it.find(f"{ns}link")
            summary_el = it.find(f"{ns}summary")
            if title_el is None or link_el is None:
                continue
            href = link_el.attrib.get("href", "")
            items.append(
                Item(
                    title=(title_el.text or "").strip(),
                    url=href,
                    source=source_name,
                    summary=((summary_el.text or "") if summary_el is not None else "")[:200],
                )
            )
            if len(items) >= limit:
                break
    return items


def fetch_reddit(sub: str, limit: int = 10) -> list[Item]:
    url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit}"
    try:
        data = json.loads(_http_get(url))
    except Exception as e:
        print(f"  ! reddit {sub} failed: {e}", file=sys.stderr)
        return []
    items: list[Item] = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("score", 0) < 50:
            continue
        items.append(
            Item(
                title=d.get("title", "(no title)"),
                url="https://www.reddit.com" + d.get("permalink", ""),
                source=f"reddit:{sub}",
                summary=(d.get("selftext", "") or "")[:200],
            )
        )
    return items


# ---------- scoring ----------

def _keywords_from(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8").lower()
    # Crude: take wordlike tokens of length >=4, drop common stopwords.
    import re

    tokens = re.findall(r"[a-z][a-z0-9-]{3,}", text)
    stop = {
        "this", "that", "with", "from", "have", "will", "your", "what", "which",
        "their", "they", "them", "into", "more", "less", "than", "then", "when",
        "where", "would", "could", "should", "about", "after", "before", "been",
        "being", "very", "just", "like", "make", "made", "does", "doing", "much",
        "many", "some", "most", "such", "also", "only", "every", "each", "other",
        "name", "summary", "last", "updated", "tags", "active", "deferred",
        "current", "denys", "file", "files", "phase", "phases", "plan",
    }
    return {t for t in tokens if t not in stop}


def score_items(items: list[Item]) -> None:
    system_kw = _keywords_from(GAPS) | _keywords_from(ARCH)
    personal_kw = _keywords_from(ENGINEERING) | _keywords_from(LEARNING)

    for it in items:
        blob = f"{it.title} {it.summary}".lower()
        toks = set(blob.split())
        # crude overlap score normalized by item-token count
        denom = max(len(toks), 1)
        sys_hits = sum(1 for t in toks if t in system_kw)
        per_hits = sum(1 for t in toks if t in personal_kw)
        it.score_system = sys_hits / denom
        it.score_personal = per_hits / denom
        it.lens = "system" if it.score_system >= it.score_personal else "personal-tooling"
        # grading thresholds — tuned tight to avoid noise on a cold cache
        if it.best_score >= 0.04:
            it.grade = "worth-looking-at"
        elif it.best_score >= 0.02:
            it.grade = "maybe"
        else:
            it.grade = "probably-noise"


# ---------- writers ----------

def append_ledger(items: list[Item], today: dt.date) -> int:
    if not LEDGER.exists():
        return 0
    existing = LEDGER.read_text(encoding="utf-8")
    out_lines: list[str] = []
    for it in items:
        if it.url in existing:
            continue  # dedup hard against ledger
        out_lines.append(f"### {today.isoformat()} — {it.title}")
        out_lines.append(f"- **Lens:** {it.lens}")
        out_lines.append(f"- **Source:** {it.url}")
        out_lines.append(f"- **Initial grade:** {it.grade}")
        out_lines.append(
            f"- **Why flagged:** heuristic overlap "
            f"(system={it.score_system:.3f}, personal={it.score_personal:.3f})"
        )
        out_lines.append("- **Followup (7d):** _pending_")
        out_lines.append("- **Followup (30d):** _pending_")
        out_lines.append("")
    if not out_lines:
        return 0
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write("\n".join(out_lines))
    return len(out_lines) // 7  # entries are 7 lines + blank


def append_proposals(items: list[Item], today: dt.date) -> int:
    if not PROPOSALS.exists():
        return 0
    qualifying = [it for it in items if it.grade == "worth-looking-at"]
    if not qualifying:
        return 0
    existing = PROPOSALS.read_text(encoding="utf-8")
    out_lines: list[str] = []
    for it in qualifying:
        if it.url in existing:
            continue
        slug = "-".join(it.title.lower().split()[:5])[:60]
        out_lines.append(f"### {today.isoformat()}-{slug}")
        out_lines.append(f"- **Status:** new")
        out_lines.append(f"- **Lens:** {it.lens}")
        out_lines.append(f"- **Source:** {it.url}")
        out_lines.append(
            f"- **Why it matters:** heuristic match — "
            f"{it.lens} keywords overlap (review needed)"
        )
        out_lines.append("- **What changes:** _to evaluate_")
        out_lines.append("- **Effort:** _unknown_")
        out_lines.append("- **Risk:** _unknown_")
        out_lines.append("- **Notes:** auto-surfaced by scout dry-run; LLM scoring pending")
        out_lines.append("")
    if not out_lines:
        return 0
    with PROPOSALS.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write("\n".join(out_lines))
    return len([it for it in qualifying if it.url not in existing])


# ---------- main ----------

def gather_items(limit: int) -> list[Item]:
    cfg = yaml.safe_load(SOURCES.read_text()) or {}
    items: list[Item] = []

    # 1. Hacker News (always one source)
    print("Fetching: hackernews top stories...")
    items.extend(fetch_hn(limit=15))

    # 2. RSS blogs from sources.yaml
    for blog in (cfg.get("people") or {}).get("blogs") or []:
        name = blog.split("/")[2] if "//" in blog else blog
        print(f"Fetching: {name}")
        items.extend(fetch_rss(blog, name, limit=8))

    # 3. Reddit (one sub per run to keep rate-limit friendly)
    for sub in (cfg.get("reddit") or [])[:1]:
        sub_clean = sub.lstrip("r/")
        print(f"Fetching: reddit {sub_clean}")
        items.extend(fetch_reddit(sub_clean, limit=8))

    # cap total before scoring
    return items[:limit] if limit else items


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="don't write files")
    p.add_argument("--limit", type=int, default=40, help="max items to consider")
    args = p.parse_args()

    today = dt.date.today()
    print(f"Scout dry-run — {today.isoformat()}\n")

    items = gather_items(args.limit)
    print(f"\n{len(items)} items gathered.")

    score_items(items)

    by_grade: dict[str, int] = {}
    for it in items:
        by_grade[it.grade] = by_grade.get(it.grade, 0) + 1
    print(f"Grades: {by_grade}")

    if args.dry_run:
        print("\n--dry-run: not writing files.")
        for it in items[:10]:
            print(f"  [{it.grade:18}] [{it.lens:14}] {it.title[:80]}")
        return

    new_ledger = append_ledger(items, today)
    new_props = append_proposals(items, today)
    print(f"\nLedger: +{new_ledger} entries. Proposals: +{new_props} entries.")


if __name__ == "__main__":
    main()
