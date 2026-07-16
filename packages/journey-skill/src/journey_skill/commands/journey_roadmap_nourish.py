"""journey-roadmap-nourish — deterministic mechanic for backfilling roadmap briefings.

ADR-0017 mechanical-conductor sub-pattern (ADR-0018, Fatia 5): a **thin skill**
(`.claude/skills/journey-roadmap-nourish/SKILL.md`) conducts the backfill — it reads each
unit's real sources and **authors** the rich ``briefing`` (judgment, ADR-0017) following the
tone directive; this **mechanic** does only the deterministic parts:

- ``list`` enumerates the units that still lack a briefing (phase/sub-phase by default),
  with each unit's ``summary_ref`` so the skill knows **where to read** — never fabricates.
- ``set-briefing`` persists an authored briefing, reusing the single source
  ``journey_core.briefing_ops`` (anti-drift; same write op as ``journey-phase-end``).

Boundary: backfill is forward-fill-agnostic — it nourishes any unit lacking a briefing,
including phases already completed before the mechanism existed (the go-live gap ADR-0018
§Consequências left open). The feature-005 generator stays deterministic and only preserves
the authored briefing via ``merge_authored``. Writes are routed through the repository runtime;
UNC paths are vetoed (ADR-0004).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Backfill missing roadmap briefings (ADR-0018, Fatia 5).")


@app.command("list")
def list_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    include_tasks: Annotated[
        bool, typer.Option(help="Also list task-level units (off by design — ATRITO-33).")
    ] = False,
) -> None:
    r"""List roadmap units missing a narrative field, with their source pointer (read-only).

    Output: one unit per line — ``<id>\t<level>\t<status>\t<missing>\t<name>\t<ref>`` — where
    ``<missing>`` lists which of briefing/deliverable/notes are still empty, and ``<ref>`` is the
    ``summary_ref`` the skill must READ to author them (referência, não cópia). A trailing summary
    line reports the count. Exits 0 with no unit lines when fully nourished.
    """
    from journey_core.briefing_ops import list_unnourished

    units = list_unnourished(Path(repo_root) / "roadmap.yaml", include_tasks=include_tasks)
    for u in units:
        ref = u.ref_doc or "—"
        if u.ref_doc and u.ref_anchor:
            ref = f"{u.ref_doc} {u.ref_anchor}"
        typer.echo(f"{u.id}\t{u.level}\t{u.status}\t{','.join(u.missing)}\t{u.name}\t{ref}")
    typer.echo(f"# {len(units)} unidade(s) com campo(s) de narrativa em falta", err=True)


@app.command("set-briefing")
def set_briefing_cmd(
    unit: Annotated[str, typer.Argument(help="Roadmap unit id (phase/sub-phase) to nourish.")],
    briefing: Annotated[
        str, typer.Argument(help="Authored briefing text (didactic/narrative; see tone directive).")
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Persist an authored briefing in roadmap.yaml (ADR-0018), reusing the single write source.

    The briefing TEXT is authored by the conducting skill following the tone directive
    (docs/design/roadmap-render-fase-a.md, secao Tom e qualidade); this verb only persists it
    via ``journey_core.briefing_ops`` (anti-drift). The regen preserves it (005 ``merge_authored``).
    """
    from journey_core.briefing_ops import set_briefing

    typer.echo(str(set_briefing(Path(repo_root) / "roadmap.yaml", unit, briefing)))


@app.command("set-deliverable")
def set_deliverable_cmd(
    unit: Annotated[str, typer.Argument(help="Roadmap unit id (phase/sub-phase) to nourish.")],
    deliverable: Annotated[
        str, typer.Argument(help="Authored deliverable text (popup 'Entregável').")
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Persist the authored ``deliverable`` (popup 'Entregável') — ADR-0018 Fatia 6.

    Authored by the conducting skill; this verb only persists it via the single source
    ``journey_core.briefing_ops`` (anti-drift). The regen preserves it (005 ``merge_authored``).
    """
    from journey_core.briefing_ops import set_deliverable

    typer.echo(str(set_deliverable(Path(repo_root) / "roadmap.yaml", unit, deliverable)))


@app.command("set-notes")
def set_notes_cmd(
    unit: Annotated[str, typer.Argument(help="Roadmap unit id (phase/sub-phase) to nourish.")],
    notes: Annotated[
        str, typer.Argument(help="Authored execution notes (the 'informações' column).")
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Persist the authored execution ``notes`` (history → 'informações' column) — Fatia 6.

    The "o que aconteceu" narrative from HANDOVER/git. Authored by the conducting skill; this
    verb only persists it via the single source ``journey_core.briefing_ops`` (anti-drift).
    """
    from journey_core.briefing_ops import set_notes

    typer.echo(str(set_notes(Path(repo_root) / "roadmap.yaml", unit, notes)))


@app.command("regen-roadmap")
def regen_roadmap_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Trigger the 005 roadmap regeneration so the nourished briefings render (invoke as CLI)."""
    import subprocess

    argv = ["journey-roadmap", "generate", "--repo", str(repo_root), "--output-dir", str(repo_root)]
    subprocess.run(argv, check=True, capture_output=True, text=True)
    typer.echo(str(Path(repo_root) / "roadmap.yaml"))


@app.command("set-atrito-narrative")
def set_atrito_narrative_cmd(
    ref: Annotated[str, typer.Argument(help="ATRITO ref to author (e.g. ATRITO-83).")],
    narrative: Annotated[
        str,
        typer.Argument(help="Authored didactic narrative (plain language for the non-dev ICP)."),
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Persist a didactic ATRITO narrative in docs/atrito-narratives.yaml (ADR-0046).

    The narrative TEXT is authored by the conducting skill (judgment, ADR-0017) for the non-dev
    ICP; this verb only persists it via ``journey_core.atrito_narrative_ops`` (single source).
    The Site reads it on-demand — it never gains an LLM (fronteira ADR-0032).
    """
    from journey_core.atrito_narrative_ops import set_atrito_narrative

    typer.echo(str(set_atrito_narrative(repo_root, ref, narrative)))


@app.command("list-unnarrated")
def list_unnarrated_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """List the ATRITOs (from the ledger) still lacking a didactic narrative — ALL, no heuristic."""
    from journey_core.atrito_narrative_ops import list_unnarrated

    refs = list_unnarrated(repo_root)
    if not refs:
        typer.echo("todos os ATRITOs têm narrativa.")
        return
    for ref in refs:
        typer.echo(ref)


def main() -> None:
    """Console-script entry point (`journey-roadmap-nourish`)."""
    app()
