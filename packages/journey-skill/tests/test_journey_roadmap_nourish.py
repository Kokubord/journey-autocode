from pathlib import Path

import yaml
from journey_skill.commands import journey_roadmap_nourish as nr
from typer.testing import CliRunner

runner = CliRunner()


def _roadmap(tmp_path: Path) -> Path:
    p = tmp_path / "roadmap.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "project": "x",
                "generator_version": "0",
                "phases": [
                    {
                        "id": "build",
                        "name": "Build",
                        "status": "in_execution",
                        "summary": "b",
                        "summary_ref": {"doc": "methodology.md", "anchor": "#3.3"},
                        "subphases": [
                            {
                                "id": "001",
                                "name": "journey-init",
                                "status": "done",
                                "summary": "s",
                                "tasks": [{"id": "T001", "name": "t", "status": "done"}],
                            },
                            {
                                "id": "011",
                                "name": "journey-report",
                                "status": "done",
                                "summary": "r",
                                "briefing": "Já nutrido.",
                                "deliverable": "Relatórios.",
                                "notes": "Fatia 1.",
                                "tasks": [],
                            },
                        ],
                    }
                ],
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return p


def test_list_reports_missing_fields_and_ref(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(nr.app, ["list", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    # <id>\t<level>\t<status>\t<missing>\t<name>\t<ref>
    assert lines[0].startswith("build\t0\tin_execution\tbriefing,deliverable,notes\tBuild\t")
    assert "methodology.md #3.3" in lines[0]
    assert any(
        ln.startswith("001\t1\tdone\tbriefing,deliverable,notes\tjourney-init") for ln in lines
    )
    assert not any(ln.startswith("011") for ln in lines)  # fully nourished -> skipped


def test_set_all_three_fields_then_list_is_empty(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    root = str(tmp_path)
    for unit in ("build", "001"):
        assert (
            runner.invoke(
                nr.app, ["set-briefing", unit, f"Conceitual {unit}.", "--repo-root", root]
            ).exit_code
            == 0
        )
        assert (
            runner.invoke(
                nr.app, ["set-deliverable", unit, f"Entregável {unit}.", "--repo-root", root]
            ).exit_code
            == 0
        )
        assert (
            runner.invoke(
                nr.app, ["set-notes", unit, f"Histórico {unit}.", "--repo-root", root]
            ).exit_code
            == 0
        )
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    sub = data["phases"][0]["subphases"][0]
    assert sub["briefing"] == "Conceitual 001." and sub["deliverable"] == "Entregável 001."
    assert sub["notes"] == "Histórico 001."
    after = runner.invoke(nr.app, ["list", "--repo-root", root])
    assert [ln for ln in after.stdout.splitlines() if ln.strip()] == []


def test_set_briefing_unknown_id_fails(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(nr.app, ["set-notes", "999", "x", "--repo-root", str(tmp_path)])
    assert result.exit_code != 0
