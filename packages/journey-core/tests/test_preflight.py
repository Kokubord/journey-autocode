"""Tests for the pre-flight decision state machine (feature 015, FATIA 1)."""

from journey_core.models.environment import (
    Branch,
    EnvironmentState,
    Track,
    WslDistro,
    WslListing,
)
from journey_core.preflight import build_remediation, decide


def _ready() -> EnvironmentState:
    return EnvironmentState(
        wsl_available=True,
        listing=WslListing(
            distros=[WslDistro(name="Ubuntu", state="Running", version=2)],
            default_distro="Ubuntu",
        ),
        agent_present=True,
    )


def test_ready_env_hands_off_guided_by_default() -> None:
    decision = decide(_ready())
    assert decision.branch is Branch.HANDOFF
    assert decision.track is Track.GUIDED
    assert decision.remediation == []


def test_ready_env_fast_path_is_self_serve() -> None:
    decision = decide(_ready(), allow_fast_path=True)
    assert decision.branch is Branch.HANDOFF
    assert decision.track is Track.SELF_SERVE


def test_wsl_absent_is_first_class_ramp() -> None:
    decision = decide(EnvironmentState(wsl_available=False, agent_present=True))
    assert decision.branch is Branch.RAMP
    assert decision.track is Track.GUIDED
    keys = [s.key for s in decision.remediation]
    assert "install-wsl" in keys


def test_wsl_absent_step_never_auto_resolves_and_needs_admin_reboot() -> None:
    decision = decide(EnvironmentState(wsl_available=False))
    step = next(s for s in decision.remediation if s.key == "install-wsl")
    assert step.auto_resolvable is False  # never runs admin/reboot itself (Q2/FR-003)
    assert step.requires_admin is True
    assert step.requires_reboot is True


def test_wsl_v1_default_yields_set_wsl2_step() -> None:
    state = EnvironmentState(
        wsl_available=True,
        listing=WslListing(
            distros=[WslDistro(name="Ubuntu", state="Running", version=1)],
            default_distro="Ubuntu",
        ),
        agent_present=True,
    )
    keys = [s.key for s in decide(state).remediation]
    assert keys == ["set-wsl2-default"]


def test_agent_absent_yields_install_agent_step() -> None:
    state = EnvironmentState(
        wsl_available=True,
        listing=WslListing(
            distros=[WslDistro(name="Ubuntu", state="Running", version=2)],
            default_distro="Ubuntu",
        ),
        agent_present=False,
    )
    keys = [s.key for s in decide(state).remediation]
    assert keys == ["install-agent"]


def test_build_remediation_empty_when_usable() -> None:
    assert build_remediation(_ready()) == []
