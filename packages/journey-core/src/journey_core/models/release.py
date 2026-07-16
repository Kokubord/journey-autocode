"""Models for /journey-release-start (feature 009): RELEASE-NOTES + semver validation."""

from __future__ import annotations

import re

from pydantic import BaseModel

#: semver with an optional leading ``v`` (FR-001: v1.0.0, v1.2.3-beta.1).
SEMVER_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def is_semver(version: str) -> bool:
    """Whether ``version`` is a valid semver (optional leading ``v``) — FR-001."""
    return bool(SEMVER_RE.match(version))


class ReleaseEntry(BaseModel):
    """One commit in the release notes: short sha + summary + ADR refs parsed from the message."""

    sha: str
    summary: str
    adr_refs: list[int] = []


class ReleaseNotes(BaseModel):
    """RELEASE-NOTES grouped by commit type (FR-005) — derived from commits, never hand-compiled."""

    version: str
    features: list[ReleaseEntry] = []
    fixes: list[ReleaseEntry] = []
    decisions: list[ReleaseEntry] = []
    others: list[ReleaseEntry] = []
