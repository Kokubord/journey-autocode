"""Detected project state, read before any write (FR-001/FR-002, ADR-0004)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Runtime(StrEnum):
    """Execution runtime where the repository lives (ADR-0004 §7.6)."""

    NATIVE = "nativo"
    WSL_TUNNEL = "tunel_wsl"
    WINDOWS = "windows"


class Tier(StrEnum):
    """Adoption tier. Only ``standard`` is lived in H1; others deferred (FR-016)."""

    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


class ProjectState(BaseModel):
    """Diagnosis of the target project, captured before any write.

    The correct folder/project is the first gate (FR-001); an environment
    failure triggers stop-and-self-heal (FR-002, ATRITO-11).
    """

    runtime: Runtime
    os: str
    git_present: bool = False
    spec_kit_present: bool = False
    language: str = "pt-BR"
    tier: Tier = Tier.STANDARD
    ssh_ok: bool = False
    preexisting_artifacts: list[str] = Field(default_factory=list)
    folder_confirmed: bool = False
