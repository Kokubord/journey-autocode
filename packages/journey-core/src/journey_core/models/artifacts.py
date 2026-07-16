"""Canonical artifacts materialized by journey-init (FR-008)."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class ArtifactType(StrEnum):
    """Kind of canonical artifact (FR-008)."""

    HANDOVER = "handover"
    AGENTS = "agents"
    CLAUDE = "claude"
    GITIGNORE = "gitignore"
    README = "readme"
    CONTRIBUTING = "contributing"
    ROADMAP = "roadmap"
    ROADMAP_SEED = "roadmap_seed"
    ADR = "adr"
    CI = "ci"
    CONSTITUTION_PLACEHOLDER = "constitution_placeholder"
    ARCHIVE_DIR = "archive_dir"


class CanonicalArtifact(BaseModel):
    """A single canonical artifact the command must materialize.

    All artifacts must be present at the end (SC-001); none is overwritten
    blindly (FR-014).
    """

    path: Path
    type: ArtifactType
    origin: str = "template"
    required: bool = True
