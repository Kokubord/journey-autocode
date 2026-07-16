# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
"""Smoke tests for /journey-release-start (feature 009) — in a tmp git repo."""

from pathlib import Path

from git import Repo
from journey_skill.commands.journey_release_start import app
from typer.testing import CliRunner

runner = CliRunner()


def _repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "t")
        cw.set_value("user", "email", "t@e")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.0.0"\n', encoding="utf-8"
    )
    repo.index.add(["pyproject.toml"])
    repo.index.commit("feat: initial")
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    repo.index.add(["a.md"])
    repo.index.commit("DECISION(x): escolha [ADR-0001]")
    return repo


def test_preview_shows_notes_without_mutation(tmp_path: Path) -> None:
    _repo(tmp_path)
    result = runner.invoke(app, ["preview", "v1.0.0", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "versão: 0.0.0 → 1.0.0" in result.stdout
    assert "RELEASE NOTES — v1.0.0" in result.stdout
    assert "feat: initial" in result.stdout
    assert "ADR-0001" in result.stdout
    # no mutation
    assert not (tmp_path / "RELEASE-NOTES-v1.0.0.md").exists()
    assert not (tmp_path / "docs" / "release").exists()
    assert 'version = "0.0.0"' in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")


def test_start_creates_branch_bumps_writes_notes_and_stubs(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = runner.invoke(app, ["start", "v1.0.0", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "release/v1.0.0" in {head.name for head in repo.heads}
    assert 'version = "1.0.0"' in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert (tmp_path / "RELEASE-NOTES-v1.0.0.md").is_file()
    # US2: cutover/runbook scaffolds suggested
    cutover = tmp_path / "docs" / "release" / "cutover-plan-v1.0.0.md"
    runbook = tmp_path / "docs" / "release" / "runbook-v1.0.0.md"
    assert cutover.is_file()
    assert runbook.is_file()
    assert "preencher" in cutover.read_text(encoding="utf-8")  # scaffold, not fabricated content


def test_bad_version_exits_nonzero(tmp_path: Path) -> None:
    _repo(tmp_path)
    result = runner.invoke(app, ["preview", "1.0", "--repo-root", str(tmp_path)])
    assert result.exit_code == 1
