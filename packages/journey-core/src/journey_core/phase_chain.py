"""Phase chaining (ATRITO-70) — offer the next phase at a boundary (reuse the canonical order).

Each phase skill, on completion, suggests the next phase's command — the act of running it is the
human confirmation (clarify Q1); never auto-fired, never an inter-skill invocation. The canonical
order is the single source ``Phase`` (no second hardcoded list). ``Run`` is the last phase → no next
(``None``); never fabricate a Run→Discovery cycle (clarify Q3 / ATRITO-32).
"""

from __future__ import annotations

from journey_core.models.phase_state import Phase

#: Canonical phase order = the ``Phase`` enum order (single source — reused, not recreated).
_ORDER: tuple[Phase, ...] = tuple(Phase)


def next_phase(current: Phase) -> Phase | None:
    """The phase after ``current`` in the canonical order, or ``None`` for the last (Run)."""
    i = _ORDER.index(current)
    return _ORDER[i + 1] if i + 1 < len(_ORDER) else None


def build_phase_offer(current: Phase, slug: str = "<slug>") -> str | None:
    """The actionable offer at the end of ``current`` — **suggest** the next command (clarify Q1).

    Returns ``None`` when ``current`` is the last phase (Run) — no fabricated cycle (Q3). The
    didactic 1-line description of the next phase is added by the conducting skill (§7 tone).
    """
    nxt = next_phase(current)
    if nxt is None:
        return None
    return (
        f"Fase **{current.value}** concluída. Próxima fase: **{nxt.value}**. "
        f"Iniciar agora? Rode `/journey-phase-start {nxt.value} {slug}`."
    )
