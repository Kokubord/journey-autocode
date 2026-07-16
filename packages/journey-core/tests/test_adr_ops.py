from pathlib import Path

import pytest
from journey_core.adr_ops import next_adr_number, write_adr
from journey_core.exceptions import WriteRoutingError
from journey_core.models import Adr


def _adr(number: int) -> Adr:
    return Adr(
        number=number,
        slug="x",
        title="X",
        date="2026-06-17",
        author="rkokubo",
        contexto="c",
        decisao="d",
        consequencias="k",
        alternativas="a",
        referencias="r",
    )


def test_next_adr_number_empty_and_populated(tmp_path: Path) -> None:
    assert next_adr_number(tmp_path) == 1
    (tmp_path / "0001-a.md").write_text("x", encoding="utf-8")
    (tmp_path / "0002-b.md").write_text("x", encoding="utf-8")
    assert next_adr_number(tmp_path) == 3


def test_write_adr_renders_canonical(tmp_path: Path) -> None:
    path = write_adr(tmp_path, _adr(18))
    assert path.name == "0018-x.md"
    assert path.read_text(encoding="utf-8").startswith("# ADR-0018 — X")


def test_write_adr_vetoes_unc() -> None:
    with pytest.raises(WriteRoutingError):
        write_adr("//wsl.localhost/ubuntu/repo/docs/adr", _adr(1))
