"""Smoke tests for /journey-upgrade (feature 002) — Basic→Standard, non-destructive, gates."""

from pathlib import Path

from journey_core.models.project_state import Tier
from journey_skill.commands.journey_upgrade import app, compute_delta, detect_tier
from typer.testing import CliRunner

runner = CliRunner()


def _basic(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text(
        "# meu projeto\n", encoding="utf-8"
    )  # no .specify/ no specs/
    return tmp_path


def test_detect_tier_basic_standard_ambiguous(tmp_path: Path) -> None:
    assert detect_tier(tmp_path) is Tier.BASIC  # neither
    (tmp_path / ".specify").mkdir()
    assert detect_tier(tmp_path) is None  # only one -> ambiguous (escalate)
    (tmp_path / "specs").mkdir()
    assert detect_tier(tmp_path) is Tier.STANDARD  # both


def test_compute_delta_lists_missing(tmp_path: Path) -> None:
    delta = compute_delta(tmp_path, Tier.BASIC, Tier.STANDARD)
    assert "specs/" in delta.missing
    assert "CLAUDE.md" in delta.missing


def test_preview_does_not_write(tmp_path: Path) -> None:
    _basic(tmp_path)
    r = runner.invoke(app, ["preview", "--to", "standard", "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    assert "delta basic→standard" in r.stdout
    assert "specs/" in r.stdout
    assert not (tmp_path / "CLAUDE.md").exists()  # NO write


def test_apply_materializes_writes_adr_then_idempotent(tmp_path: Path) -> None:
    _basic(tmp_path)
    r = runner.invoke(app, ["apply", "--to", "standard", "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    assert (tmp_path / "CLAUDE.md").is_file()
    assert (tmp_path / "specs").is_dir()
    assert (tmp_path / ".specify" / "memory" / "constitution.md").is_file()
    assert "DECISION(meta): upgrade to standard" in r.stdout
    assert any("upgrade-basic-standard" in p.name for p in (tmp_path / "docs" / "adr").iterdir())
    # README (pre-existing) untouched
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# meu projeto\n"
    # 2nd apply -> idempotent
    r2 = runner.invoke(app, ["apply", "--to", "standard", "--repo-root", str(tmp_path)])
    assert r2.exit_code == 0
    assert "idempotente" in r2.stdout


def test_downgrade_is_circuit_breaker(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()
    (tmp_path / "specs").mkdir()  # Standard
    r = runner.invoke(app, ["apply", "--to", "basic", "--repo-root", str(tmp_path)])
    assert r.exit_code == 1
    assert "DOWNGRADE" in r.output


def test_enterprise_is_guard_only(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()
    (tmp_path / "specs").mkdir()  # Standard
    r = runner.invoke(app, ["apply", "--to", "enterprise", "--repo-root", str(tmp_path)])
    assert r.exit_code == 1
    assert "ATRITO-50" in r.output


def test_ambiguous_tier_escalates(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()  # only one -> ambiguous
    r = runner.invoke(app, ["preview", "--to", "standard", "--repo-root", str(tmp_path)])
    assert r.exit_code == 1
    assert "AMBÍGUO" in r.output


def test_apply_preserves_customized_claude_md(tmp_path: Path) -> None:
    _basic(tmp_path)
    (tmp_path / "CLAUDE.md").write_text(
        "# Regras do meu projeto\n\nNão apagar isto.\n", encoding="utf-8"
    )
    r = runner.invoke(app, ["apply", "--to", "standard", "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Não apagar isto." in content  # user content preserved (ATRITO-16, US4)
    assert "BEGIN JOURNEY" in content  # managed block inserted
