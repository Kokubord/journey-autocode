"""Conducted execution plan — replaces the manual master prompt (design level).

This is a DESIGN-level model: the concrete checkpoint-engine architecture is
implementation (Build) and is deliberately NOT pinned here (plan.md / ATRITO-54).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SubPhase(StrEnum):
    """Ordered Foundation sub-phases (methodology §3.1)."""

    PRE_IDE = "pre_ide"
    NA_IDE = "na_ide"
    VALIDACAO = "validacao"


class Checkpoint(BaseModel):
    """A pause point requiring explicit human approval (FR-005)."""

    label: str
    requires_human_gate: bool = True


class Step(BaseModel):
    """A single conducted step. The step count is not fixed (FR-005)."""

    description: str
    sub_phase: SubPhase


class ExecutionPlan(BaseModel):
    """Conducted plan over the three sub-phases, with human-gated checkpoints.

    No step is skipped; the run pauses at each checkpoint for approval (FR-005).
    """

    sub_phases: list[SubPhase] = Field(
        default_factory=lambda: [SubPhase.PRE_IDE, SubPhase.NA_IDE, SubPhase.VALIDACAO]
    )
    steps: list[Step] = []
    checkpoints: list[Checkpoint] = []
    fast_path: bool = False
