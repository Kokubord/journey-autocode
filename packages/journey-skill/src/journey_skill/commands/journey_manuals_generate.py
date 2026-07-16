"""journey-manuals-generate — deterministic mechanic for the project manuals (feature 008).

ADR-0017 conducting pattern, **judgment-heavy pole** (como a 004 — skill **GROSSA**, não fina):
the in-session skill (`.claude/skills/journey-manuals-generate/SKILL.md`) reads the source
digest + the files and **SYNTHESIZES** the four canonical manuals of the TARGET project (PT by
default), then invokes this mechanic to persist them. This module is **deterministic**: emit a
light source digest and write skill-authored manual payloads — it does NOT synthesize content.

Writes routed through the runtime; UNC vetoed (ADR-0004). Manuals document the TARGET project,
not Journey (FR-007). Human review before commit is suggested (FR-009). The auto-trigger at
``/journey-phase-end`` in Build (FR-008) is **DEFERRED** (Build not lived) — manual invocation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from journey_core.manuals_ops import write_manual
from journey_core.models.manual import Manual
from journey_core.parsers.sources import source_digest

app = typer.Typer(help="Deterministic mechanic for /journey-manuals-generate (feature 008).")


@app.command("read-sources")
def read_sources_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print the light source digest as JSON for the skill to synthesize from (FR-003)."""
    typer.echo(source_digest(repo_root).model_dump_json(indent=2))


@app.command("write-manual")
def write_manual_cmd(
    payload: Annotated[Path, typer.Option(help="Manual JSON authored by the skill.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Write a skill-authored manual; suggest human review before commit (FR-001/009)."""
    manual = Manual.model_validate_json(payload.read_text(encoding="utf-8"))
    typer.echo(str(write_manual(repo_root, manual)))
    typer.echo("revisão humana antes do commit — não commitar cego (FR-009, ADR-0005)", err=True)


def main() -> None:
    """Console-script entry point (`journey-manuals-generate`)."""
    app()
