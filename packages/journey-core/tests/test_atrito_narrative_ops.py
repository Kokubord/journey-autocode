"""Tests for the ATRITO narrative authoring op (ADR-0046, Build-2).

Mirrors test_briefing_ops: the WRITE op (sets one ref, preserves others, creates the file,
never fabricates) + list_unnarrated (all ledger ATRITOs minus the authored). The honesty
cases (empty / non-ATRITO raise; no relevance heuristic) are the heart.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from journey_core.atrito_narrative_ops import list_unnarrated, set_atrito_narrative
from journey_core.exceptions import JourneyError


def _read(repo_root: Path) -> dict[str, Any]:
    data: Any = yaml.safe_load(
        (repo_root / "docs" / "atrito-narratives.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(data, dict)
    return cast("dict[str, Any]", data)


def _ledger(repo_root: Path, *refs: str) -> None:
    (repo_root / "docs").mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"### {r} — título técnico\nblá blá técnico.\n" for r in refs)
    (repo_root / "docs" / "JOURNEY-ATRITOS-FOUNDATION.md").write_text(body, encoding="utf-8")


def test_set_writes_a_ref(tmp_path: Path) -> None:
    set_atrito_narrative(tmp_path, "ATRITO-83", "Em linguagem simples: a fonte se autoavalia.")
    data = _read(tmp_path)
    assert data["ATRITO-83"]["narrative"] == "Em linguagem simples: a fonte se autoavalia."


def test_set_preserves_other_refs(tmp_path: Path) -> None:
    set_atrito_narrative(tmp_path, "ATRITO-83", "narrativa do 83")
    set_atrito_narrative(tmp_path, "ATRITO-89", "narrativa do 89")
    data = _read(tmp_path)
    assert data["ATRITO-83"]["narrative"] == "narrativa do 83"
    assert data["ATRITO-89"]["narrative"] == "narrativa do 89"


def test_set_creates_file_if_absent(tmp_path: Path) -> None:
    assert not (tmp_path / "docs" / "atrito-narratives.yaml").exists()
    out = set_atrito_narrative(tmp_path, "ATRITO-1", "narrativa")
    assert out.is_file()


def test_set_refuses_empty_narrative(tmp_path: Path) -> None:
    with pytest.raises(JourneyError):
        set_atrito_narrative(tmp_path, "ATRITO-83", "   ")


def test_set_refuses_non_atrito_ref(tmp_path: Path) -> None:
    for bad in ["ADR-0001", "atrito-83", "ATRITO-", "../x", "ATRITO-7a", ""]:
        with pytest.raises(JourneyError):
            set_atrito_narrative(tmp_path, bad, "narrativa")


def test_list_unnarrated_is_ledger_minus_authored(tmp_path: Path) -> None:
    _ledger(tmp_path, "ATRITO-1", "ATRITO-2", "ATRITO-3")
    set_atrito_narrative(tmp_path, "ATRITO-2", "narrativa do 2")
    assert list_unnarrated(tmp_path) == ["ATRITO-1", "ATRITO-3"]


def test_list_unnarrated_empty_when_all_narrated(tmp_path: Path) -> None:
    _ledger(tmp_path, "ATRITO-1")
    set_atrito_narrative(tmp_path, "ATRITO-1", "narrativa")
    assert list_unnarrated(tmp_path) == []
