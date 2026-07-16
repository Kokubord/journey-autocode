"""Environment pre-flight models for the non-dev launcher (feature 015, ADR-0022).

The launcher is **Camada 0** — it runs on a bare Windows host (outside WSL/Python) and answers
"is a usable environment present?", branching **READY → handoff to journey-init** vs
**ABSENT → guided ramp**. These models are the **pure** core (FATIA 1); the actual ``wsl.exe``
gathering and the PowerShell artifact (ADR-0023) are later, manual-validation slices.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class WslDistro(BaseModel):
    """A single distribution reported by ``wsl -l -v``."""

    name: str
    state: str
    version: int


class WslListing(BaseModel):
    """The parsed result of ``wsl -l -v`` — the installed distributions and the default one."""

    distros: list[WslDistro] = []
    default_distro: str | None = None

    @property
    def has_wsl2_default(self) -> bool:
        """True when the default distribution exists and runs on WSL **version 2**."""
        if self.default_distro is None:
            return False
        return any(d.name == self.default_distro and d.version == 2 for d in self.distros)


class Track(StrEnum):
    """Which path the user takes — non-dev guided ramp vs dev fast-path (ATRITO-12/04)."""

    GUIDED = "guided"
    SELF_SERVE = "self_serve"


class Branch(StrEnum):
    """The pre-flight branch decision (ADR-0022)."""

    HANDOFF = "handoff"  # ambiente usável → entrega ao journey-init (Camada 1)
    RAMP = "ramp"  # ambiente ausente/incompleto → rampa guiada


class RemediationStatus(StrEnum):
    """Lifecycle of a remediation step — never silently 'done' (SC-002, zero false-success)."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class RemediationStep(BaseModel):
    """One step the ramp guides or escalates (US2). Admin/reboot steps are never auto-resolved."""

    key: str
    description: str
    auto_resolvable: bool
    requires_admin: bool
    requires_reboot: bool
    instruction: str
    status: RemediationStatus = RemediationStatus.PENDING


class EnvironmentState(BaseModel):
    """The readiness facts gathered by the pre-flight (the gathering itself is a later slice)."""

    wsl_available: bool = False
    listing: WslListing = Field(default_factory=WslListing)
    agent_present: bool = False
    repo_present: bool = False
    toolchain_present: bool = True  # NATIVE (Ubuntu/Mac) readiness — feature 016

    @property
    def usable(self) -> bool:
        """True only when WSL2 is the default **and** the agent is present.

        Never inferred loosely — a launcher must not report ready when it is not (SC-002). The
        project folder (``repo_present``) is the concern of ``journey-init`` (Camada 1), not of the
        environment ramp, so it does not gate ``usable``.
        """
        return self.wsl_available and self.listing.has_wsl2_default and self.agent_present


class PreflightDecision(BaseModel):
    """The pre-flight outcome — the branch, the track, and any remediation steps."""

    branch: Branch
    track: Track
    reason: str
    remediation: list[RemediationStep] = []
