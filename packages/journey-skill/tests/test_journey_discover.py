import json
from pathlib import Path

import pytest
from journey_core.exceptions import WriteRoutingError
from journey_core.models import Adr, SpecDraft, Vision
from journey_skill.commands.journey_discover import (
    app,
    consolidate_vision,
    next_adr_number,
    read_context,
    scaffold_spec_draft,
    write_adr,
)
from typer.testing import CliRunner

runner = CliRunner()


def _adr(number: int) -> Adr:
    return Adr(
        number=number,
        slug="x",
        title="X",
        date="2026-06-17",
        author="rkokubo",
        contexto="c",
        decisao="d",
        consequencias="k",
        alternativas="a",
        referencias="r",
    )


def test_next_adr_number_empty_and_populated(tmp_path: Path) -> None:
    assert next_adr_number(tmp_path) == 1
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-a.md").write_text("x", encoding="utf-8")
    (adr_dir / "0002-b.md").write_text("x", encoding="utf-8")
    assert next_adr_number(tmp_path) == 3


def test_read_context_surfaces_preexisting_vision(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text("| **Fase atual** | Build |\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "JOURNEY-VISION.md").write_text("# Visão", encoding="utf-8")
    ctx = read_context(tmp_path)
    assert ctx["next_adr_number"] == 1
    assert ctx["preexisting_vision"]["exists"] is True  # type: ignore[index]
    assert ctx["handover"]["current_phase"] == "Build"  # type: ignore[index]


def test_consolidate_vision_writes_firm_target(tmp_path: Path) -> None:
    path = consolidate_vision(tmp_path, Vision(content="# Visão consolidada"))
    assert path == tmp_path / "docs" / "JOURNEY-VISION.md"
    assert path.read_text(encoding="utf-8") == "# Visão consolidada"


def test_write_adr_writes_canonical_file(tmp_path: Path) -> None:
    path = write_adr(tmp_path, _adr(17))
    assert path.name == "0017-x.md"
    assert path.read_text(encoding="utf-8").startswith("# ADR-0017 — X")


def test_scaffold_spec_draft_under_drafts(tmp_path: Path) -> None:
    path = scaffold_spec_draft(
        tmp_path, SpecDraft(feature_slug="journey-foo", title="Foo", content="# draft")
    )
    assert path == tmp_path / "specs" / "drafts" / "journey-foo.spec.md"
    assert path.read_text(encoding="utf-8") == "# draft"


def test_writes_veto_unc_path() -> None:
    with pytest.raises(WriteRoutingError):
        consolidate_vision("//wsl.localhost/ubuntu/repo", Vision(content="x"))


def test_cli_read_context(tmp_path: Path) -> None:
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    result = runner.invoke(app, ["read-context", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "next_adr_number" in result.stdout


def test_cli_write_adr(tmp_path: Path) -> None:
    payload = tmp_path / "adr.json"
    payload.write_text(_adr(20).model_dump_json(), encoding="utf-8")
    result = runner.invoke(
        app, ["write-adr", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert (tmp_path / "docs" / "adr" / "0020-x.md").exists()


def test_cli_consolidate_vision(tmp_path: Path) -> None:
    payload = tmp_path / "v.json"
    payload.write_text(Vision(content="# V").model_dump_json(), encoding="utf-8")
    result = runner.invoke(
        app, ["consolidate-vision", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert (tmp_path / "docs" / "JOURNEY-VISION.md").read_text(encoding="utf-8") == "# V"


def test_cli_scaffold_draft(tmp_path: Path) -> None:
    payload = tmp_path / "d.json"
    payload.write_text(
        SpecDraft(feature_slug="f", title="F", content="x").model_dump_json(), encoding="utf-8"
    )
    result = runner.invoke(
        app, ["scaffold-draft", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert (tmp_path / "specs" / "drafts" / "f.spec.md").exists()


def test_payload_roundtrip_adr(tmp_path: Path) -> None:
    payload = tmp_path / "adr.json"
    payload.write_text(_adr(18).model_dump_json(), encoding="utf-8")
    adr = Adr.model_validate_json(payload.read_text(encoding="utf-8"))
    assert adr.number == 18 and json.loads(payload.read_text())["slug"] == "x"
