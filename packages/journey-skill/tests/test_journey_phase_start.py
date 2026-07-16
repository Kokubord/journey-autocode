import json
from pathlib import Path

import pytest
from git import Repo
from journey_core.exceptions import JourneyError
from journey_core.models import Phase
from journey_skill.commands.journey_phase_start import (
    app,
    check_discovery_completeness,
    configure_pr_template,
    create_phase_branch,
    mark_active,
    oversized_features,
    phase_branch_name,
    phase_checklist,
    should_create_branch,
    validate_phase,
)
from typer.testing import CliRunner

runner = CliRunner()

_HANDOVER = (
    "## Meta\n\n| Campo | Valor |\n|---|---|\n"
    "| **Última atualização** | 2026-06-17 |\n"
    "| **Fase atual** | Discovery — workshop (ativa) |\n"
)


def _git_repo(tmp_path: Path) -> Path:
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "T")
    repo.git.config("user.email", "t@t")
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    repo.git.add("f.txt")
    repo.git.commit("-m", "init")
    return tmp_path


def test_validate_phase_ok_and_case_insensitive() -> None:
    assert validate_phase("build") is Phase.BUILD
    assert validate_phase("  Discovery ") is Phase.DISCOVERY


def test_validate_phase_invalid() -> None:
    with pytest.raises(JourneyError):
        validate_phase("sprint")


def test_mark_active_writes_and_preserves_previous(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text(_HANDOVER, encoding="utf-8")
    state = mark_active(tmp_path, Phase.BUILD, "dashboard")
    assert state.previous == "Discovery — workshop (ativa)"
    assert "Build — sub-fase **dashboard** (ativa)" in (tmp_path / "HANDOVER.md").read_text(
        encoding="utf-8"
    )


def test_phase_checklist_nonempty() -> None:
    assert phase_checklist(Phase.BUILD)


def test_should_create_branch_policy() -> None:
    assert should_create_branch(Phase.BUILD, 2) is True
    assert should_create_branch(Phase.BUILD, 1) is False
    assert should_create_branch(Phase.DISCOVERY, 3) is False


def test_phase_branch_name() -> None:
    assert phase_branch_name(6, "journey-phase-start") == "feat/phase-6-journey-phase-start"


def test_create_phase_branch_and_duplicate(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    name = create_phase_branch(root, "feat/phase-6-x")
    assert name == "feat/phase-6-x"
    assert "feat/phase-6-x" in {h.name for h in Repo(root).heads}
    with pytest.raises(JourneyError):
        create_phase_branch(root, "feat/phase-6-x")


def test_configure_pr_template_idempotent(tmp_path: Path) -> None:
    first = configure_pr_template(tmp_path)
    assert first is not None and first.exists()
    assert configure_pr_template(tmp_path) is None  # already present


def test_cli_read_state_and_mark(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text(_HANDOVER, encoding="utf-8")
    r1 = runner.invoke(app, ["read-state", "--repo-root", str(tmp_path)])
    assert r1.exit_code == 0 and "Discovery — workshop (ativa)" in r1.stdout
    r2 = runner.invoke(app, ["mark", "build", "dashboard", "--repo-root", str(tmp_path)])
    assert r2.exit_code == 0 and "Build — sub-fase **dashboard** (ativa)" in r2.stdout


def test_cli_mark_invalid_phase(tmp_path: Path) -> None:
    (tmp_path / "HANDOVER.md").write_text(_HANDOVER, encoding="utf-8")
    result = runner.invoke(app, ["mark", "sprint", "x", "--repo-root", str(tmp_path)])
    assert result.exit_code != 0


def test_cli_branch(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    result = runner.invoke(
        app, ["branch", "--n", "6", "--slug", "dashboard", "--repo-root", str(root)]
    )
    assert result.exit_code == 0
    assert "feat/phase-6-dashboard" in {h.name for h in Repo(root).heads}
    assert (root / ".github" / "pull_request_template.md").exists()


def test_set_briefing_writes_opening_briefing(tmp_path: Path) -> None:
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
                        "subphases": [{"id": "010", "name": "f", "status": "next", "tasks": []}],
                    }
                ],
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    result = runner.invoke(
        app, ["set-briefing", "010", "Abre a fase X: prepara Y.", "--repo-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    data = yaml.safe_load(roadmap.read_text(encoding="utf-8"))
    assert data["phases"][0]["subphases"][0]["briefing"] == "Abre a fase X: prepara Y."


def test_set_briefing_tolerates_absent_roadmap(tmp_path: Path) -> None:
    result = runner.invoke(app, ["set-briefing", "build", "x", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0  # tolerates absent roadmap.yaml (warn + exit 0)
    assert not (tmp_path / "roadmap.yaml").exists()  # did not fabricate


# --- Discovery→Build gate (ATRITO-41 / feature 025) -------------------------


def _feature(root: Path, name: str, *, plan: bool = True, tasks: str = "- [ ] T001 do it") -> None:
    d = root / "specs" / name
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# spec", encoding="utf-8")
    if plan:
        (d / "plan.md").write_text("# plan", encoding="utf-8")
    (d / "tasks.md").write_text(tasks, encoding="utf-8")


def _constitution(root: Path, text: str) -> None:
    memory = root / ".specify" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(text, encoding="utf-8")


def test_check_discovery_complete_when_all_features_full(tmp_path: Path) -> None:
    _constitution(tmp_path, "# Proj — Constituição ratificada 1.0.0")
    _feature(tmp_path, "001-a")
    _feature(tmp_path, "002-b")
    assert check_discovery_completeness(tmp_path) == []


def test_check_discovery_flags_skeleton_feature(tmp_path: Path) -> None:
    _constitution(tmp_path, "# Proj — Constituição ratificada 1.0.0")
    _feature(tmp_path, "001-a")
    _feature(tmp_path, "002-b", plan=False)  # skeleton: no plan.md
    gaps = check_discovery_completeness(tmp_path)
    assert any("002-b" in g and "plan.md" in g for g in gaps)
    assert not any("001-a" in g for g in gaps)


def test_check_discovery_flags_empty_tasks(tmp_path: Path) -> None:
    _constitution(tmp_path, "# Proj — Constituição ratificada")
    _feature(tmp_path, "001-a", tasks="# Tasks\n(nenhuma ainda)")
    gaps = check_discovery_completeness(tmp_path)
    assert any("001-a" in g and "sem tarefa" in g for g in gaps)


def test_check_discovery_flags_placeholder_constitution(tmp_path: Path) -> None:
    _constitution(tmp_path, "# X — Constituição (Placeholder)")
    _feature(tmp_path, "001-a")
    gaps = check_discovery_completeness(tmp_path)
    assert any("PLACEHOLDER" in g for g in gaps)


def test_check_discovery_cli_reports_gaps_json(tmp_path: Path) -> None:
    _constitution(tmp_path, "# Proj — Constituição ratificada")
    _feature(tmp_path, "001-a", plan=False)
    result = runner.invoke(app, ["check-discovery", "--repo-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["complete"] is False and payload["gaps"]


# --- Sub-phase granularity advice (ATRITO-96 / feature 026) ------------------


def _many_tasks(n: int) -> str:
    return "\n".join(f"- [ ] T{i:03d} do thing {i}" for i in range(1, n + 1))


def test_oversized_features_flags_big_not_small(tmp_path: Path) -> None:
    _feature(tmp_path, "001-small", tasks="- [ ] T001 do it")
    _feature(tmp_path, "002-big", tasks=_many_tasks(20))
    names = [name for name, _ in oversized_features(tmp_path, max_tasks=12)]
    assert "002-big" in names and "001-small" not in names


def test_oversized_features_respects_threshold(tmp_path: Path) -> None:
    _feature(tmp_path, "001-a", tasks=_many_tasks(10))
    assert oversized_features(tmp_path, max_tasks=12) == []
    assert oversized_features(tmp_path, max_tasks=5) == [("001-a", 10)]


def test_subphase_advice_cli_lists_candidates(tmp_path: Path) -> None:
    _feature(tmp_path, "001-big", tasks=_many_tasks(30))
    result = runner.invoke(
        app, ["subphase-advice", "--repo-root", str(tmp_path), "--max-tasks", "12"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["slice_candidates"][0]["feature"] == "001-big"
    assert payload["slice_candidates"][0]["tasks"] == 30
