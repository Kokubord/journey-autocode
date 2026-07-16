from pathlib import Path

import pytest
import yaml
from journey_core.briefing_ops import (
    list_unnourished,
    set_briefing,
    set_deliverable,
    set_notes,
)
from journey_core.exceptions import JourneyError, WriteRoutingError


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
                        "subphases": [
                            {
                                "id": "007",
                                "name": "phase-end",
                                "status": "done",
                                "summary": "s",
                                "tasks": [{"id": "T001", "name": "t", "status": "done"}],
                            }
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


def test_sets_briefing_by_subphase_id(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    set_briefing(p, "007", "Briefing didático da 007.")
    sub = yaml.safe_load(p.read_text(encoding="utf-8"))["phases"][0]["subphases"][0]
    assert sub["briefing"] == "Briefing didático da 007."


def test_sets_briefing_at_phase_level(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    set_briefing(p, "build", "Fase Build em curso.")
    assert (
        yaml.safe_load(p.read_text(encoding="utf-8"))["phases"][0]["briefing"]
        == "Fase Build em curso."
    )


def test_preserves_other_fields_and_does_not_fabricate_other_nodes(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    set_briefing(p, "007", "x")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    sub = data["phases"][0]["subphases"][0]
    assert sub["summary"] == "s" and sub["name"] == "phase-end" and sub["status"] == "done"
    assert data["phases"][0]["summary"] == "b"  # parent fields untouched
    assert "briefing" not in data["phases"][0]  # sibling/parent node NOT fabricated


def test_idempotent_overwrites(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    set_briefing(p, "007", "a")
    set_briefing(p, "007", "b")
    sub = yaml.safe_load(p.read_text(encoding="utf-8"))["phases"][0]["subphases"][0]
    assert sub["briefing"] == "b"


def test_unknown_id_raises(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    with pytest.raises(JourneyError):
        set_briefing(p, "999", "x")


def test_empty_briefing_raises(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    with pytest.raises(JourneyError):
        set_briefing(p, "007", "   ")


def test_unc_path_is_vetoed() -> None:
    with pytest.raises(WriteRoutingError):
        set_briefing("//wsl.localhost/Ubuntu/x/roadmap.yaml", "007", "x")


def test_set_deliverable_and_set_notes(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    set_deliverable(p, "007", "Entregável da 007.")
    set_notes(p, "007", "Histórico da 007.")
    sub = yaml.safe_load(p.read_text(encoding="utf-8"))["phases"][0]["subphases"][0]
    assert sub["deliverable"] == "Entregável da 007." and sub["notes"] == "Histórico da 007."


def test_set_notes_empty_raises(tmp_path: Path) -> None:
    p = _roadmap(tmp_path)
    with pytest.raises(JourneyError):
        set_notes(p, "007", "  ")


# --- list_unnourished (ADR-0018, Fatia 5/6 — backfill enumeration over 3 fields) ----


def _roadmap_with_refs(tmp_path: Path) -> Path:
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
                                "summary_ref": {"doc": "specs/001/spec.md", "anchor": None},
                                "tasks": [{"id": "T001", "name": "t", "status": "done"}],
                            },
                            {
                                "id": "011",
                                "name": "journey-report",
                                "status": "done",
                                "summary": "r",
                                "briefing": "Já nutrido — não deve aparecer.",
                                "deliverable": "Relatórios formais.",
                                "notes": "Fatia 1 entregue.",
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


def test_list_unnourished_returns_phase_and_subphase_skipping_nourished(tmp_path: Path) -> None:
    units = list_unnourished(_roadmap_with_refs(tmp_path))
    ids = [u.id for u in units]
    assert ids == ["build", "001"]  # 011 fully nourished -> skipped; tasks excluded by default
    build = units[0]
    assert build.level == 0 and build.ref_doc == "methodology.md" and build.ref_anchor == "#3.3"
    assert build.missing == ("briefing", "deliverable", "notes")  # none authored on build
    sub = units[1]
    assert sub.level == 1 and sub.name == "journey-init" and sub.ref_anchor is None


def test_list_unnourished_reports_partial_missing(tmp_path: Path) -> None:
    p = _roadmap_with_refs(tmp_path)
    set_briefing(p, "001", "Conceitual da 001.")  # only briefing -> deliverable/notes still missing
    sub = next(u for u in list_unnourished(p) if u.id == "001")
    assert sub.missing == ("deliverable", "notes")


def test_list_unnourished_can_include_tasks(tmp_path: Path) -> None:
    units = list_unnourished(_roadmap_with_refs(tmp_path), include_tasks=True)
    ids = [u.id for u in units]
    assert ids == ["build", "001", "T001"]
    assert units[-1].level == 2


def test_list_unnourished_empty_when_all_authored(tmp_path: Path) -> None:
    p = _roadmap_with_refs(tmp_path)
    for unit in ("build", "001"):
        set_briefing(p, unit, f"Briefing {unit}.")
        set_deliverable(p, unit, f"Entregável {unit}.")
        set_notes(p, unit, f"Histórico {unit}.")
    assert list_unnourished(p) == []
