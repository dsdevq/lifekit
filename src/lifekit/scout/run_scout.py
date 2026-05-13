"""Scout dry-run — fetches sources, scores via two lenses, writes to ledger + proposals.

Reads the instance root from `lifekit.core.paths.life_root()` (override with
LIFEKIT_ROOT env var).
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import yaml

from ..core.paths import life_root

UA = "Mozilla/5.0 (compatible; lifekit-scout/0.0.1; +personal-use)"
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


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def _fetch_hn(limit: int = 15) -> list[Item]:
    try:
        ids = json.loads(_http_get("https://hacker-news.firebaseio.com/v0/topstories.json"))[:limit]
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"  ! hn topstories failed: {e}", file=sys.stderr)
        return []
    items: list[Item] = []
    for sid in ids:
        try:
            s = json.loads(_http_get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"))
        except Exception:
            continue
        if not s or s.get("score", 0) < 100:
            continue
        url = s.get("url") or f"https://news.ycombinator.com/item?id={sid}"
        items.append(Item(title=s.get("title", "(no title)"), url=url, source="hackernews", summary=(s.get("text", "") or "")[:200]))
    return items


def _fetch_rss(url: str, source_name: str, limit: int = 10) -> list[Item]:
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
    for it in root.iter("item"):
        t = it.find("title"); l = it.find("link"); d = it.find("description")
        if t is None or l is None:
            continue
        items.append(Item(title=(t.text or "").strip(), url=(l.text or "").strip(), source=source_name, summary=((d.text or "") if d is not None else "")[:200]))
        if len(items) >= limit:
            break
    if not items:
        ns = "{http://www.w3.org/2005/Atom}"
        for it in root.iter(f"{ns}entry"):
            t = it.find(f"{ns}title"); l = it.find(f"{ns}link"); s = it.find(f"{ns}summary")
            if t is None or l is None:
                continue
            items.append(Item(title=(t.text or "").strip(), url=l.attrib.get("href", ""), source=source_name, summary=((s.text or "") if s is not None else "")[:200]))
            if len(items) >= limit:
                break
    return items


def _fetch_reddit(sub: str, limit: int = 10) -> list[Item]:
    url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit}"
    try:
        data = json.loads(_http_get(url))
    except Exception as e:
        print(f"  ! reddit {sub} failed: {e}", file=sys.stderr)
        return []
    items: list[Item] = []
    for c in data.get("data", {}).get("children", []):
        d = c.get("data", {})
        if d.get("score", 0) < 50:
            continue
        items.append(Item(title=d.get("title", "(no title)"), url="https://www.reddit.com" + d.get("permalink", ""), source=f"reddit:{sub}", summary=(d.get("selftext", "") or "")[:200]))
    return items


def _keywords_from(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8").lower()
    tokens = re.findall(r"[a-z][a-z0-9-]{3,}", text)
    stop = {"this", "that", "with", "from", "have", "will", "your", "what", "which", "their", "they", "them", "into", "more", "less", "than", "then", "when", "where", "would", "could", "should", "about", "after", "before", "been", "being", "very", "just", "like", "make", "made", "does", "doing", "much", "many", "some", "most", "such", "also", "only", "every", "each", "other", "name", "summary", "last", "updated", "tags", "active", "deferred", "current", "file", "files", "phase", "phases", "plan"}
    return {t for t in tokens if t not in stop}


def _score(items: list[Item], root: Path) -> None:
    system_kw = _keywords_from(root / "system" / "gaps.md") | _keywords_from(root / "system" / "architecture.md")
    personal_kw = _keywords_from(root / "domains" / "engineering.md") | _keywords_from(root / "domains" / "learning.md")
    for it in items:
        blob = f"{it.title} {it.summary}".lower()
        toks = set(blob.split())
        denom = max(len(toks), 1)
        sys_hits = sum(1 for t in toks if t in system_kw)
        per_hits = sum(1 for t in toks if t in personal_kw)
        it.score_system = sys_hits / denom
        it.score_personal = per_hits / denom
        it.lens = "system" if it.score_system >= it.score_personal else "personal-tooling"
        it.grade = "worth-looking-at" if it.best_score >= 0.04 else ("maybe" if it.best_score >= 0.02 else "probably-noise")


def _append_ledger(items: list[Item], today: dt.date, root: Path) -> int:
    path = root / "scout" / "ledger.md"
    if not path.exists():
        return 0
    existing = path.read_text(encoding="utf-8")
    out: list[str] = []
    for it in items:
        if it.url in existing:
            continue
        out += [
            f"### {today.isoformat()} — {it.title}",
            f"- **Lens:** {it.lens}",
            f"- **Source:** {it.url}",
            f"- **Initial grade:** {it.grade}",
            f"- **Why flagged:** heuristic overlap (system={it.score_system:.3f}, personal={it.score_personal:.3f})",
            "- **Followup (7d):** _pending_",
            "- **Followup (30d):** _pending_",
            "",
        ]
    if not out:
        return 0
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(out))
    return len(out) // 8


def _append_proposals(items: list[Item], today: dt.date, root: Path) -> int:
    path = root / "system" / "proposals.md"
    if not path.exists():
        return 0
    qualifying = [it for it in items if it.grade == "worth-looking-at"]
    if not qualifying:
        return 0
    existing = path.read_text(encoding="utf-8")
    out: list[str] = []
    written = 0
    for it in qualifying:
        if it.url in existing:
            continue
        slug = "-".join(it.title.lower().split()[:5])[:60]
        out += [
            f"### {today.isoformat()}-{slug}",
            "- **Status:** new",
            f"- **Lens:** {it.lens}",
            f"- **Source:** {it.url}",
            "- **Why it matters:** heuristic match — review needed",
            "- **What changes:** _to evaluate_",
            "- **Effort:** _unknown_",
            "- **Risk:** _unknown_",
            "- **Notes:** auto-surfaced by scout; LLM scoring pending",
            "",
        ]
        written += 1
    if not out:
        return 0
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(out))
    return written


def run(*, limit: int = 40, dry_run: bool = False, root: Path | None = None) -> dict:
    root = root or life_root()
    sources_path = root / "scout" / "sources.yaml"
    cfg = yaml.safe_load(sources_path.read_text()) if sources_path.exists() else {}
    items: list[Item] = []

    items.extend(_fetch_hn(limit=15))
    for blog in (cfg.get("people") or {}).get("blogs") or []:
        name = blog.split("/")[2] if "//" in blog else blog
        items.extend(_fetch_rss(blog, name, limit=8))
    for sub in (cfg.get("reddit") or [])[:1]:
        items.extend(_fetch_reddit(sub.lstrip("r/"), limit=8))

    if limit:
        items = items[:limit]
    _score(items, root)

    grades: dict[str, int] = {}
    for it in items:
        grades[it.grade] = grades.get(it.grade, 0) + 1

    new_ledger = new_props = 0
    if not dry_run:
        today = dt.date.today()
        new_ledger = _append_ledger(items, today, root)
        new_props = _append_proposals(items, today, root)

    return {"items": len(items), "grades": grades, "ledger_added": new_ledger, "proposals_added": new_props}


def main() -> None:
    result = run()
    print(f"items={result['items']}  grades={result['grades']}")
    print(f"ledger +{result['ledger_added']}  proposals +{result['proposals_added']}")


if __name__ == "__main__":
    main()
