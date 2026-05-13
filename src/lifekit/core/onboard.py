"""`lifekit onboard` — bootstrap an instance from a global-context file.

Reads `~/.claude/CLAUDE.md` (or any path via `--from`), drafts domain files,
and marks fields that can't be inferred as `_(needs your input — <specific>)_`.

LLM path: if `ANTHROPIC_API_KEY` is set AND `anthropic` is importable, calls
Claude to do real bootstrap. Otherwise stub-mode: writes a clear marker so
the user knows nothing was inferred. Tests run in stub-mode by default.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .paths import templates_root

DOMAIN_NAMES = [
    "career",
    "engineering",
    "learning",
    "health",
    "commitments",
    "ideas",
    "finance",
]


@dataclass
class OnboardResult:
    target: Path
    source: Path | None
    domains_written: list[str]
    used_llm: bool
    overwritten: bool
    notes: list[str]


def _default_source() -> Path | None:
    candidates = [
        Path.home() / ".claude" / "CLAUDE.md",
        Path.home() / ".cursor" / "CLAUDE.md",
        Path.home() / ".config" / "claude" / "CLAUDE.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _has_anthropic() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def _call_llm(source_text: str, domain: str) -> str | None:
    """Ask Claude to draft a domain file based on the source context.

    Returns the draft Markdown (with frontmatter), or None on failure.
    """
    try:
        import anthropic

        client = anthropic.Anthropic()
        system_prompt = (
            "You are bootstrapping a personal-AI memory store. "
            "Given the user's global-context document, draft the specified "
            "domain file. Output ONLY the Markdown with YAML frontmatter. "
            "Use the format from lifekit templates. Mark fields you cannot "
            "infer as `_(needs your input — <one-line specific question>)_`."
        )
        user_prompt = (
            f"Domain: {domain}\n\n"
            f"User's CLAUDE.md context:\n---\n{source_text}\n---\n\n"
            f"Draft ~/.life/domains/{domain}.md now."
        )
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text  # type: ignore[union-attr]
    except Exception as e:
        print(f"  ! LLM call for {domain} failed: {e}")
        return None


def _stub_domain(template_text: str, source_present: bool) -> str:
    """Inject onboarding markers into a template when LLM isn't available."""
    note = (
        "\n\n<!-- onboard stub: LLM not available. "
        "Set ANTHROPIC_API_KEY and reinstall lifekit with the [llm] extra "
        "to enable LLM-driven drafting. "
        f"Source context {'detected' if source_present else 'not found'}. -->\n"
    )
    return template_text + note


def onboard(
    target: Path | None = None,
    source: Path | None = None,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> OnboardResult:
    """Bootstrap domain files in `target` from the global-context `source`."""
    from .paths import life_root

    target = target or life_root()
    source = source or _default_source()
    notes: list[str] = []

    if source is not None and not source.exists():
        raise FileNotFoundError(f"source not found: {source}")

    source_text = source.read_text(encoding="utf-8") if source else ""

    if not target.exists() or not (target / "domains").exists():
        raise FileNotFoundError(
            f"no lifekit instance at {target}. Run `lifekit init` first."
        )

    # Check if instance already has populated domains
    populated = False
    domains_dir = target / "domains"
    for name in DOMAIN_NAMES:
        f = domains_dir / f"{name}.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        # populated if frontmatter has a non-TODO last_updated
        if "last_updated: TODO" not in text and "_(needs your input" not in text[:500]:
            populated = True
            break

    if populated and not force:
        raise FileExistsError(
            f"{target} appears already populated. Re-run with force=True to overwrite."
        )

    use_llm = _has_anthropic() and source_text != ""
    if not use_llm and source is not None:
        notes.append(
            "LLM not configured — wrote stub markers in each domain. "
            "Install lifekit[llm] and set ANTHROPIC_API_KEY for real drafting."
        )

    templates_dir = templates_root() / "domains"
    written: list[str] = []

    for name in DOMAIN_NAMES:
        template_file = templates_dir / f"{name}.md"
        if not template_file.exists():
            notes.append(f"missing template for {name}, skipping")
            continue
        template_text = template_file.read_text(encoding="utf-8")

        if use_llm:
            drafted = _call_llm(source_text, name)
            content = drafted if drafted else _stub_domain(template_text, source is not None)
        else:
            content = _stub_domain(template_text, source is not None)

        if dry_run:
            written.append(name)
            continue

        target_file = domains_dir / f"{name}.md"
        target_file.write_text(content, encoding="utf-8")
        written.append(name)

    return OnboardResult(
        target=target,
        source=source,
        domains_written=written,
        used_llm=use_llm,
        overwritten=populated,
        notes=notes,
    )


def copy_templates_for_test(target: Path) -> None:
    """Helper for tests: lay down a fresh templates copy at target."""
    src = templates_root()
    target.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
