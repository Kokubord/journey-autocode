"""journey-bootstrap — pull the knowledge base, then hand off to journey-init (feature 016).

The pull origin is **configurable** (URL only — never a secret); access uses the **ambient git
credential** — this command **never** handles a secret and encodes **no broad access** (exactly one
configured URL). **Security by construction:** ``--dest`` and ``--project-dir`` (= journey-init
``--target``) must be **fresh** (empty/new, never a repo) and **distinct** — so the
bootstrap never writes over an existing project and journey-init never defaults to the CWD. The real
remote pull / GitHub auth is **manual-validated**; ``--dry-run`` prints the commands network-free.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from journey_core.models.knowledge_base import KnowledgeBaseSource, PullKind
from journey_core.pull_ops import (
    build_handoff_command,
    build_pull_command,
    run_pull,
    unsafe_dir_reason,
)

app = typer.Typer(
    add_completion=False,
    help="Pull the Journey knowledge base from the configurable origin, then hand off to 001.",
)


@app.callback(invoke_without_command=True)
def run(
    origin_url: Annotated[
        str, typer.Option(help="Configurable pull origin (URL only — never a secret).")
    ],
    dest: Annotated[
        str, typer.Option(help="Fresh dir for the pulled base (empty/new, never a repo).")
    ],
    project_dir: Annotated[
        str, typer.Option(help="Fresh project dir = journey-init --target (empty/new).")
    ],
    project_name: Annotated[
        str, typer.Option(help="Project codename for the handoff.")
    ] = "project",
    kind: Annotated[PullKind, typer.Option(help="Pull style.")] = PullKind.GIT_CLONE,
    dry_run: Annotated[bool, typer.Option(help="Print commands without running anything.")] = False,
) -> None:
    """Pull the base from the configured origin, then hand off to journey-init (reuse)."""
    source = KnowledgeBaseSource(url=origin_url, kind=kind)
    # Security by construction (before announcing or acting): distinct + fresh dirs only.
    if Path(dest).resolve() == Path(project_dir).resolve():
        typer.echo("Recuso: --dest e --project-dir devem ser pastas distintas.")
        raise typer.Exit(code=2)
    for value in (dest, project_dir):
        reason = unsafe_dir_reason(value)
        if reason is not None:
            typer.echo(reason)
            raise typer.Exit(code=2)
    handoff = build_handoff_command(f"{dest}/templates", project_name, project_dir)
    if dry_run:
        typer.echo("pull: " + " ".join(build_pull_command(source, dest)))
        typer.echo("handoff: " + " ".join(handoff))
        return
    result = run_pull(source, dest)
    typer.echo(result.message)
    if not result.ok:
        raise typer.Exit(code=1)
    typer.echo("handoff: " + " ".join(handoff))


def main() -> None:
    """Console-script entry point for ``journey-bootstrap``."""
    app()
