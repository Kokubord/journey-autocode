from journey_core.models import ExitCheckItem, ExitChecklist, StructuredPR


def test_exit_checklist_blocked_by_failing_blocking_item() -> None:
    cl = ExitChecklist(
        items=[
            ExitCheckItem(label="Testes a passar", ok=False, blocking=True),
            ExitCheckItem(label="HANDOVER", ok=True, blocking=False),
        ]
    )
    assert cl.blocked is True
    assert cl.blocking_failures == ["Testes a passar"]


def test_exit_checklist_not_blocked_when_only_nonblocking_fails() -> None:
    cl = ExitChecklist(
        items=[
            ExitCheckItem(label="Testes a passar", ok=True),
            ExitCheckItem(label="HANDOVER", ok=False, blocking=False),
        ]
    )
    assert cl.blocked is False
    assert cl.blocking_failures == []


def test_structured_pr_markdown_sections() -> None:
    pr = StructuredPR(
        title="Phase Build — dashboard",
        material_decisions=["DECISION(meta): adopt X [ADR-0020]"],
        adrs=[20],
    )
    md = pr.to_markdown()
    assert md.startswith("# Phase Build — dashboard")
    assert "## Decisões materiais desta fase" in md
    assert "DECISION(meta): adopt X [ADR-0020]" in md
    assert "## ADRs criados" in md
    assert "- ADR-0020" in md
    assert "## Checklist de revisão" in md


def test_structured_pr_empty_sections_have_placeholders() -> None:
    md = StructuredPR(title="Phase Discovery — x").to_markdown()
    assert "(nenhuma decisão material registada no período)" in md
    assert "- (nenhum)" in md
    # default review checklist kicks in
    assert "Bateria verde" in md
