from pathlib import Path

import pytest
from journey_core.exceptions import JourneyError
from journey_core.models import Adr
from journey_skill.commands.journey_decision import (
    app,
    append_decisao_fresca,
    decisao_fresca_entry,
    decision_commit_message,
    read_context,
    write_decision_adr,
)
from typer.testing import CliRunner

runner = CliRunner()

_HANDOVER = (
    "## Meta\n\n| Campo | Valor |\n|---|---|\n| **Fase atual** | Build |\n\n"
    "## Decisões frescas (últimos 7 dias)\n\n"
    "> Formato: `YYYY-MM-DD — <decisão> — [ADR-NNNN]`. Mais recentes primeiro.\n\n"
    "- 2026-06-16 — **Decisão anterior** — [ADR-0016]\n"
)


def _adr(number: int, supersedes: list[int] | None = None) -> Adr:
    return Adr(
        number=number,
        slug="exemplo",
        title="Exemplo",
        date="2026-06-17",
        author="rkokubo",
        contexto="c",
        decisao="d",
        consequencias="k",
        alternativas="a",
        referencias="r",
        supersedes=supersedes or [],
    )


def test_read_context(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text(_HANDOVER, encoding="utf-8")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-a.md").write_text("x", encoding="utf-8")
    ctx = read_context(tmp_path)
    assert ctx["current_phase"] == "Build"
    assert ctx["next_adr_number"] == 2
    assert ctx["adr_count"] == 1


def test_write_decision_adr_canonical(tmp_path: Path) -> None:
    path = write_decision_adr(tmp_path, _adr(17))
    assert path == tmp_path / "docs" / "adr" / "0017-exemplo.md"
    assert path.read_text(encoding="utf-8").startswith("# ADR-0017 — Exemplo")


def test_write_decision_adr_supersede_by_reference(tmp_path: Path) -> None:
    path = write_decision_adr(tmp_path, _adr(17, supersedes=[6]))
    text = path.read_text(encoding="utf-8")
    assert "Supersede (por referência — ADR-0009):** ADR-0006." in text


def test_decision_commit_message() -> None:
    assert decision_commit_message("meta", "adopt X", 17) == "DECISION(meta): adopt X [ADR-0017]"


def test_decisao_fresca_entry() -> None:
    assert (
        decisao_fresca_entry("2026-06-17", "adopt X", 17) == "- 2026-06-17 — adopt X — [ADR-0017]"
    )


def test_append_decisao_fresca_inserts_first(tmp_path: Path) -> None:
    h = tmp_path / "HANDOVER.md"
    h.write_text(_HANDOVER, encoding="utf-8")
    append_decisao_fresca(tmp_path, "- 2026-06-17 — nova — [ADR-0017]")
    text = h.read_text(encoding="utf-8")
    # new bullet is above the previous one, and the previous is preserved
    assert text.index("[ADR-0017]") < text.index("[ADR-0016]")
    assert "**Decisão anterior**" in text


def test_append_decisao_fresca_missing_file(tmp_path: Path) -> None:
    with pytest.raises(JourneyError):
        append_decisao_fresca(tmp_path, "- x")


def test_append_decisao_fresca_no_section(tmp_path: Path) -> None:
    h = tmp_path / "HANDOVER.md"
    h.write_text("## Meta\n\n| x | y |\n", encoding="utf-8")
    with pytest.raises(JourneyError):
        append_decisao_fresca(tmp_path, "- x")


def test_cli_read_context_and_register(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text(_HANDOVER, encoding="utf-8")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    r1 = runner.invoke(app, ["read-context", "--repo-root", str(tmp_path)])
    assert r1.exit_code == 0 and "next_adr_number" in r1.stdout
    r2 = runner.invoke(
        app,
        [
            "register",
            "--summary-pt",
            "adota X",
            "--summary-en",
            "adopt X",
            "--number",
            "17",
            "--scope",
            "meta",
            "--date",
            "2026-06-17",
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r2.exit_code == 0
    assert "DECISION(meta): adopt X [ADR-0017]" in r2.stdout  # commit in EN
    h = (tmp_path / "HANDOVER.md").read_text(encoding="utf-8")
    assert "adota X" in h and "[ADR-0017]" in h  # HANDOVER entry in PT
    assert "adopt X" not in h  # EN summary does NOT leak into the PT HANDOVER entry


def test_cli_write_adr(tmp_path: Path) -> None:
    payload = tmp_path / "adr.json"
    payload.write_text(_adr(20).model_dump_json(), encoding="utf-8")
    result = runner.invoke(
        app, ["write-adr", "--payload", str(payload), "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert (tmp_path / "docs" / "adr" / "0020-exemplo.md").exists()
