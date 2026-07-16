"""Tests for journey-bootstrap (feature 016, FATIA pull) — --dry-run is network-free."""

from pathlib import Path

from journey_skill.commands.journey_bootstrap import app
from typer.testing import CliRunner

runner = CliRunner()

_URL = "https://github.com/owner/journey-base.git"


def test_dry_run_includes_explicit_target_url_only(tmp_path: Path) -> None:
    dest = tmp_path / "base"
    proj = tmp_path / "proj"
    result = runner.invoke(
        app,
        ["--origin-url", _URL, "--dest", str(dest), "--project-dir", str(proj), "--dry-run"],
    )
    assert result.exit_code == 0
    assert f"git clone --depth 1 {_URL} {dest}" in result.stdout
    assert f"--target {proj}" in result.stdout  # never the CWD
    assert "token" not in result.stdout.lower()


def test_dry_run_uvx_kind(tmp_path: Path) -> None:
    dest = tmp_path / "base"
    proj = tmp_path / "proj"
    result = runner.invoke(
        app,
        [
            "--origin-url",
            _URL,
            "--dest",
            str(dest),
            "--project-dir",
            str(proj),
            "--kind",
            "uvx",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert f"uvx --from git+{_URL}" in result.stdout


def test_refuses_non_empty_dest(tmp_path: Path) -> None:
    dest = tmp_path / "base"
    dest.mkdir()
    (dest / "x").write_text("y", encoding="utf-8")
    proj = tmp_path / "proj"
    result = runner.invoke(
        app,
        ["--origin-url", _URL, "--dest", str(dest), "--project-dir", str(proj), "--dry-run"],
    )
    assert result.exit_code == 2
    assert "não está vazia" in result.stdout


def test_refuses_existing_git_repo_target(tmp_path: Path) -> None:
    dest = tmp_path / "base"
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".git").mkdir()
    result = runner.invoke(
        app,
        ["--origin-url", _URL, "--dest", str(dest), "--project-dir", str(proj), "--dry-run"],
    )
    assert result.exit_code == 2
    assert "repositório git" in result.stdout


def test_refuses_same_dest_and_project_dir(tmp_path: Path) -> None:
    same = tmp_path / "x"
    result = runner.invoke(
        app,
        ["--origin-url", _URL, "--dest", str(same), "--project-dir", str(same), "--dry-run"],
    )
    assert result.exit_code == 2
    assert "distintas" in result.stdout
