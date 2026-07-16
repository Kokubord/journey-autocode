"""Tests for the multi-environment pre-flight generalization (feature 016, FATIA 1)."""

from journey_core.models.environment import (
    Branch,
    EnvironmentState,
    Track,
    WslDistro,
    WslListing,
)
from journey_core.models.project_state import Runtime
from journey_core.multi_env import build_native_remediation, decide_for_runtime


def _wsl_ready() -> EnvironmentState:
    return EnvironmentState(
        wsl_available=True,
        listing=WslListing(
            distros=[WslDistro(name="Ubuntu", state="Running", version=2)],
            default_distro="Ubuntu",
        ),
        agent_present=True,
    )


def test_native_ready_handoff() -> None:
    d = decide_for_runtime(
        Runtime.NATIVE, EnvironmentState(toolchain_present=True, agent_present=True)
    )
    assert d.branch is Branch.HANDOFF
    assert d.remediation == []


def test_native_fast_path_self_serve() -> None:
    state = EnvironmentState(toolchain_present=True, agent_present=True)
    assert decide_for_runtime(Runtime.NATIVE, state, allow_fast_path=True).track is Track.SELF_SERVE


def test_native_no_toolchain_ramp() -> None:
    d = decide_for_runtime(
        Runtime.NATIVE, EnvironmentState(toolchain_present=False, agent_present=True)
    )
    assert d.branch is Branch.RAMP
    assert [s.key for s in d.remediation] == ["install-toolchain"]


def test_native_no_agent_ramp() -> None:
    d = decide_for_runtime(
        Runtime.NATIVE, EnvironmentState(toolchain_present=True, agent_present=False)
    )
    assert [s.key for s in d.remediation] == ["install-agent"]


def test_wsl_tunnel_reuses_fatia1_handoff() -> None:
    assert decide_for_runtime(Runtime.WSL_TUNNEL, _wsl_ready()).branch is Branch.HANDOFF


def test_windows_without_wsl_ramps_install_wsl() -> None:
    d = decide_for_runtime(
        Runtime.WINDOWS, EnvironmentState(wsl_available=False, agent_present=True)
    )
    assert d.branch is Branch.RAMP
    assert "install-wsl" in [s.key for s in d.remediation]


def test_toolchain_present_defaults_true() -> None:
    assert EnvironmentState().toolchain_present is True


def test_build_native_remediation_empty_when_ready() -> None:
    assert (
        build_native_remediation(EnvironmentState(toolchain_present=True, agent_present=True)) == []
    )
