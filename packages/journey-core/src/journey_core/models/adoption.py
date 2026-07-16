"""Adoption decision recorded by journey-init (SC-003, ATRITO-31)."""

from __future__ import annotations

from pydantic import BaseModel


class AdoptionDecision(BaseModel):
    """The single owner commit that adopts the Journey methodology.

    The commit message is English with no ``Co-Authored-By`` trailer (ADR-0001,
    ATRITO-31) and is pushed to the remote (SC-003).
    """

    adr: str = "docs/adr/0001-adopcao-journey.md"
    commit_message: str = "DECISION(meta): adopt Journey methodology [ADR-0001]"
