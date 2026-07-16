"""Tests for the Scope Guard models (feature 014)."""

from journey_core.models.scope import RITE_STAGES, ScopeTrigger


def test_three_triggers_one_rite() -> None:
    assert {t.value for t in ScopeTrigger} == {"auto", "manual", "emergent"}
    assert len(list(ScopeTrigger)) == 3  # one mechanism, three triggers (FR-001)


def test_rite_has_four_firm_stages() -> None:
    assert len(RITE_STAGES) == 4
    assert RITE_STAGES[0].startswith("Reabrir a Visão")
    assert RITE_STAGES[-1] == "ADR de escopo"
