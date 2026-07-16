"""Tests for the renderers — markdown table, context, CSV, decisions (feature 011)."""

from journey_core.models.report import (
    CANONICAL_COLUMNS,
    DecisionRow,
    ReportLevel,
    ReportRow,
    ReportTable,
)
from journey_core.report_render import (
    render_context,
    render_csv,
    render_decisions_md,
    render_markdown,
)


def _table() -> ReportTable:
    return ReportTable(
        project="journey",
        rows=[
            ReportRow(
                level=ReportLevel.PHASE,
                phase="Build",
                unit="",
                status="in_execution",
                progress_pct=50,
                planned_start="2026-06-01",
                planned_end="2026-06-10",
                actual_start="2026-06-02",
                actual_end="2026-06-12",
                variance_days=2,
                material_decisions=3,
                commits=9,
                sessions=4,
                tokens=None,
                cost_usd=None,
                relevant_info="Bloqueio: pipeline de tokens.",
                briefing="Monta as peças do produto a partir do plano.",
                deliverable="As 8 peças essenciais em main.",
            ),
            ReportRow(
                level=ReportLevel.TASK,
                phase="Build",
                unit="scaffold",
                status="future",
            ),
        ],
    )


def test_header_lists_the_15_canonical_columns() -> None:
    header_line = render_markdown(_table()).splitlines()[2]
    for column in CANONICAL_COLUMNS:
        assert column in header_line
    assert header_line.count("|") == 16


def test_phase_row_uses_honesty_labels_and_br_dates() -> None:
    out = render_markdown(_table(), granularity="phase")
    assert "12/06/26" in out
    assert "50%" in out
    assert "2d" in out
    assert "pendente" in out
    assert "Bloqueio: pipeline de tokens." in out  # col-15 ← notes


def test_status_renders_pt_label_not_slug() -> None:
    out = render_markdown(_table(), granularity="phase")
    assert "Em execução" in out  # PT label (B5)
    assert "in_execution" not in out  # the raw slug is gone


def test_phase_granularity_excludes_tasks() -> None:
    assert "scaffold" not in render_markdown(_table(), granularity="phase")


def test_task_granularity_shows_only_tasks() -> None:
    out = render_markdown(_table(), granularity="task")
    assert "scaffold" in out
    assert "—" in out
    assert "pendente" in out


def test_csv_has_15_columns_and_no_narrative() -> None:
    out = render_csv(_table(), granularity="phase")
    header = out.splitlines()[0]
    assert header.count(",") == 14  # 15 columns -> 14 commas
    assert "Monta as peças" not in out  # briefing narrative is not in CSV
    assert "Bloqueio: pipeline de tokens." in out  # col-15 IS in CSV


def test_csv_quotes_fields_with_commas() -> None:
    table = ReportTable(
        project="x",
        rows=[ReportRow(level=ReportLevel.TASK, phase="P", unit="a, b", status="done")],
    )
    assert '"a, b"' in render_csv(table, granularity="task")


def test_context_renders_briefing_and_distinct_deliverable() -> None:
    out = render_context(_table())
    assert "## Contexto por fase/etapa" in out
    assert "### Build" in out
    assert "Monta as peças do produto a partir do plano." in out
    assert "**Entregável:** As 8 peças essenciais em main." in out


def test_context_omits_nodes_without_authored_narrative() -> None:
    table = ReportTable(
        project="x",
        rows=[ReportRow(level=ReportLevel.PHASE, phase="Empty", unit="", status="future")],
    )
    assert render_context(table) == ""


def test_decisions_md_lists_adrs() -> None:
    out = render_decisions_md(
        [DecisionRow(number=18, title="Nutrição rica", status="Aceito", date="2026-06-17")]
    )
    assert "# Relatório de decisões" in out
    assert "ADR-0018" in out
    assert "Nutrição rica" in out
    assert "Aceito" in out


def test_decisions_md_dashes_missing_fields() -> None:
    out = render_decisions_md([DecisionRow(number=1, title="x")])
    assert "—" in out  # status/date None -> —
