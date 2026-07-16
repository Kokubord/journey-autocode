"""Tests for the pull operations (feature 016, FATIA pull) — pure parts; real pull is manual."""

import subprocess
from collections.abc import Sequence
from pathlib import Path

from journey_core.models.knowledge_base import KnowledgeBaseSource, PullKind
from journey_core.pull_ops import (
    auth_failure_message,
    build_conduct_plan,
    build_handoff_command,
    build_pull_command,
    run_pull,
    unsafe_dir_reason,
)

_URL = "https://github.com/owner/journey-base.git"


def test_build_pull_command_git_clone_url_only() -> None:
    cmd = build_pull_command(KnowledgeBaseSource(url=_URL), "/tmp/base")
    assert cmd == ["git", "clone", "--depth", "1", _URL, "/tmp/base"]
    assert all("token" not in part.lower() for part in cmd)


def test_build_pull_command_uvx() -> None:
    cmd = build_pull_command(KnowledgeBaseSource(url=_URL, kind=PullKind.UVX), "/tmp/base")
    assert cmd[:3] == ["uvx", "--from", f"git+{_URL}"]


def test_auth_failure_message_is_honest_and_secretless() -> None:
    msg = auth_failure_message(KnowledgeBaseSource(url=_URL))
    assert _URL in msg
    assert "segredo" in msg
    assert "PAT" not in msg and "deploy key" not in msg


def _runner(returncode: int) -> object:
    def run(cmd: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(args=list(cmd), returncode=returncode)

    return run


def test_run_pull_success() -> None:
    r = run_pull(KnowledgeBaseSource(url=_URL), "/tmp/base", runner=_runner(0))  # type: ignore[arg-type]
    assert r.ok is True


def test_run_pull_failure_is_honest() -> None:
    src = KnowledgeBaseSource(url=_URL)
    r = run_pull(src, "/tmp/base", runner=_runner(1))  # type: ignore[arg-type]
    assert r.ok is False
    assert r.message == auth_failure_message(src)


def test_run_pull_tool_missing_is_honest() -> None:
    def boom(cmd: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
        raise FileNotFoundError

    src = KnowledgeBaseSource(url=_URL)
    r = run_pull(src, "/tmp/base", runner=boom)
    assert r.ok is False
    assert r.message == auth_failure_message(src)


def test_build_handoff_includes_explicit_target() -> None:
    cmd = build_handoff_command("/base/templates", "demo", "/new/proj")
    assert cmd == [
        "journey-init",
        "--project-name",
        "demo",
        "--target",
        "/new/proj",
        "--templates",
        "/base/templates",
    ]
    assert "--target" in cmd  # never defaults to the CWD


def test_unsafe_dir_reason_fresh_is_safe(tmp_path: Path) -> None:
    assert unsafe_dir_reason(str(tmp_path / "nope")) is None  # non-existent → fresh
    assert unsafe_dir_reason(str(tmp_path)) is None  # empty → safe


def test_unsafe_dir_reason_refuses_non_empty(tmp_path: Path) -> None:
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    reason = unsafe_dir_reason(str(tmp_path))
    assert reason is not None and "não está vazia" in reason


def test_unsafe_dir_reason_refuses_git_repo(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    reason = unsafe_dir_reason(str(tmp_path))
    assert reason is not None and "repositório git" in reason


def test_build_conduct_plan_pull_then_init_with_target() -> None:
    plan = build_conduct_plan(KnowledgeBaseSource(url=_URL), "/base", "/proj", "demo")
    assert len(plan) == 2
    assert plan[0][0] == "git"  # pull first
    assert plan[1][0] == "journey-init" and "--target" in plan[1]  # then init, target-safe


def test_build_handoff_with_remote_appends_remote() -> None:
    cmd = build_handoff_command(
        "/base/templates", "demo", "/proj", remote_url="git@github.com:u/r.git"
    )
    assert cmd[-2:] == ["--remote", "git@github.com:u/r.git"]
    assert "--target" in cmd


def test_build_handoff_without_remote_has_no_remote() -> None:
    assert "--remote" not in build_handoff_command("/base/templates", "demo", "/proj")


def test_build_conduct_plan_passes_remote() -> None:
    plan = build_conduct_plan(
        KnowledgeBaseSource(url=_URL), "/base", "/proj", "demo", remote_url="git@github.com:u/r.git"
    )
    assert "--remote" in plan[1]
