"""Phase/sub-phase state for /journey-phase-start (feature 006, FR-001/002/003).

The six canonical phases (methodology §3.1 / Vision §4.4). The active phase is marked
in the HANDOVER ``Fase atual`` Meta row (see ``journey_core.parsers.phase``). The
per-phase checklists are **templated and deterministic** (ADR-0017 sub-pattern for the
mechanical conducting commands): the skill narrates them, it does not improvise them.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Phase(StrEnum):
    """The six canonical Journey phases (methodology §3.1)."""

    WARMUP = "warmup"
    FOUNDATION = "foundation"
    DISCOVERY = "discovery"
    BUILD = "build"
    RELEASE = "release"
    RUN = "run"

    @property
    def label(self) -> str:
        """Display label (capitalized) for HANDOVER markers and output."""
        return self.value.capitalize()


class PhaseState(BaseModel):
    """The phase/sub-phase being opened, with the previous state preserved.

    ``previous`` keeps the prior ``Fase atual`` value verbatim so the command never
    overwrites it blindly (FR-002).
    """

    phase: Phase
    slug: str
    active: bool = True
    previous: str | None = None

    @property
    def marker(self) -> str:
        """The HANDOVER ``Fase atual`` value written when the phase is opened (FR-003)."""
        return f"{self.phase.label} — sub-fase **{self.slug}** (ativa)"


# Templated, per-phase "what to expect" checklists (FR-005). Deterministic — the skill
# narrates these; it does not generate them (ADR-0017 mechanical-conductor sub-pattern).
PHASE_CHECKLISTS: dict[Phase, list[str]] = {
    Phase.WARMUP: [
        "Reunir a visão fundadora e o contexto inicial do produto.",
        "Preparar a adoção do Journey (próximo: Foundation via /journey-init).",
    ],
    Phase.FOUNDATION: [
        "Instalar a metodologia (/journey-init) e os artefactos da raiz.",
        "Confirmar o Opening/Closing Handshake operante.",
        "Próximo: Discovery (constituição, stack, licença).",
    ],
    Phase.DISCOVERY: [
        "Conduzir o workshop (/journey-discover): visão, ADRs, drafts de spec.",
        "Ratificar a constituição (speckit-constitution) e refinar specs (speckit-*).",
        "Gerar o roadmap inicial (/journey-roadmap). Critério de fim: spec+plan+tasks + roadmap.",
    ],
    Phase.BUILD: [
        "Executar o plano feature a feature (speckit-implement); não repensar escopo.",
        "A partir da 2ª sub-fase: uma branch + um PR por sub-fase (main protegida).",
        "Decisões materiais → ADR + commit DECISION; fechar com /journey-phase-end.",
    ],
    Phase.RELEASE: [
        "Validar pre-release num projeto piloto; gerar manuais.",
        "Publicação no PyPI exige autorização explícita do owner (irreversível).",
    ],
    Phase.RUN: [
        "Acompanhar qualidade contínua e regressões (Regression Guard).",
        "Registar retrospectivas (/journey-retrospective).",
    ],
}


def checklist_for(phase: Phase) -> list[str]:
    """Return the templated checklist for ``phase`` (FR-005)."""
    return PHASE_CHECKLISTS[phase]
