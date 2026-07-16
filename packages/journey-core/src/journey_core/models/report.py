"""Report model for /journey-report — the canonical 15-column table (feature 011, Vision §10.3).

The column SET is **described** from Vision §10.3 (l.1947-1972); the concrete serialization
(CSV/XLSX/PDF, types) is Build/ADR-candidate and is **not fixed here** (plan.md, ATRITO-54).
Tokens/Custo (FR-007) have no source yet → Optional, surfaced as ``pendente`` downstream;
``relevant_info`` (col-15) carries the authored ``notes`` (ADR-0018 F6). "Informações relevantes"
is a **distinct** column from the didactic context block (FR-003, the ``briefing``).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ReportLevel(StrEnum):
    """Row granularity (FR-002: dupla — fase executivo / tarefa operacional)."""

    PHASE = "phase"
    SUBPHASE = "subphase"
    TASK = "task"


#: The 15 canonical columns of §10.3, in order. Display labels are PT (the Vision's language).
CANONICAL_COLUMNS: tuple[str, ...] = (
    "Fase",
    "Sub-fase/tarefa",
    "Status",
    "% avanço",
    "Início planejado",
    "Conclusão planejado",
    "Início real",
    "Conclusão real",
    "Variação",
    "Decisões materiais",
    "Commits",
    "Sessões",
    "Tokens",
    "Custo (USD)",
    "Informações relevantes",
)


class ReportRow(BaseModel):
    """One row of the 15-column report (§10.3). Optional fields surface as pendente/—.

    ``level`` is structural (granularidade dupla, FR-002), not one of the 15 columns; it lets a
    downstream renderer filter executive (phase) vs operational (task) views.
    """

    level: ReportLevel
    phase: str  # 1. Fase
    unit: str  # 2. Sub-fase/tarefa ("" for a phase-level row)
    status: str  # 3. Status (one of the 9 slugs, ADR-0015)
    progress_pct: int | None = None  # 4. % avanço (derived from task statuses)
    planned_start: str | None = None  # 5. Início planejado
    planned_end: str | None = None  # 6. Conclusão planejado
    actual_start: str | None = None  # 7. Início real
    actual_end: str | None = None  # 8. Conclusão real
    variance_days: int | None = None  # 9. Variação (real − planejado, em dias)
    material_decisions: int | None = None  # 10. Decisões materiais
    commits: int | None = None  # 11. Commits
    sessions: int | None = None  # 12. Sessões
    tokens: int | None = None  # 13. Tokens (DEFERIDO — FR-007, pipeline post-hoc)
    cost_usd: float | None = None  # 14. Custo USD (DEFERIDO — FR-007)
    relevant_info: str | None = None  # 15. Informações relevantes (← node ``notes``, ADR-0018 F6)
    # Structural narrative for the US2 context block (FR-003) — NOT columns of §10.3:
    briefing: str | None = None  # didactic "o que é / para que serve" (ADR-0018)
    deliverable: str | None = None  # "Entregável" — distinct from briefing (ADR-0018 F6)


class ReportTable(BaseModel):
    """The tabular report: ordered rows projected from roadmap.yaml + the canonical columns."""

    project: str
    rows: list[ReportRow]

    @property
    def columns(self) -> tuple[str, ...]:
        """The 15 canonical column labels (§10.3), in order."""
        return CANONICAL_COLUMNS


class DecisionRow(BaseModel):
    """One material decision for the ``decisions`` report (FR-004) — an ADR on disk (FR-005).

    Listed, not interpreted: number + title + status + date, read from the ADR file header. Missing
    header fields stay ``None`` (surfaced as ``—``; never fabricated).
    """

    number: int
    title: str
    status: str | None = None
    date: str | None = None
