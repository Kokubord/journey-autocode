"""Smoke tests for the /journey-report command — types, formats, writing (feature 011)."""

from pathlib import Path
from typing import Any

import yaml
from journey_skill.commands.journey_report import app
from typer.testing import CliRunner

runner = CliRunner()


def _roadmap(tmp_path: Path) -> None:
    doc: dict[str, Any] = {
        "project": "journey",
        "phases": [
            {
                "id": "build",
                "name": "Build",
                "status": "in_execution",
                "planned": {"start": None, "end": None},
                "metrics": {
                    "actual_start": "2026-06-11",
                    "actual_end": None,
                    "material_decisions": 1,
                    "commits": 2,
                    "sessions": 1,
                    "tokens": None,
                    "cost_usd": None,
                },
                "subphases": [
                    {
                        "id": "011",
                        "name": "journey-report",
                        "status": "in_execution",
                        "briefing": "Gera os relatórios formais do projeto.",
                        "deliverable": "Relatórios em PDF/markdown/CSV.",
                        "notes": "Em curso — Fatia 1 entregue.",
                        "planned": {"start": None, "end": None},
                        "metrics": {
                            "actual_start": "2026-06-11",
                            "actual_end": None,
                            "material_decisions": 0,
                            "commits": 2,
                            "sessions": 1,
                            "tokens": None,
                            "cost_usd": None,
                        },
                        "tasks": [
                            {"id": "T001", "name": "scaffold", "status": "done"},
                            {"id": "T002", "name": "model", "status": "future"},
                        ],
                    }
                ],
            }
        ],
    }
    (tmp_path / "roadmap.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def _adr(tmp_path: Path) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "0001-primeira.md").write_text(
        "# ADR-0001 — Primeira decisão\n\n| Campo | Valor |\n|--|--|\n"
        "| Status | Aceito |\n| Data | 2026-06-01 |\n",
        encoding="utf-8",
    )


def test_default_status_writes_table_and_context(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(app, ["--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Relatório — journey" in result.stdout
    assert "Contexto por fase/etapa" in result.stdout
    assert "Gera os relatórios formais do projeto." in result.stdout
    assert "Em curso — Fatia 1 entregue." in result.stdout  # notes -> col-15
    assert list((tmp_path / "docs" / "reports").glob("status-*.md"))  # file written (FR-006)


def test_tabular_csv_writes_csv_file(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(
        app, ["--type", "tabular", "--format", "csv", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    files = list((tmp_path / "docs" / "reports").glob("tabular-*.csv"))
    assert len(files) == 1
    assert "Fase,Sub-fase/tarefa,Status" in files[0].read_text(encoding="utf-8")


def test_decisions_md_lists_adrs(tmp_path: Path) -> None:
    _adr(tmp_path)
    result = runner.invoke(app, ["--type", "decisions", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Relatório de decisões" in result.stdout
    assert "ADR-0001" in result.stdout
    assert "Primeira decisão" in result.stdout


def test_task_view_lists_tasks(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(
        app, ["--type", "tabular", "--level", "task", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "scaffold" in result.stdout


def test_deferred_type_fails_honestly(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--type", "phase-retrospective", "--repo-root", str(tmp_path)])
    assert result.exit_code == 1
    assert "ATRITO-65" in result.output


def test_deferred_format_fails_honestly(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(
        app, ["--type", "tabular", "--format", "pdf", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 1


def test_unknown_type_fails_honestly(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--type", "bogus", "--repo-root", str(tmp_path)])
    assert result.exit_code == 1
    assert "desconhecido" in result.output


def test_csv_rejected_for_status(tmp_path: Path) -> None:
    _roadmap(tmp_path)
    result = runner.invoke(
        app, ["--type", "status", "--format", "csv", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 1


def test_absent_roadmap_exits_nonzero(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--repo-root", str(tmp_path)])
    assert result.exit_code == 1
