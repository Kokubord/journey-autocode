"""Conducting mechanic for /journey-retrospective (feature 013).

Judgment-heavy (ADR-0017): the SKILL.md conducts the workshop — it facilitates the four sections
from the REAL versioned inputs and anchors every lesson in a citable source (propose-never-assert,
ATRITO-32). This mechanic is thin & **local** (no network): ``read-context`` gathers the phase
inputs (Closing blocks + ADRs + commits); ``record`` materializes
``docs/retrospectives/NNN-<slug>.md`` from the four sections the workshop produced; ``propose-adr``
reuses :class:`RetroProposal`/``adr_ops`` to draft a learning ADR. Operational metrics (FR-006) are
``pendente`` — the token pipeline is built (#123) but 013 does not wire it yet (deferred); never
fabricated. Facilitation format + incidents (FR-007) are DEFERRED. Reuses
``parsers.closing``/``parsers.adr``/``parsers.phase``/``parsers.git_state`` + ``adr_ops`` +
``retrospective_ops`` — nothing recreated.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from journey_core.adr_ops import next_adr_number, write_adr
from journey_core.exceptions import JourneyError
from journey_core.models.archaeology import RetroProposal
from journey_core.models.retrospective import METRICS_PENDING, Retrospective
from journey_core.parsers.adr import parse_adr_index
from journey_core.parsers.closing import parse_closing_blocks
from journey_core.parsers.git_state import commits_since_date
from journey_core.parsers.phase import read_active_phase
from journey_core.retrospective_ops import next_retro_number, write_retrospective

app = typer.Typer(add_completion=False, help="Retrospectiva estruturada de fase (feature 013).")

_ADR_DIR = "docs/adr"
_RETRO_DIR = "docs/retrospectives"
_HANDOVER = "HANDOVER.md"
_DEFAULT_DAYS = 30


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(1)


def _since_date(since: str) -> date:
    if since:
        try:
            return date.fromisoformat(since)
        except ValueError:
            _fail(f"--since inválido: {since!r} (use YYYY-MM-DD).")
    return date.today() - timedelta(days=_DEFAULT_DAYS)


@app.command("read-context")
def read_context(
    since: Annotated[str, typer.Option("--since", help="Data ISO (default 30 dias atrás).")] = "",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Emit the phase inputs (Closing blocks + ADRs + commits) as JSON for the skill — no write."""
    root = Path(repo_root)
    start = _since_date(since)
    try:
        commits = commits_since_date(root, start)
    except JourneyError as exc:
        _fail(str(exc))
    blocks = parse_closing_blocks(root / _HANDOVER)
    adrs = parse_adr_index(root / _ADR_DIR)
    payload = {
        "phase": read_active_phase(root / _HANDOVER),
        "since": start.isoformat(),
        "closing_blocks": [
            {
                "fase": b.fase,
                "subfase": b.subfase,
                "timestamp": b.timestamp,
                "adrs_criados": b.adrs_criados,
            }
            for b in blocks
        ],
        "adrs": [{"number": a.number, "slug": a.slug} for a in adrs],
        "commit_count": len(commits),
        "commits": [{"sha": c.sha[:7], "summary": c.summary} for c in commits],
        "metricas_operacionais": METRICS_PENDING,  # FR-006 — never fabricate
        "incidentes": (
            "FR-007 deferido — registro de incidentes (docs/incidents/) não desenhado nesta spec."
        ),
        "note": (
            "Insumos versionados; cada lição do workshop cita a origem (sem transcrição manual)."
        ),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("record")
def record(
    payload: Annotated[Path, typer.Option(help="JSON da Retrospectiva (4 secções) do workshop.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Mostra sem escrever.")] = False,
) -> None:
    """Write ``docs/retrospectives/NNN-<slug>.md`` from the four workshop sections (FR-003)."""
    try:
        retro = Retrospective.model_validate_json(payload.read_text(encoding="utf-8"))
    except ValueError as exc:  # includes the non-empty-source guard (anti-fabrication)
        _fail(f"retrospectiva inválida: {exc}")
    number = next_retro_number(Path(repo_root) / _RETRO_DIR)
    if dry_run:
        typer.echo(f"# RETROSPECTIVA {number:03d} (dry-run — nada escrito)\n")
        typer.echo(retro.to_markdown(number))
        return
    path = write_retrospective(Path(repo_root) / _RETRO_DIR, retro, number)
    typer.echo(f"escrita: {path}")


@app.command("propose-adr")
def propose_adr(
    payload: Annotated[Path, typer.Option(help="JSON com a RetroProposal do ADR de aprendizado.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Mostra sem escrever.")] = False,
) -> None:
    """Draft a LEARNING ADR (reuse RetroProposal/adr_ops; sources required)."""
    try:
        proposal = RetroProposal.model_validate_json(payload.read_text(encoding="utf-8"))
    except ValueError as exc:  # includes the non-empty-sources guard (propose-never-assert)
        _fail(f"proposta inválida: {exc}")
    adr = proposal.adr
    adr.number = next_adr_number(Path(repo_root) / _ADR_DIR)  # non-destructive (next free)
    flag = " [INCERTO — confirmar]" if proposal.uncertain else ""
    if dry_run:
        typer.echo(f"# ADR de aprendizado (dry-run — nada escrito) ADR-{adr.number:04d}{flag}")
        typer.echo(f"fontes: {', '.join(proposal.sources)}\n")
        typer.echo(adr.to_markdown())
        return
    path = write_adr(Path(repo_root) / _ADR_DIR, adr)
    typer.echo(f"ADR de aprendizado (status={adr.status.value}){flag}: {path}")
    typer.echo(f"fontes: {', '.join(proposal.sources)}")


def main() -> None:
    """Entry point for the ``journey-retrospective`` console script."""
    app()
