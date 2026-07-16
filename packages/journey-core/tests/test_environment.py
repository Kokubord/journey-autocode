"""Tests for the launcher environment models (feature 015, FATIA 1)."""

from journey_core.models.environment import (
    Branch,
    EnvironmentState,
    RemediationStatus,
    RemediationStep,
    Track,
    WslDistro,
    WslListing,
)


def _wsl2_listing() -> WslListing:
    return WslListing(
        distros=[WslDistro(name="Ubuntu", state="Running", version=2)],
        default_distro="Ubuntu",
    )


def test_has_wsl2_default_true() -> None:
    assert _wsl2_listing().has_wsl2_default is True


def test_has_wsl2_default_false_when_v1() -> None:
    listing = WslListing(
        distros=[WslDistro(name="Ubuntu", state="Running", version=1)],
        default_distro="Ubuntu",
    )
    assert listing.has_wsl2_default is False


def test_has_wsl2_default_false_when_no_default() -> None:
    listing = WslListing(distros=[WslDistro(name="Ubuntu", state="Running", version=2)])
    assert listing.has_wsl2_default is False


def test_has_wsl2_default_false_when_default_not_in_list() -> None:
    listing = WslListing(
        distros=[WslDistro(name="Ubuntu", state="Running", version=2)],
        default_distro="Debian",
    )
    assert listing.has_wsl2_default is False


def test_usable_true_full_env() -> None:
    state = EnvironmentState(wsl_available=True, listing=_wsl2_listing(), agent_present=True)
    assert state.usable is True


def test_usable_false_when_wsl_absent() -> None:
    assert EnvironmentState(wsl_available=False, agent_present=True).usable is False


def test_usable_false_when_agent_absent() -> None:
    state = EnvironmentState(wsl_available=True, listing=_wsl2_listing(), agent_present=False)
    assert state.usable is False


def test_usable_ignores_repo_present() -> None:
    # repo creation is journey-init's concern, not the environment ramp's
    state = EnvironmentState(
        wsl_available=True, listing=_wsl2_listing(), agent_present=True, repo_present=False
    )
    assert state.usable is True


def test_remediation_step_defaults_pending() -> None:
    step = RemediationStep(
        key="k",
        description="d",
        auto_resolvable=False,
        requires_admin=True,
        requires_reboot=True,
        instruction="i",
    )
    assert step.status is RemediationStatus.PENDING


def test_enum_values() -> None:
    assert Track.GUIDED.value == "guided"
    assert Branch.HANDOFF.value == "handoff"
