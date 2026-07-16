"""Pre-flight decision for the non-dev launcher — the pure state machine (feature 015, ADR-0022).

Given an :class:`EnvironmentState`, decide the **branch**: usable → handoff to ``journey-init``;
otherwise → a guided ramp with concrete :class:`RemediationStep`s. The non-dev wall "WSL absent"
is a first-class branch here, and admin/reboot steps are **never** auto-resolved (clarify Q2 /
FR-003) — the launcher guides, the user acts.
"""

from __future__ import annotations

from journey_core.models.environment import (
    Branch,
    EnvironmentState,
    PreflightDecision,
    RemediationStep,
    Track,
)


def build_remediation(state: EnvironmentState) -> list[RemediationStep]:
    """Concrete remediation steps for an unusable environment (US2).

    Ordered by the dependency chain: WSL must exist (and be v2) before the agent matters.
    """
    steps: list[RemediationStep] = []
    if not state.wsl_available:
        steps.append(
            RemediationStep(
                key="install-wsl",
                description="Instalar o WSL2",
                auto_resolvable=False,
                requires_admin=True,
                requires_reboot=True,
                instruction=(
                    "O launcher prepara o comando `wsl --install`; voce o executa (pede "
                    "privilegio de administrador) e reinicia o computador. O launcher acompanha "
                    "e retoma apos o reboot — nunca roda admin nem reinicia por conta propria."
                ),
            )
        )
    elif not state.listing.has_wsl2_default:
        steps.append(
            RemediationStep(
                key="set-wsl2-default",
                description="Definir uma distribuicao WSL2 como padrao",
                auto_resolvable=False,
                requires_admin=False,
                requires_reboot=False,
                instruction=(
                    "Ha WSL, mas a distribuicao padrao nao esta em WSL2. O launcher mostra o "
                    "passo para definir/atualizar uma distro para a versao 2 e revalida."
                ),
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
                instruction=(
                    "O launcher indica como instalar o IDE/agente e conecta-lo ao runtime WSL."
                ),
            )
        )
    return steps


def decide(state: EnvironmentState, *, allow_fast_path: bool = False) -> PreflightDecision:
    """Branch the pre-flight: handoff when usable, otherwise a guided ramp.

    ``allow_fast_path`` lets an experienced user (dev) take the self-serve track when the
    environment is already usable (US3, ATRITO-04). Never claims ready when it is not (SC-002).
    """
    if state.usable:
        track = Track.SELF_SERVE if allow_fast_path else Track.GUIDED
        return PreflightDecision(
            branch=Branch.HANDOFF,
            track=track,
            reason="ambiente usavel — handoff ao journey-init (Camada 1)",
            remediation=[],
        )
    return PreflightDecision(
        branch=Branch.RAMP,
        track=Track.GUIDED,
        reason="ambiente ausente/incompleto — rampa guiada",
        remediation=build_remediation(state),
    )
