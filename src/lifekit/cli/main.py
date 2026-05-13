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
    click.echo("next: edit domains/*.md and routines/workflows.yaml, then run `lifekit onboard`")


@cli.command("status")
def cmd_status() -> None:
    """Report on the current ~/.life/ instance."""
    root = life_root()
    if not root.exists():
        click.echo(f"no instance at {root}. run `lifekit init`.")
        sys.exit(1)
    domains = sorted((root / "domains").glob("*.md")) if (root / "domains").exists() else []
    routines_file = root / "routines" / "workflows.yaml"
    click.echo(f"instance: {root}")
    click.echo(f"  domains: {len(domains)} file(s)")
    click.echo(f"  routines config: {'present' if routines_file.exists() else 'missing'}")
    click.echo(f"  scout sources: {'present' if (root / 'scout' / 'sources.yaml').exists() else 'missing'}")


@cli.command("onboard")
def cmd_onboard() -> None:
    """Interactive wizard to populate domain files (stub — not yet implemented)."""
    click.echo("onboard: not yet implemented.")
    click.echo("for now, edit ~/.life/domains/*.md by hand. see README.")


@cli.command("run")
@click.argument("routine", required=True)
def cmd_run(routine: str) -> None:
    """Run a routine ad-hoc (stub — wires into your orchestrator)."""
    click.echo(f"run {routine}: not yet implemented.")
    click.echo("planned: dispatch to your configured orchestrator adapter.")


@cli.command("scout")
@click.option("--lens", type=click.Choice(["system", "personal-tooling", "both"]), default="both")
@click.option("--dry-run", is_flag=True)
def cmd_scout(lens: str, dry_run: bool) -> None:
    """Run scout pass (stub — see examples/jane-doe/ for the reference implementation)."""
    click.echo(f"scout --lens={lens}: not yet implemented in this skeleton.")
    click.echo("reference implementation at examples/jane-doe/scout/run_scout.py.")


@cli.command("refresh")
def cmd_refresh() -> None:
    """Update last_updated dates and surface gaps from proposals (stub)."""
    click.echo("refresh: not yet implemented in this skeleton.")
    click.echo("reference implementation at examples/jane-doe/system/refresh.py.")


if __name__ == "__main__":
    cli()
