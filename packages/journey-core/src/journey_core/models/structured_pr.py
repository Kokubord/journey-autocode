"""Structured PR model for /journey-phase-end (feature 007, FR-003).

Renders the phase-closing PR body: "Decisões materiais desta fase" + ADRs criados +
checklist de revisão. The values are derived deterministically from the period's commits
(mechanic); the skill narrates/opens the PR (git conduzido, gate humano — ADR-0005).
"""

from __future__ import annotations

from pydantic import BaseModel

_DEFAULT_REVIEW = [
    "Bateria verde (ruff/format/mypy/pyright/pytest)",
    "HANDOVER consolidado",
    "ADRs do período listados",
    "Gate do owner para merge (sem squash — §6.4)",
]


class StructuredPR(BaseModel):
    """A phase-closing PR body in the canonical structure (FR-003)."""

    title: str
    material_decisions: list[str] = []
    adrs: list[int] = []
    review_checklist: list[str] = []

    def to_markdown(self) -> str:
        """Serialize the PR body: decisions + ADRs + review checklist."""
        lines = [f"# {self.title}", "", "## Decisões materiais desta fase", ""]
        lines += (
            [f"- {d}" for d in self.material_decisions]
            if self.material_decisions
            else ["- (nenhuma decisão material registada no período)"]
        )
        lines += ["", "## ADRs criados", ""]
        lines += [f"- ADR-{n:04d}" for n in self.adrs] if self.adrs else ["- (nenhum)"]
        lines += ["", "## Checklist de revisão", ""]
        lines += [f"- [ ] {c}" for c in (self.review_checklist or _DEFAULT_REVIEW)]
        lines += [""]
        return "\n".join(lines)
