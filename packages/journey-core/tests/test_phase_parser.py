from pathlib import Path

import pytest
from journey_core.exceptions import JourneyError, WriteRoutingError
from journey_core.models import Phase, PhaseState
from journey_core.parsers import read_active_phase, set_active_phase

_HANDOVER = (
    "## Meta\n\n| Campo | Valor |\n|---|---|\n"
    "| **Última atualização** | 2026-06-17 |\n"
    "| **Fase atual** | Discovery — workshop (ativa) |\n"
    "| **Tier de adopção** | Standard |\n"
)


def test_read_active_phase_missing(tmp_path: Path) -> None:
    assert read_active_phase(tmp_path / "HANDOVER.md") is None


def test_read_active_phase_value(tmp_path: Path) -> None:
    h = tmp_path / "HANDOVER.md"
    h.write_text(_HANDOVER, encoding="utf-8")
    assert read_active_phase(h) == "Discovery — workshop (ativa)"


def test_set_active_phase_replaces_only_value(tmp_path: Path) -> None:
    h = tmp_path / "HANDOVER.md"
    h.write_text(_HANDOVER, encoding="utf-8")
    set_active_phase(h, PhaseState(phase=Phase.BUILD, slug="dashboard"))
    text = h.read_text(encoding="utf-8")
    assert "| **Fase atual** | Build — sub-fase **dashboard** (ativa) |" in text
    # rest preserved
    assert "| **Última atualização** | 2026-06-17 |" in text
    assert "| **Tier de adopção** | Standard |" in text
    assert "Discovery — workshop" not in text


def test_set_active_phase_missing_file(tmp_path: Path) -> None:
    with pytest.raises(JourneyError):
        set_active_phase(tmp_path / "HANDOVER.md", PhaseState(phase=Phase.BUILD, slug="x"))


def test_set_active_phase_no_row(tmp_path: Path) -> None:
    h = tmp_path / "HANDOVER.md"
    h.write_text("## Meta\n\n| **Outra** | x |\n", encoding="utf-8")
    with pytest.raises(JourneyError):
        set_active_phase(h, PhaseState(phase=Phase.BUILD, slug="x"))


def test_set_active_phase_vetoes_unc() -> None:
    with pytest.raises(WriteRoutingError):
        set_active_phase(
            "//wsl.localhost/ubuntu/repo/HANDOVER.md", PhaseState(phase=Phase.RUN, slug="x")
        )
