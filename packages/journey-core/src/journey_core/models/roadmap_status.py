"""Canonical roadmap status enum + Portuguese labels — the SINGLE source (ADR-0015 §3).

Born in ``journey-roadmap`` (the cockpit), but both the cockpit render AND the ``/journey-report``
projection (which lives in ``journey-core`` and cannot import the roadmap package) need the same 10
states and the same Portuguese labels. Centralizing them here removes the duplication/drift and ends
the "slugish": the report rendered the raw English slug before; now it renders the PT label.
"""

from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    """The canonical qualitative states (Vision §5.2.3; ADR-0015 §3; +superseded ATRITO-73)."""

    DONE = "done"
    DONE_PROD = "done_prod"
    DONE_EARLY = "done_early"
    IN_EXECUTION = "in_execution"
    IN_PROGRESS = "in_progress"
    MERGED_STAGING = "merged_staging"
    STANDBY = "standby"
    NEXT = "next"
    FUTURE = "future"
    SUPERSEDED = "superseded"


STATUS_LABELS_PT: dict[Status, str] = {
    Status.DONE: "Concluída",
    Status.DONE_PROD: "Concluída em prod",
    Status.DONE_EARLY: "Concluída prematuramente",
    Status.IN_EXECUTION: "Em execução",
    Status.IN_PROGRESS: "Em curso",
    Status.MERGED_STAGING: "Mergeado em staging",
    Status.STANDBY: "Em standby / Pausado",
    Status.NEXT: "Próxima",
    Status.FUTURE: "Futura",
    Status.SUPERSEDED: "Substituída",
}


def label_pt(status: Status) -> str:
    """Return the canonical Portuguese label for a status (render side, §8.5)."""
    return STATUS_LABELS_PT[status]
