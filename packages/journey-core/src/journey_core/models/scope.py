"""Scope Guard models (feature 014, ATRITO-34).

One **rite**, three **triggers** (FR-001). The scope decision is recorded as a **regular ADR**
(reuse :mod:`journey_core.adr_ops` / :class:`journey_core.models.adr.Adr`, as ``/journey-decision``)
— no parallel scope-ADR model. The fine mechanics (auto-drift detector, exact scope-ADR format,
exact reentrant step-by-step) are **deferred — H2** (FR-007); this carries only the firm shape.
"""

from __future__ import annotations

from enum import StrEnum


class ScopeTrigger(StrEnum):
    """The 3 triggers of the single Scope Guard rite (FR-001) — all route to the same rite."""

    AUTO = "auto"  # detecção automática de deriva (o detector é FR-007, deferido H2)
    MANUAL = "manual"  # /journey-scope-review (gatilho explícito)
    EMERGENT = "emergent"  # detalhe emergente no Build


#: The 4 firm stages of the reentrant rite (shape from ATRITO-34; fine steps = FR-007 H2).
RITE_STAGES: tuple[str, ...] = (
    "Reabrir a Visão (delimitada)",
    "Discovery → ADRs",
    "Plano de impacto + roadmap (via spec 005)",
    "ADR de escopo",
)
