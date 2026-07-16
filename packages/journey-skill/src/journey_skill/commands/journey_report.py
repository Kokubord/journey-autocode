"""Conducting mechanic for /journey-report (feature 011).

``journey-skill`` does NOT import ``journey-roadmap`` (option 1a): it reads ``roadmap.yaml`` via
``journey_core.report_ops`` and renders via ``journey_core.report_render``. The report is a
**projection** of the roadmap (FR-009) — no re-collection, no fabrication (ADR-0018).

Types (FR-004): ``status`` (table + context, default) · ``tabular`` (15-col) · ``decisions``
(ADRs, via ``parse_adr_index``). Deferred: ``audit-trail`` (chronology), ``phase-retrospective``
(ATRITO-65 — Scope Guard), ``steering`` (ATRITO-50). Formats (FR-006): ``md`` · ``csv`` (15-col
tabular only). Deferred: ``xlsx``/``pdf`` (deps not adopted; ATRITO-50). Writes
``docs/reports/<type>-YYYY-MM-DD.<fmt>`` and echoes the content.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from journey_core.exceptions import JourneyError
from journey_core.report_ops import project_decisions, project_report, write_report
from journey_core.report_render import (
    render_context,
    render_csv,
    render_decisions_md,
    render_markdown,
)

app = typer.Typer(add_completion=False, help="Generate the formal report (§10.3, feature 011).")

_SUPPORTED_TYPES = ("status", "tabular", "decisions")
_DEFERRED_TYPES = {
    "audit-trail": "cronologia git+sessões — fatia futura",
    "phase-retrospective": "histórico por fase — ATRITO-65 (Scope Guard)",
    "steering": "Enterprise/PDF assinado — ATRITO-50",
}
_SUPPORTED_FORMATS = ("md", "csv")
_DEFERRED_FORMATS = {
    "xlsx": "requer dependência não adotada",
    "pdf": "requer dependência não adotada — use print→PDF do navegador sobre o md (ATRITO-50)",
}


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(1)


def _build(report_type: str, report_format: str, level: str, repo_root: Path) -> str:
    """Render the report content for a (type, format) pair, or fail honestly on an invalid combo."""
    if report_type == "decisions":
        if report_format != "md":
            _fail("--format=csv é só para --type=tabular; use --type=decisions --format=md.")
        return render_decisions_md(project_decisions(repo_root))
    try:
        table = project_report(repo_root / "roadmap.yaml")
    except JourneyError as exc:
        _fail(str(exc))
    if report_type == "tabular":
        return render_csv(table, level) if report_format == "csv" else render_markdown(table, level)
    # status (table + didactic context)
    if report_format == "csv":
        _fail("--format=csv não disponível para --type=status (use --type=tabular para CSV).")
    return render_markdown(table, level) + "\n" + render_context(table)


@app.callback(invoke_without_command=True)
def report(
    report_type: Annotated[
        str, typer.Option("--type", help="status | tabular | decisions.")
    ] = "status",
    report_format: Annotated[
        str, typer.Option("--format", help="md | csv (csv = tabular).")
    ] = "md",
    level: Annotated[
        str, typer.Option(help="Granularidade: phase (executivo) | task (operacional).")
    ] = "phase",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Generate the report (§10.3): writes docs/reports/<type>-YYYY-MM-DD.<fmt> and echoes it.

    Honesty: tokens/custo are pendentes (FR-007); fields without a real source surface as pendente/—
    and are never fabricated (ADR-0018). Deferred types/formats fail with a clear message.
    """
    if report_type in _DEFERRED_TYPES:
        _fail(f"--type={report_type} diferido: {_DEFERRED_TYPES[report_type]}.")
    if report_type not in _SUPPORTED_TYPES:
        _fail(
            f"--type={report_type} desconhecido. Suportados: {', '.join(_SUPPORTED_TYPES)}. "
            f"Diferidos: {', '.join(_DEFERRED_TYPES)}."
        )
    if report_format in _DEFERRED_FORMATS:
        _fail(f"--format={report_format} diferido: {_DEFERRED_FORMATS[report_format]}.")
    if report_format not in _SUPPORTED_FORMATS:
        _fail(
            f"--format={report_format} desconhecido. Suportados: {', '.join(_SUPPORTED_FORMATS)}."
        )

    content = _build(report_type, report_format, level, Path(repo_root))
    filename = f"{report_type}-{date.today().isoformat()}.{report_format}"
    path = write_report(repo_root, filename, content)
    typer.echo(content)
    typer.echo(f"escrito: {path}", err=True)


def main() -> None:
    """Entry point for the ``journey-report`` console script."""
    app()
