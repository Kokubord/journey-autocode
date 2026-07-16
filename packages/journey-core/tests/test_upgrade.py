"""Tests for the tier-delta model (feature 002)."""

from journey_core.models.project_state import Tier
from journey_core.models.upgrade import TierDelta


def test_tier_delta_holds_missing() -> None:
    delta = TierDelta(from_tier=Tier.BASIC, to_tier=Tier.STANDARD, missing=["specs/", "CLAUDE.md"])
    assert delta.from_tier is Tier.BASIC
    assert delta.to_tier is Tier.STANDARD
    assert "specs/" in delta.missing


def test_tier_delta_defaults_empty() -> None:
    delta = TierDelta(from_tier=Tier.STANDARD, to_tier=Tier.STANDARD)
    assert delta.missing == []  # nothing missing -> idempotent target
