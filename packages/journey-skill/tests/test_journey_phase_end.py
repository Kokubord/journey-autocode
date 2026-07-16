import contextlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
from git import Repo
from journey_core.models import Phase
from journey_core.parsers.git_state import CommitInfo
from journey_skill.commands import journey_phase_end as pe
from typer.testing import CliRunner, Result

runner = CliRunner()


def _commit(summary: str) -> CommitInfo:
    return CommitInfo(sha="0" * 40, authored_at=datetime(2026, 6, 17, tzinfo=UTC), summary=summary)


def _repo(tmp_path: Path) -> Path:
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "T")
    repo.git.config("user.email", "t@t")
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    repo.git.add("a.txt")
    repo.git.commit("-m", "chore: base")
    return tmp_path


def test_material_decisions_and_adrs() -> None:
    commits = [
        _commit("DECISION(meta): adopt X [ADR-0020]"),
        _commit("feat(x): something"),
        _commit("DECISION(core): Y [ADR-0021]"),
    ]
    assert pe.material_decisions(commits) == [
        "DECISION(meta): adopt X [ADR-0020]",
        "DECISION(core): Y [ADR-0021]",
    ]
    assert pe.adrs_in(commits) == [20, 21]


def test_build_structured_pr() -> None:
    pr = pe.build_structured_pr(Phase.BUILD, "dashboard", [_commit("DECISION(m): z [ADR-0020]")])
    assert pr.title == "Phase Build — dashboard"
    assert pr.adrs == [20]


def test_build_exit_checklist_blocks_on_failing_tests() -> None:
    assert pe.build_exit_checklist(tests_ok=False, ci_ok=True, handover_ok=True).blocked is True
    assert pe.build_exit_checklist(tests_ok=True, ci_ok=True, handover_ok=True).blocked is False


def test_build_exit_checklist_build_end_adds_manuals() -> None:
    cl = pe.build_exit_checklist(
        tests_ok=True, ci_ok=True, handover_ok=True, build_end=True, manuals_ok=False
    )
    assert any("Manuais" in item.label for item in cl.items)
    assert cl.blocked is False  # manuals item is non-blocking


def test_commits_since_filters_by_boundary(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    repo = Repo(root)
    base_sha = repo.head.commit.hexsha
    (root / "b.txt").write_text("2", encoding="utf-8")
    repo.git.add("b.txt")
    repo.git.commit("-m", "feat: second")
    since = pe.commits_since(root, base_sha)
    assert [c.summary for c in since] == ["feat: second"]
    assert len(pe.commits_since(root, None)) == 2


def test_trigger_roadmap_regen_is_inert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Render local aposentado (feature 023 / ATRITO-78): o trigger NÃO invoca subprocess
    # nem gera roadmap local; retorna None e nada é executado.
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> None:
        calls.append(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    pe.trigger_roadmap_regen(tmp_path)  # inerte (no-op) — nada a asserir do retorno
    assert calls == []
    assert not (tmp_path / "roadmap.yaml").exists()


def test_cli_exit_check_blocks() -> None:
    ok = runner.invoke(pe.app, ["exit-check", "--tests-ok", "--ci-ok", "--handover-ok"])
    assert ok.exit_code == 0
    blocked = runner.invoke(pe.app, ["exit-check", "--no-tests-ok", "--ci-ok", "--handover-ok"])
    assert blocked.exit_code == 1


def test_cli_build_pr(tmp_path: Path) -> None:
    _repo(tmp_path)
    result = runner.invoke(pe.app, ["build-pr", "build", "dashboard", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "# Phase Build — dashboard" in result.stdout


def test_cli_set_briefing_writes_to_yaml(tmp_path: Path) -> None:
    import yaml

    roadmap = tmp_path / "roadmap.yaml"
    roadmap.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "project": "x",
                "generator_version": "0",
                "phases": [
                    {
                        "id": "build",
                        "name": "Build",
                        "status": "in_execution",
                        "subphases": [{"id": "007", "name": "f", "status": "done", "tasks": []}],
                    }
                ],
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    result = runner.invoke(
        pe.app, ["set-briefing", "007", "Esta etapa fecha a fase.", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    data = yaml.safe_load(roadmap.read_text(encoding="utf-8"))
    assert data["phases"][0]["subphases"][0]["briefing"] == "Esta etapa fecha a fase."


def _combined(result: Result) -> str:
    """stdout+stderr — robusto à versão do click (8.1 mistura; 8.2 separa)."""
    out = result.output or ""
    with contextlib.suppress(ValueError, AttributeError):  # 8.1: stderr já está em output
        out += result.stderr or ""
    return out


def test_cli_session_id_resolved_no_warning() -> None:
    # [ATRITO-91 guard] id presente → imprime o id no stdout, SEM aviso.
    result = runner.invoke(pe.app, ["session-id"], env={"CLAUDE_CODE_SESSION_ID": "sess-xyz"})
    assert result.exit_code == 0
    assert "sess-xyz" in result.stdout
    assert "WSLENV" not in _combined(result)


def test_cli_session_id_unresolved_warns_but_does_not_block() -> None:
    # [ATRITO-91 guard] sem id → AVISA (stderr), mas NÃO bloqueia e mantém o sentinela no stdout.
    result = runner.invoke(pe.app, ["session-id"], env={"CLAUDE_CODE_SESSION_ID": ""})
    assert result.exit_code == 0  # não bloqueia (degradação honesta)
    assert "unresolved" in result.stdout  # sentinela preservado (contrato ATRITO-43)
    assert "WSLENV" in _combined(result)  # aviso acionável presente


# --- CI placeholder warning (ATRITO-97 / feature 027) -----------------------


def _write_ci(root: Path, text: str) -> None:
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(text, encoding="utf-8")


def test_ci_is_placeholder_detects_noop(tmp_path: Path) -> None:
    _write_ci(tmp_path, "jobs:\n  ci:\n    steps:\n      - run: echo Foundation placeholder\n")
    assert pe.ci_is_placeholder(tmp_path) is True


def test_ci_is_placeholder_false_for_real_ci(tmp_path: Path) -> None:
    _write_ci(tmp_path, "jobs:\n  ci:\n    steps:\n      - run: uv run pytest\n")
    assert pe.ci_is_placeholder(tmp_path) is False


def test_ci_is_placeholder_false_when_absent(tmp_path: Path) -> None:
    assert pe.ci_is_placeholder(tmp_path) is False


def test_exit_check_warns_but_does_not_block_on_placeholder_ci(tmp_path: Path) -> None:
    _write_ci(tmp_path, "steps:\n  - run: echo intentionally a no-op\n")
    result = runner.invoke(pe.app, ["exit-check", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0  # aviso, NÃO bloqueia
    assert "placeholder" in _combined(result).lower()
