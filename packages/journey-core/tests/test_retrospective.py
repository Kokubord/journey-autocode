"""Unit tests for the retrospective model + write ops (feature 013)."""

from pathlib import Path

import pytest
from journey_core.models.retrospective import METRICS_PENDING, RetroItem, Retrospective
from journey_core.retrospective_ops import next_retro_number, write_retrospective


def _retro() -> Retrospective:
    return Retrospective(
        slug="build-adiaveis",
        scope="Build — 5 adiáveis",
        date="2026-06-19",
        funcionou=[RetroItem(text="reuso forte", source="ADR-0017")],
    )


def test_retroitem_requires_citable_source() -> None:
    with pytest.raises(ValueError):
        RetroItem(text="lição sem fonte", source="   ")  # anti-fabrication


def test_to_markdown_has_four_sections_and_pending_metrics() -> None:
    md = _retro().to_markdown(1)
    assert "# Retrospectiva 001 — Build — 5 adiáveis" in md
    for title in (
        "O que funcionou",
        "O que não funcionou",
        "Lições aprendidas",
        "ADRs de aprendizado (sugeridos)",
    ):
        assert f"## {title}" in md
    assert "reuso forte — _fonte: ADR-0017_" in md
    assert METRICS_PENDING in md  # FR-006 — never a fabricated number
    assert "pendente" in md


def test_empty_section_is_not_fabricated() -> None:
    md = _retro().to_markdown(1)
    # nao_funcionou/licoes/adrs_aprendizado are empty -> explicit non-fabricated placeholder
    assert "_(sem registos nesta secção — não fabricado)_" in md


def test_filename_is_three_digit_sequential() -> None:
    assert _retro().filename(1) == "001-build-adiaveis.md"
    assert _retro().filename(42) == "042-build-adiaveis.md"


def test_next_retro_number_sequences(tmp_path: Path) -> None:
    d = tmp_path / "docs" / "retrospectives"
    assert next_retro_number(d) == 1  # dir absent
    d.mkdir(parents=True)
    assert next_retro_number(d) == 1  # empty
    (d / "001-a.md").write_text("x", encoding="utf-8")
    (d / "002-b.md").write_text("x", encoding="utf-8")
    assert next_retro_number(d) == 3


def test_write_retrospective_creates_tracked_dir(tmp_path: Path) -> None:
    d = tmp_path / "docs" / "retrospectives"
    path = write_retrospective(d, _retro(), 1)
    assert path.is_file()
    assert path.name == "001-build-adiaveis.md"
    assert "## Lições aprendidas" in path.read_text(encoding="utf-8")
