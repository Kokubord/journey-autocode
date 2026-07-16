import pytest
from journey_core.exceptions import WriteRoutingError
from journey_core.models.project_state import Runtime
from journey_core.writer import detect_runtime, guard_write_target, is_unc_path


def test_is_unc_path_detects_forward_slash_unc() -> None:
    assert is_unc_path("//wsl.localhost/ubuntu/home/x")
    assert is_unc_path("//wsl$/ubuntu/x")


def test_is_unc_path_detects_backslash_unc() -> None:
    assert is_unc_path(r"\\wsl.localhost\ubuntu\x")


def test_is_unc_path_allows_native() -> None:
    assert not is_unc_path("/home/rkokubo/projetos/journey")


def test_guard_write_target_rejects_unc() -> None:
    with pytest.raises(WriteRoutingError):
        guard_write_target("//wsl.localhost/ubuntu/x")


def test_guard_write_target_returns_path() -> None:
    assert str(guard_write_target("/home/x/file.txt")) == "/home/x/file.txt"


def test_detect_runtime_returns_runtime() -> None:
    assert isinstance(detect_runtime(), Runtime)
