# pyright: reportPrivateUsage=false
"""Tests for the projector + decisions reader + report writer (feature 011)."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from journey_core.exceptions import JourneyError
from journey_core.models.report import ReportLevel
from journey_core.report_ops import project_decisions, project_report, write_report


def _write(tmp_path: Path, doc: dict[str, Any]) -> Path:
    p = tmp_path / "roadmap.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return p


def _doc() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project": "journey",
        "generator_version": "0",
        "phases": [
            {
                "id": "build",
                "name": "Build",
                "status": "in_execution",
                "planned": {"start": "2026-06-01", "end": "2026-06-10"},
                "metrics": {
                    "actual_start": "2026-06-02",
                    "actual_end": "2026-06-12",
                    "material_decisions": 3,
                    "commits": 9,
                    "sessions": 4,
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
                            {"id": "T002", "name": "model", "status": "done"},
                            {"id": "T003", "name": "projector", "status": "future"},
                            {"id": "T004", "name": "tabular", "status": "future"},
                        ],
                    }
                ],
            }
        ],
    }


def test_project_report_emits_phase_subphase_and_task_rows(tmp_path: Path) -> None:
    table = project_report(_write(tmp_path, _doc()))
    assert table.project == "journey"
    assert [r.level for r in table.rows] == [
        ReportLevel.PHASE,
        ReportLevel.SUBPHASE,
        ReportLevel.TASK,
        ReportLevel.TASK,
        ReportLevel.TASK,
        ReportLevel.TASK,
    ]


def test_phase_row_maps_metrics_and_derives_progress_and_variance(tmp_path: Path) -> None:
    phase = project_report(_write(tmp_path, _doc())).rows[0]
    assert phase.phase == "Build"
    assert phase.unit == ""
    assert phase.commits == 9
    assert phase.sessions == 4
    assert phase.material_decisions == 3
    assert phase.variance_days == 2
    assert phase.progress_pct == 50


def test_narrative_fields_projected_from_authored_nodes(tmp_path: Path) -> None:
    rows = project_report(_write(tmp_path, _doc())).rows
    sub = rows[1]
    assert sub.relevant_info == "Em curso — Fatia 1 entregue."
    assert sub.briefing == "Gera os relatórios formais do projeto."
    assert sub.deliverable == "Relatórios em PDF/markdown/CSV."
    phase = rows[0]
    assert phase.relevant_info is None
    assert phase.briefing is None


def test_deferred_columns_stay_none_never_fabricated(tmp_path: Path) -> None:
    for row in project_report(_write(tmp_path, _doc())).rows:
        assert row.tokens is None
        assert row.cost_usd is None


def test_task_rows_name_status_only(tmp_path: Path) -> None:
    tasks = [
        r for r in project_report(_write(tmp_path, _doc())).rows if r.level is ReportLevel.TASK
    ]
    assert {t.unit for t in tasks} == {"scaffold", "model", "projector", "tabular"}
    for t in tasks:
        assert t.phase == "Build"
        assert t.commits is None
        assert t.progress_pct is None


def test_only_exact_done_counts_matching_005_cockpit(tmp_path: Path) -> None:
    doc: dict[str, Any] = {
        "project": "x",
        "phases": [
            {
                "id": "p",
                "name": "P",
                "status": "in_execution",
                "subphases": [
                    {
                        "id": "s",
                        "name": "S",
                        "status": "in_execution",
                        "tasks": [
                            {"id": "T1", "name": "a", "status": "done"},
                            {"id": "T2", "name": "b", "status": "done_prod"},
                            {"id": "T3", "name": "c", "status": "merged_staging"},
                            {"id": "T4", "name": "d", "status": "done_early"},
                        ],
                    }
                ],
            }
        ],
    }
    sub = project_report(_write(tmp_path, doc)).rows[1]
    assert sub.progress_pct == 25  # only the exact 'done' counts


def test_progress_is_binary_when_node_has_no_tasks(tmp_path: Path) -> None:
    doc: dict[str, Any] = {
        "project": "x",
        "phases": [
            {"id": "w", "name": "W", "status": "done", "subphases": []},
            {"id": "r", "name": "R", "status": "future", "subphases": []},
            {"id": "m", "name": "M", "status": "merged_staging", "subphases": []},
        ],
    }
    rows = project_report(_write(tmp_path, doc)).rows
    assert rows[0].progress_pct == 100
    assert rows[1].progress_pct == 0
    assert rows[2].progress_pct == 0  # merged_staging is NOT done (parity with 005)


def test_project_report_raises_when_roadmap_absent(tmp_path: Path) -> None:
    with pytest.raises(JourneyError):
        project_report(tmp_path / "missing.yaml")


# ── decisions reader (US3) ──


def _adr(adr_dir: Path, num: int, slug: str, title: str, status: str, when: str) -> None:
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / f"{num:04d}-{slug}.md").write_text(
        f"# ADR-{num:04d} — {title}\n\n"
        "| Campo  | Valor |\n|--------|-------|\n"
        f"| Status | {status} |\n| Data   | {when} |\n| Autor  | x |\n\n## Contexto\n…\n",
        encoding="utf-8",
    )


def test_project_decisions_lists_adrs_ordered_with_header_fields(tmp_path: Path) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    _adr(adr_dir, 2, "b", "Segunda decisão", "Aceito", "2026-06-02")
    _adr(adr_dir, 1, "a", "Primeira decisão", "Superseded", "2026-06-01")
    decisions = project_decisions(tmp_path)
    assert [d.number for d in decisions] == [1, 2]
    assert decisions[0].title == "Primeira decisão"
    assert decisions[0].status == "Superseded"
    assert decisions[1].date == "2026-06-02"


def test_project_decisions_empty_when_no_adr_dir(tmp_path: Path) -> None:
    assert project_decisions(tmp_path) == []


def test_project_decisions_title_falls_back_to_slug_and_never_fabricates(tmp_path: Path) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0003-no-header.md").write_text("sem cabeçalho\n", encoding="utf-8")
    d = project_decisions(tmp_path)[0]
    assert d.title == "no-header"  # slug fallback
    assert d.status is None
    assert d.date is None


def test_write_report_writes_under_docs_reports(tmp_path: Path) -> None:
    path = write_report(tmp_path, "status-2026-06-18.md", "# x\n")
    assert path == tmp_path / "docs" / "reports" / "status-2026-06-18.md"
    assert path.read_text(encoding="utf-8") == "# x\n"


from journey_core.report_ops import _derive_progress as _dp73  # noqa: E402


def test_derive_progress_superseded_is_none() -> None:
    assert _dp73("superseded", []) is None


def test_derive_progress_done_future_unchanged() -> None:
    assert _dp73("done", []) == 100
    assert _dp73("future", []) == 0
    assert _dp73(None, ["done", "future"]) == 50
