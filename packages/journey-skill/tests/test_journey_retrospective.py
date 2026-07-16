# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Smoke tests for /journey-retrospective (feature 013) — in a tmp git repo."""

import json
from pathlib import Path

from git import Repo
from journey_skill.commands.journey_retrospective import app
from typer.testing import CliRunner

runner = CliRunner()


def _repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "t")
        cw.set_value("user", "email", "t@e")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-x.md").write_text("# ADR-0001 — X\n", encoding="utf-8")
    (tmp_path / "f").write_text("f", encoding="utf-8")
    repo.index.add(["f", "docs/adr/0001-x.md"])
    repo.index.commit("feat: algo da fase")
    (tmp_path / "HANDOVER.md").write_text(
        "# H\n\n"
        "| **Fase atual** | Build — sub-fase **x** (ativa) |\n\n"
        "```yaml\n"
        "fase: Build\n"
        "subfase: x\n"
        "timestamp: 2026-06-19\n"
        "adrs_criados:\n"
        "  - ADR-0001\n"
        "```\n",
        encoding="utf-8",
    )
    return repo


def _retro_payload(tmp_path: Path) -> Path:
    doc = {
        "slug": "fase-x",
        "scope": "Build — fase x",
        "date": "2026-06-19",
        "funcionou": [{"text": "reuso", "source": "ADR-0001"}],
        "nao_funcionou": [],
        "licoes": [{"text": "marcar tasks no fecho", "source": "commit feat: algo da fase"}],
        "adrs_aprendizado": [],
    }
    p = tmp_path / "retro.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return p


def _adr_payload(tmp_path: Path, *, sources: list[str]) -> Path:
    adr = {
        "number": 0,
        "slug": "aprendizado",
        "title": "Aprendizado da fase",
        "status": "Proposto",
        "date": "2026-06-19",
        "author": "a",
        "contexto": "c",
        "decisao": "d",
        "consequencias": "x",
        "alternativas": "alt",
        "referencias": "r",
        "supersedes": [],
    }
    p = tmp_path / "prop.json"
    p.write_text(json.dumps({"adr": adr, "sources": sources, "uncertain": False}), encoding="utf-8")
    return p


def test_read_context_emits_inputs_local(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(app, ["read-context", "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert d["commit_count"] >= 1
    assert any("algo da fase" in c["summary"] for c in d["commits"])
    assert d["adrs"] == [{"number": 1, "slug": "x"}]
    assert d["closing_blocks"] and d["closing_blocks"][0]["fase"] == "Build"
    assert "pendente" in d["metricas_operacionais"]  # FR-006 — never fabricated


def test_record_writes_sequential_doc(tmp_path: Path) -> None:
    _repo(tmp_path)
    payload = _retro_payload(tmp_path)
    r = runner.invoke(app, ["record", "--payload", str(payload), "--repo-root", str(tmp_path)])
    assert r.exit_code == 0
    f = tmp_path / "docs" / "retrospectives" / "001-fase-x.md"
    assert f.is_file()
    body = f.read_text(encoding="utf-8")
    assert "## O que funcionou" in body
    assert "marcar tasks no fecho — _fonte: commit feat: algo da fase_" in body
    # second record -> 002
    r2 = runner.invoke(app, ["record", "--payload", str(payload), "--repo-root", str(tmp_path)])
    assert r2.exit_code == 0
    assert (tmp_path / "docs" / "retrospectives" / "002-fase-x.md").is_file()


def test_record_dry_run_does_not_write(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "record",
            "--payload",
            str(_retro_payload(tmp_path)),
            "--dry-run",
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "dry-run" in r.stdout
    assert not (tmp_path / "docs" / "retrospectives").exists()


def test_propose_adr_reuses_retroproposal_dry_run(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "propose-adr",
            "--payload",
            str(_adr_payload(tmp_path, sources=["sha1"])),
            "--dry-run",
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "ADR-0002" in r.stdout  # next free number
    assert not (tmp_path / "docs" / "adr" / "0002-aprendizado.md").exists()


def test_propose_adr_rejects_no_sources(tmp_path: Path) -> None:
    _repo(tmp_path)
    r = runner.invoke(
        app,
        [
            "propose-adr",
            "--payload",
            str(_adr_payload(tmp_path, sources=[])),
            "--repo-root",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 1  # propose-never-assert: no source -> invalid
