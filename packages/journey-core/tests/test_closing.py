from pathlib import Path

from journey_core.parsers import parse_closing_blocks


def test_parse_closing_blocks_missing_file(tmp_path: Path) -> None:
    assert parse_closing_blocks(tmp_path / "HANDOVER.md") == []


def test_parse_closing_blocks_extracts_pivot(tmp_path: Path) -> None:
    content = (
        "# HANDOVER\n\n"
        "```yaml\n"
        "fase: Build\n"
        "subfase: B0 journey-core\n"
        "sessao_id: abc-123\n"
        "adrs_criados: [ADR-0015]\n"
        "```\n\n"
        "```yaml\n"
        "not_a_closing: true\n"
        "```\n"
    )
    file_path = tmp_path / "HANDOVER.md"
    file_path.write_text(content, encoding="utf-8")
    blocks = parse_closing_blocks(file_path)
    assert len(blocks) == 1
    assert blocks[0].fase == "Build"
    assert blocks[0].subfase == "B0 journey-core"
    assert blocks[0].sessao_id == "abc-123"
    assert blocks[0].adrs_criados == ["ADR-0015"]
