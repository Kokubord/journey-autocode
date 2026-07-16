"""Tests for the 15-column report model (feature 011)."""

from journey_core.models.report import (
    CANONICAL_COLUMNS,
    ReportLevel,
    ReportRow,
    ReportTable,
)


def test_canonical_columns_are_the_15_of_section_10_3() -> None:
    assert len(CANONICAL_COLUMNS) == 15
    assert CANONICAL_COLUMNS[0] == "Fase"
    assert CANONICAL_COLUMNS[-1] == "Informações relevantes"
    # col 15 is distinct from the didactic context block (briefing) — not merged
    assert all("briefing" not in c.lower() for c in CANONICAL_COLUMNS)


def test_report_row_optional_fields_default_to_none() -> None:
    row = ReportRow(level=ReportLevel.TASK, phase="Build", unit="T001", status="future")
    assert row.tokens is None
    assert row.cost_usd is None
    assert row.relevant_info is None
    assert row.commits is None
    assert row.progress_pct is None


def test_report_table_exposes_canonical_columns() -> None:
    table = ReportTable(project="journey", rows=[])
    assert table.columns == CANONICAL_COLUMNS
