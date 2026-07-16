# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
"""Tests for archaeology models + commits_since_date (feature 003)."""

from datetime import date, timedelta
from pathlib import Path

import pytest
from git import Repo
from journey_core.models.adr import Adr, AdrStatus
from journey_core.models.archaeology import RetroProposal
from journey_core.parsers.git_state import commits_since_date


def _adr() -> Adr:
    return Adr(
        number=0,
        slug="retro",
        title="T",
        status=AdrStatus.PROPOSTO,
        date="2026-06-18",
        author="a",
        contexto="ADR criado retroativamente em 2026-06-18 após auditoria.",
        decisao="d",
        consequencias="cq",
        alternativas="alt",
        referencias="r",
    )


def test_retroproposal_requires_at_least_one_source() -> None:
    with pytest.raises(ValueError):
        RetroProposal(adr=_adr(), sources=[])  # propose-never-assert (FR-007)


def test_retroproposal_ok_with_source_and_uncertain() -> None:
    p = RetroProposal(adr=_adr(), sources=["abc123", "specs/001-x"], uncertain=True)
    assert p.uncertain
    assert p.sources == ["abc123", "specs/001-x"]


def test_commits_since_date_filters_by_authored_date(tmp_path: Path) -> None:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "t")
        cw.set_value("user", "email", "t@e")
    (tmp_path / "a").write_text("a", encoding="utf-8")
    repo.index.add(["a"])
    repo.index.commit("feat: c1")
    recent = commits_since_date(tmp_path, date.today() - timedelta(days=1))
    assert any(c.summary == "feat: c1" for c in recent)
    future = commits_since_date(tmp_path, date.today() + timedelta(days=1))
    assert future == []  # nothing authored after tomorrow
