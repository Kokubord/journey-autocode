"""Smoke tests for the /journey-scope-review read-context mechanic (feature 014)."""

import json
from pathlib import Path

from journey_skill.commands.journey_scope_review import app
from typer.testing import CliRunner

runner = CliRunner()


def _project(tmp_path: Path, *, vision: bool = True) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-x.md").write_text("# ADR-0001 — X\n", encoding="utf-8")
    (adr_dir / "0002-y.md").write_text("# ADR-0002 — Y\n", encoding="utf-8")
    (tmp_path / "roadmap.yaml").write_text("project: x\nphases: []\n", encoding="utf-8")
    if vision:
        (tmp_path / "docs" / "JOURNEY-VISION.md").write_text("# Visão\n", encoding="utf-8")


def test_read_context_emits_firm_inputs(tmp_path: Path) -> None:
    _project(tmp_path)
    result = runner.invoke(app, ["--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["vision_present"] is True
    assert data["adr_count"] == 2
    assert data["latest_adr"] == 2
    assert data["roadmap_present"] is True
    assert len(data["rite_stages"]) == 4  # the firm shape (ATRITO-34)


def test_read_context_honest_when_vision_absent(tmp_path: Path) -> None:
    _project(tmp_path, vision=False)
    result = runner.invoke(app, ["--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["vision_present"] is False  # never fabricated
    assert data["vision_path"] is None
