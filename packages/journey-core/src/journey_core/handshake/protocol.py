"""Handshake Protocol data structures and helpers (skeleton — Constituição §7.2).

The Opening Handshake confirms the agent read HANDOVER, the highest ADR, the
constitution, and git state. The Closing Handshake records the structured block
(ADR-0012). This module defines the shapes; full wiring is built incrementally.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class OpeningHandshake(BaseModel):
    """The opening confirmation produced at the start of every session."""

    handover_read: bool = False
    highest_adr: str | None = None
    constitution_version: str | None = None
    git_synced: bool = False
    summary: str = ""


class ClosingHandshake(BaseModel):
    """The structured closing block recorded in HANDOVER (ADR-0012)."""

    phase: str
    sub_phase: str
    session_id: str | None = None
    timestamp: str
    session_class: str
    relevant_work: bool = True
    adrs_created: list[str] = Field(default_factory=list)


def build_opening_handshake(
    *,
    handover_read: bool,
    highest_adr: str | None,
    constitution_version: str | None,
    git_synced: bool,
    summary: str,
) -> OpeningHandshake:
    """Assemble an :class:`OpeningHandshake` from the gathered session facts.

    Args:
        handover_read: Whether HANDOVER.md was read.
        highest_adr: Identifier of the highest-numbered ADR read.
        constitution_version: Ratified constitution version read.
        git_synced: Whether the working tree is synced with the remote.
        summary: One-line state summary.

    Returns:
        The assembled opening handshake.
    """
    return OpeningHandshake(
        handover_read=handover_read,
        highest_adr=highest_adr,
        constitution_version=constitution_version,
        git_synced=git_synced,
        summary=summary,
    )
