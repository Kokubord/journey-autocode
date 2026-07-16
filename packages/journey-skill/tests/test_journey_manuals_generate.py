import json
from pathlib import Path

from journey_skill.commands import journey_manuals_generate as mg
from typer.testing import CliRunner

runner = CliRunner()


def test_read_sources_emits_digest_json() -> None:
    repo = Path(__file__).resolve().parents[3]
    result = runner.invoke(mg.app, ["read-sources", "--repo-root", str(repo)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["project"] == "journey"
    assert any(a["id"] == "ADR-0018" for a in data["adrs"])


def test_write_manual_from_skill_payload(tmp_path: Path) -> None:
    payload = tmp_path / "m.json"
    payload.write_text(
        json.dumps(
            {
                "type": "user",
                "content": "# Manual do utilizador\nVer ADR-0001.",
                "language": "pt-BR",
            }
        ),
        encoding="utf-8",
    )
    result = runner.invoke(
        mg.app, ["write-manual", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    written = tmp_path / "docs" / "manuals" / "user.md"
    assert written.read_text(encoding="utf-8") == "# Manual do utilizador\nVer ADR-0001."


def test_write_manual_keeps_english_filename_for_other_language(tmp_path: Path) -> None:
    payload = tmp_path / "m.json"
    payload.write_text(
        json.dumps(
            {"type": "user", "content": "# User manual\nSee ADR-0001.", "language": "en-US"}
        ),
        encoding="utf-8",
    )
    result = runner.invoke(
        mg.app, ["write-manual", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert (
        tmp_path / "docs" / "manuals" / "user.md"
    ).exists()  # EN filename even with en-US content
