"""lifekit CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from ..core.init import init_instance
from ..core.paths import life_root


@click.group()
@click.version_option()
def cli() -> None:
    """lifekit — a file-based framework for building your own persistent AI collaborator."""


@cli.command("init")
@click.option("--target", type=click.Path(path_type=Path), default=None, help="Where to scaffold (default: ~/.life/)")
@click.option("--force", is_flag=True, help="Overwrite an existing non-empty instance.")
def cmd_init(target: Path | None, force: bool) -> None:
    """Create a new lifekit instance from bundled templates."""
    try:
        created = init_instance(target=target, force=force)
    except FileExistsError as e:
        click.echo(f"refused: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    click.echo(f"initialized at {created}")
    click.echo("next: edit domains/*.md and routines/workflows.yaml, then wire your runtime")


@cli.command("status")
def cmd_status() -> None:
    """Report on the current instance."""
    root = life_root()
    if not root.exists():
        click.echo(f"no instance at {root}. run `lifekit init`.")
        sys.exit(1)
    domains = sorted((root / "domains").glob("*.md")) if (root / "domains").exists() else []
    click.echo(f"instance: {root}")
    click.echo(f"  domains: {len(domains)} file(s)")
    click.echo(f"  routines config: {'present' if (root / 'routines' / 'workflows.yaml').exists() else 'missing'}")
    click.echo(f"  scout sources: {'present' if (root / 'scout' / 'sources.yaml').exists() else 'missing'}")


@cli.command("onboard")
@click.option("--from", "source", type=click.Path(path_type=Path), default=None,
              help="Source file (default: ~/.claude/CLAUDE.md or equivalent)")
@click.option("--target", type=click.Path(path_type=Path), default=None,
              help="Instance to bootstrap (default: $LIFEKIT_ROOT or ~/.life/)")
@click.option("--dry-run", is_flag=True, help="Show what would be written without touching files.")
@click.option("--force", is_flag=True, help="Overwrite a populated instance.")
def cmd_onboard(source: Path | None, target: Path | None, dry_run: bool, force: bool) -> None:
    """Bootstrap domain files from a global-context source.

    Looks for ~/.claude/CLAUDE.md by default. If ANTHROPIC_API_KEY is set
    and the `anthropic` package is installed (pip install lifekit[llm]),
    drafts each domain via Claude. Otherwise writes stub markers.
    """
    from ..core.onboard import onboard
    try:
        result = onboard(target=target, source=source, dry_run=dry_run, force=force)
    except FileNotFoundError as e:
        click.echo(f"refused: {e}", err=True)
        sys.exit(1)
    except FileExistsError as e:
        click.echo(f"refused: {e}", err=True)
        sys.exit(1)
    click.echo(f"target:  {result.target}")
    click.echo(f"source:  {result.source or '(none — stub mode)'}")
    click.echo(f"LLM:     {'on' if result.used_llm else 'off (stub mode)'}")
    click.echo(f"wrote:   {len(result.domains_written)} domain(s) {'[dry-run]' if dry_run else ''}")
    for note in result.notes:
        click.echo(f"note:    {note}")


@cli.command("run")
@click.argument("routine")
def cmd_run(routine: str) -> None:
    """Run a routine ad-hoc. Currently supported: morning-brief."""
    if routine in ("morning-brief", "morning_brief"):
        from ..routines.morning_brief import render
        click.echo(render(), nl=False)
        return
    click.echo(f"unknown routine: {routine}", err=True)
    click.echo("supported: morning-brief", err=True)
    sys.exit(2)


@cli.command("scout")
@click.option("--limit", type=int, default=40)
@click.option("--dry-run", is_flag=True)
def cmd_scout(limit: int, dry_run: bool) -> None:
    """Run a scout pass: fetch sources, score, write to ledger + proposals."""
    from ..scout.run_scout import run
    result = run(limit=limit, dry_run=dry_run)
    click.echo(f"items={result['items']}  grades={result['grades']}")
    if not dry_run:
        click.echo(f"ledger +{result['ledger_added']}  proposals +{result['proposals_added']}")


@cli.command("refresh")
@click.option("--dry-run", is_flag=True)
def cmd_refresh(dry_run: bool) -> None:
    """Update last_updated dates and surface gaps from proposals."""
    from ..system.refresh import run
    result = run(dry_run=dry_run)
    click.echo(f"date updates: {result['date_changes']}")
    click.echo(f"inferred gaps in gaps.md: {result['inferred_gaps']}")


@cli.command("emit")
@click.argument("target_format", type=click.Choice(["langgraph-workflows"]))
@click.option("--to", "out_path", type=click.Path(path_type=Path), required=True,
              help="Output file path (e.g. ~/projects/dev-agent/workflows.yaml)")
@click.option("--timezone", default="Europe/Dublin", show_default=True)
def cmd_emit(target_format: str, out_path: Path, timezone: str) -> None:
    """Emit canonical workflows.yaml into a runtime-specific format."""
    if target_format == "langgraph-workflows":
        from ..emitters.langgraph import emit
        path, n = emit(out_path.expanduser(), timezone=timezone)
        click.echo(f"wrote {path}")
        click.echo(f"  enabled routines: {n}")
        if n == 0:
            click.echo("  (no routines enabled — emitter wrote empty workflows list)")


if __name__ == "__main__":
    cli()
