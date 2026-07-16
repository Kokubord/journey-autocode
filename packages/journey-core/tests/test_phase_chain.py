"""Tests for phase chaining (ATRITO-70) — next_phase + the actionable offer."""

from pathlib import Path

import journey_core
from journey_core.models.phase_state import Phase
from journey_core.phase_chain import build_phase_offer, next_phase


def test_next_phase_canonical_order() -> None:
    assert next_phase(Phase.WARMUP) is Phase.FOUNDATION
    assert next_phase(Phase.FOUNDATION) is Phase.DISCOVERY
    assert next_phase(Phase.DISCOVERY) is Phase.BUILD
    assert next_phase(Phase.BUILD) is Phase.RELEASE
    assert next_phase(Phase.RELEASE) is Phase.RUN


def test_run_has_no_next() -> None:
    # Last phase → no next; never fabricate a cycle (§7 Q3 / ATRITO-32).
    assert next_phase(Phase.RUN) is None


def test_offer_suggests_command_not_invokes() -> None:
    offer = build_phase_offer(Phase.FOUNDATION, "x")
    assert offer is not None
    # SUGGESTS the exact command (Q1) — the act of running it is the human confirmation.
    assert "/journey-phase-start discovery x" in offer


def test_offer_none_for_run() -> None:
    assert build_phase_offer(Phase.RUN) is None


def test_phase_end_skill_has_actionable_offer_and_suggests() -> None:
    repo = Path(journey_core.__file__).resolve().parents[4]
    text = (repo / ".claude" / "skills" / "journey-phase-end" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    # The offer line is present (the next-phase command) and SUGGESTS rather than invokes.
    assert "/journey-phase-start" in text
    assert "não invoca" in text.lower()
