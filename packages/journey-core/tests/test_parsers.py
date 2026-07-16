from pathlib import Path

from journey_core.parsers import parse_adr_index, parse_handover


def test_parse_adr_index_sorts_and_ignores_non_adr(tmp_path: Path) -> None:
    assert parse_adr_index(tmp_path / "missing") == []
    (tmp_path / "0002-b.md").write_text("x", encoding="utf-8")
    (tmp_path / "0001-a.md").write_text("x", encoding="utf-8")
    (tmp_path / "README.md").write_text("x", encoding="utf-8")
    refs = parse_adr_index(tmp_path)
    assert [ref.number for ref in refs] == [1, 2]
    assert refs[0].slug == "a"


def test_parse_handover_missing_file(tmp_path: Path) -> None:
    assert parse_handover(tmp_path / "HANDOVER.md").exists is False


def test_parse_handover_extracts_meta(tmp_path: Path) -> None:
    content = (
        "## Meta\n\n| Campo | Valor |\n|---|---|\n"
        "| **Última atualização** | 2026-06-12 |\n"
        "| **Fase atual** | Build |\n"
    )
    file_path = tmp_path / "HANDOVER.md"
    file_path.write_text(content, encoding="utf-8")
    state = parse_handover(file_path)
    assert state.exists is True
    assert state.last_update == "2026-06-12"
    assert state.current_phase == "Build"
