"""Render a ReportTable to Markdown/CSV + the decisions report (feature 011).

A view **distinct** from the cockpit HTML (``journey-roadmap/render.py``) — no shared code by design
(a formal report vs a live cockpit) — but the same honesty vocabulary: dates dd/mm/yy, tokens/cost
``None`` → ``"pendente"`` (FR-007), absent dates/variance/per-task metrics → ``"—"``. ``% avanço``
is always a number (005-aligned). The CSV form carries the 15-column table only (narrative prose
does not fit a cell — honest per-format boundary). The decisions report (FR-004) lists ADRs.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable

from journey_core.models.report import (
    CANONICAL_COLUMNS,
    DecisionRow,
    ReportLevel,
    ReportRow,
    ReportTable,
)
from journey_core.models.roadmap_status import Status, label_pt

_PENDENTE = "pendente"  # deferred slot awaiting a real source (tokens/cost — FR-007)
_DASH = "—"  # absent / not-applicable value


def _esc(text: str) -> str:
    """Make a string safe for a Markdown table cell (escape pipes, flatten newlines)."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _date_br(iso: str | None) -> str:
    """dd/mm/yy from an ISO date string; ``—`` when absent (mirrors the cockpit ``dt()``)."""
    if not iso:
        return _DASH
    parts = iso.split("-")
    if len(parts) != 3:
        return _DASH
    year, month, day = parts
    return f"{day}/{month}/{year[2:]}"


def _pct(value: int | None) -> str:
    return _DASH if value is None else f"{value}%"


def _variance(days: int | None) -> str:
    return _DASH if days is None else f"{days}d"


def _int(value: int | None) -> str:
    return _DASH if value is None else str(value)


def _tokens(value: int | None) -> str:
    return _PENDENTE if value is None else str(value)


def _cost(value: float | None) -> str:
    return _PENDENTE if value is None else f"{value:.2f}"


def _status_label(slug: str) -> str:
    """PT label for a status slug (B5 — ends the slugish); unknown/empty → raw value or ``—``."""
    try:
        return label_pt(Status(slug))
    except ValueError:
        return slug or _DASH


def _values(row: ReportRow) -> list[str]:
    """The 15 raw cell values of one row, in §10.3 order, with honesty labels (no md-escaping)."""
    return [
        row.phase,
        row.unit,
        _status_label(row.status),
        _pct(row.progress_pct),
        _date_br(row.planned_start),
        _date_br(row.planned_end),
        _date_br(row.actual_start),
        _date_br(row.actual_end),
        _variance(row.variance_days),
        _int(row.material_decisions),
        _int(row.commits),
        _int(row.sessions),
        _tokens(row.tokens),
        _cost(row.cost_usd),
        row.relevant_info or _DASH,
    ]


def _select(table: ReportTable, granularity: str) -> list[ReportRow]:
    """Granularidade dupla (FR-002): ``task`` = task rows; otherwise phases + sub-phases."""
    if granularity == "task":
        return [r for r in table.rows if r.level is ReportLevel.TASK]
    return [r for r in table.rows if r.level is not ReportLevel.TASK]


def render_markdown(table: ReportTable, granularity: str = "phase") -> str:
    """Render the 15-column report as a GFM Markdown table."""
    rows = _select(table, granularity)
    header = "| " + " | ".join(CANONICAL_COLUMNS) + " |"
    separator = "| " + " | ".join(["---"] * len(CANONICAL_COLUMNS)) + " |"
    lines = [f"# Relatório — {table.project}", "", header, separator]
    lines.extend("| " + " | ".join(_esc(v) for v in _values(row)) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def render_csv(table: ReportTable, granularity: str = "phase") -> str:
    """Render the 15-column table as CSV (stdlib quoting). Narrative context is not included."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CANONICAL_COLUMNS)
    for row in _select(table, granularity):
        writer.writerow(_values(row))
    return buffer.getvalue()


def render_context(table: ReportTable) -> str:
    """Render the per-phase/sub-phase didactic context blocks (US2, FR-003) — separate from table.

    Each block carries the authored ``briefing`` and a distinct **Entregável** line
    (``deliverable``). Nodes without authored narrative are omitted (never fabricated).
    """
    blocks: list[str] = []
    for row in table.rows:
        if row.level is ReportLevel.TASK:
            continue
        if not (row.briefing or row.deliverable):
            continue
        title = row.phase if row.level is ReportLevel.PHASE else f"{row.phase} › {row.unit}"
        parts = [f"### {title}", "", row.briefing or _DASH]
        if row.deliverable:
            parts.extend(["", f"**Entregável:** {row.deliverable}"])
        blocks.append("\n".join(parts))
    if not blocks:
        return ""
    return "## Contexto por fase/etapa\n\n" + "\n\n".join(blocks) + "\n"


def render_decisions_md(decisions: Iterable[DecisionRow], project: str = "") -> str:
    """Render the ``decisions`` report (FR-004): a Markdown table of ADRs."""
    title = f"# Relatório de decisões — {project}" if project else "# Relatório de decisões"
    lines = [
        title,
        "",
        "| ADR | Título | Estado | Data |",
        "| --- | --- | --- | --- |",
    ]
    for d in decisions:
        lines.append(
            f"| ADR-{d.number:04d} | {_esc(d.title)} | {d.status or _DASH} | {d.date or _DASH} |"
        )
    return "\n".join(lines) + "\n"
