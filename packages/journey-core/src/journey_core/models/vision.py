"""Models for the Discovery workshop output (FR-001/002/005).

The consolidated vision is the central output; its write target is firm —
``docs/JOURNEY-VISION.md`` (ADR-0017 Decision 3, Vision §10.2). A pre-existing vision
is an *input* and is not blindly overwritten (FR-011). Reconciliation of a
differently-named founding document is deferred (ATRITO-63).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class WorkshopTopic(StrEnum):
    """Structured questions the workshop must cover (FR-001; Vision §6.4.1 W2)."""

    VISAO = "visao"
    PUBLICO_ALVO = "publico_alvo"
    PROBLEMA_CENTRAL = "problema_central"
    DIFERENCIAL = "diferencial"
    FREQUENCIA_USO = "frequencia_uso"
    ESTADO_ATUAL = "estado_atual"


WORKSHOP_QUESTIONS: dict[WorkshopTopic, str] = {
    WorkshopTopic.VISAO: "Qual é a visão do produto — o que ele é e aonde quer chegar?",
    WorkshopTopic.PUBLICO_ALVO: "Quem é o público-alvo (personas, ICP)?",
    WorkshopTopic.PROBLEMA_CENTRAL: "Qual é o problema central que o produto resolve?",
    WorkshopTopic.DIFERENCIAL: "Qual é o diferencial frente às alternativas?",
    WorkshopTopic.FREQUENCIA_USO: "Com que frequência o produto é usado?",
    WorkshopTopic.ESTADO_ATUAL: "Qual é o estado atual — o que já existe?",
}


class Gap(BaseModel):
    """An understanding gap, reported rather than filled by assumption (FR-002)."""

    topic: str
    description: str


class Vision(BaseModel):
    """Consolidated product vision — central output of the workshop (FR-005)."""

    path: str = "docs/JOURNEY-VISION.md"
    content: str
    sources: list[str] = []
    gaps: list[Gap] = []
