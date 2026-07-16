# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Smoke tests for /journey-archaeology (feature 003) — in a tmp git repo."""

import json
from pathlib import Path

from git import Repo
from journey_skill.commands.journey_archaeology import app
from typer.testing import CliRunner

runner = CliRunner()


def _repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "t")
        cw.set_value("user", "email", "t@e")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-x.md").write_text("# ADR-0001 — X\n", encoding="utf-8")
    (tmp_path / "specs" / "001-foo").mkdir(parents=True)
    (tmp_path / "f").write_text("f", encoding="utf-8")
    repo.index.add(["f", "docs/adr/0001-x.md"])
    repo.index.commit("feat: algo material")
    (tmp_path / "HANDOVER.md").write_text(
        "# H\n\n## Histórico da arqueologia\n\n> nota\n\n- _(vazio)_\n", encoding="utf-8"
    )
    return repo


def _payload(tmp_path: Path, *, sources: list[str]) -> Path:
    adr = {
        "number": 0,
        "slug": "retro",
        "title": "Decisão retro",
        "status": "Proposto",
        "date": "2026-06-18",
        "author": "a",
        "contexto": "ADR criado retroativamente em 2026-06-18 após auditoria.",
        "decisao": "d",
        "consequencias": "c",
        "alternativas": "alt",
        "referencias": "r",
        "supersedes": [],
    }
    p = tmp_path / "prop.json"
    p.write_text(json.dumps({"adr": adr, "sources": sources, "uncertain": False}), encoding="utf-8")
    return p


def test_read_context_local_no_write(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(app, ["read-context", "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert d["commit_count"] >= 1
    assert "001-foo" in d["specs"]
    assert any("algo material" in c["summary"] for c in d["commits"])


def test_propose_adr_dry_run_does_not_write(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "propose-adr",
            "--payload",
            str(_payload(tmp_path, sources=["sha123"])),
            "--dry-run",
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "dry-run" in r.stdout
    assert "ADR-0002" in r.stdout  # next free number (FR-006)
    assert not (tmp_path / "docs" / "adr" / "0002-retro.md").exists()


def test_propose_adr_writes_proposto(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "propose-adr",
            "--payload",
            str(_payload(tmp_path, sources=["sha123"])),
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    f = tmp_path / "docs" / "adr" / "0002-retro.md"
    assert f.is_file()
    assert "Proposto" in f.read_text(encoding="utf-8")


def test_propose_adr_rejects_no_sources(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "propose-adr",
            "--payload",
            str(_payload(tmp_path, sources=[])),
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 1  # propose-never-assert: no source -> invalid


def test_record_appends_arqueologia_and_clears_placeholder(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "record",
            "--scope",
            "últimos 30d",
            "--author",
            "a",
            "--sources",
            "git log",
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    h = (tmp_path / "HANDOVER.md").read_text(encoding="utf-8")
    assert "últimos 30d" in h
    assert "_(vazio)_" not in h
