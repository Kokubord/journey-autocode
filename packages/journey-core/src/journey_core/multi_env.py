"""Multi-environment generalization of the pre-flight decision (feature 016, ADR-0024/0004).

Reuses the env-agnostic FATIA 1 (``Branch``/``Track``/``PreflightDecision``/``decide``) and
branches the readiness + remediation per ``Runtime`` (NATIVE/WSL_TUNNEL/WINDOWS, ADR-0004) — it
does **not** re-implement the decision. On a Windows host the target runtime is WSL (ADR-0004), so
``WSL_TUNNEL`` and ``WINDOWS`` both consume the WSL-centric decision; ``NATIVE`` (Ubuntu/Mac) gets
its own readiness. This is FATIA 1 of the redesigned bootstrap; the remote pull + token are later,
gated slices.
"""

from __future__ import annotations

from journey_core.models.environment import (
    Branch,
    EnvironmentState,
    PreflightDecision,
    RemediationStep,
    Track,
)
from journey_core.models.project_state import Runtime
from journey_core.preflight import decide


def build_native_remediation(state: EnvironmentState) -> list[RemediationStep]:
    """Remediation steps for an unusable NATIVE host (Ubuntu/Mac) — toolchain + agent."""
    steps: list[RemediationStep] = []
    if not state.toolchain_present:
        steps.append(
            RemediationStep(
                key="install-toolchain",
                description="Instalar a toolchain (Python 3.12+ / uv)",
                auto_resolvable=False,
                requires_admin=False,
                requires_reboot=False,
                instruction="O agente indica como instalar Python 3.12+/uv e revalida.",
            )
        )
    if not state.agent_present:
        steps.append(
            RemediationStep(
                key="install-agent",
                description="Instalar o IDE/agente",
                auto_resolvable=False,
                requires_admin=False,
                requires_reboot=False,
                instruction="O agente indica como instalar/conectar o IDE/agente.",
            )
        )
    return steps


def decide_for_runtime(
    runtime: Runtime, state: EnvironmentState, *, allow_fast_path: bool = False
) -> PreflightDecision:
    """Branch the pre-flight per detected ``Runtime`` (ADR-0004), reusing FATIA 1.

    - ``NATIVE`` (Ubuntu/Mac): readiness = toolchain + agent present.
    - ``WSL_TUNNEL`` / ``WINDOWS``: the target is WSL (ADR-0004) → reuse the WSL-centric ``decide``
      (a Windows host without WSL yields the install-wsl ramp). Never claims ready when it is not.
    """
    if runtime is Runtime.NATIVE:
        if state.toolchain_present and state.agent_present:
            track = Track.SELF_SERVE if allow_fast_path else Track.GUIDED
            return PreflightDecision(
                branch=Branch.HANDOFF,
                track=track,
                reason="ambiente nativo pronto (Ubuntu/Mac) — handoff ao journey-init",
                remediation=[],
            )
        return PreflightDecision(
            branch=Branch.RAMP,
            track=Track.GUIDED,
            reason="ambiente nativo incompleto — rampa guiada",
            remediation=build_native_remediation(state),
        )
    return decide(state, allow_fast_path=allow_fast_path)
