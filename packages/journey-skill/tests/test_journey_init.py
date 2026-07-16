# pyright: reportUnknownMemberType=false
import subprocess
from pathlib import Path

from journey_core.models.project_state import ProjectState, Runtime
from journey_skill.commands.journey_init import (
    build_plan,
    conductor_install_hint,
    conductor_skills_source,
    default_templates_dir,
    diagnose_environment,
    environment_problems,
    is_cloud_sync,
    materialize_artifacts,
    materialize_conductors,
    merge_claude,
    render,
    run_init,
    validate_installation,
)


def _ctx() -> dict[str, str]:
    return {
        "project_name": "demo",
        "language": "pt-BR",
        "date": "2026-06-17",
        "remote_url": "git@x:y.git",
    }


def test_render_substitutes_placeholders() -> None:
    assert render("# {{ project_name }}", {"project_name": "demo"}) == "# demo"


def test_render_leaves_unknown_untouched() -> None:
    assert render("{{ unknown }}", {}) == "{{ unknown }}"


def test_build_plan_three_subphases_two_checkpoints() -> None:
    plan = build_plan()
    assert plan.sub_phases[0].value == "pre_ide"
    assert len(plan.checkpoints) == 2


def test_is_cloud_sync() -> None:
    assert is_cloud_sync(Path("/home/u/OneDrive/proj"))
    assert is_cloud_sync(Path("/Users/u/Dropbox/proj"))
    assert not is_cloud_sync(Path("/home/u/projetos/proj"))


def test_diagnose_environment_returns_state(tmp_path: Path) -> None:
    state = diagnose_environment(tmp_path, language="pt-BR")
    assert state.os
    assert isinstance(state.git_present, bool)
    assert state.preexisting_artifacts == []


def test_environment_problems_flags_missing_git() -> None:
    bad = ProjectState(runtime=Runtime.NATIVE, os="x", git_present=False)
    assert any("git" in p for p in environment_problems(bad))
    good = ProjectState(runtime=Runtime.NATIVE, os="x", git_present=True)
    assert environment_problems(good) == []


def test_merge_claude_first_run_wraps_block() -> None:
    out = merge_claude(None, "JOURNEY RULES")
    assert "BEGIN JOURNEY" in out and "JOURNEY RULES" in out


def test_merge_claude_is_idempotent() -> None:
    once = merge_claude(None, "RULES")
    twice = merge_claude(once, "RULES")
    assert once == twice


def test_merge_claude_preserves_user_content() -> None:
    existing = "# Meu CLAUDE.md\nregras do usuário\n"
    out = merge_claude(existing, "JOURNEY")
    assert "regras do usuário" in out and "JOURNEY" in out


def test_materialize_creates_then_preserves(tmp_path: Path) -> None:
    first = materialize_artifacts(default_templates_dir(), tmp_path, _ctx())
    assert len(first["created"]) == 11 and first["preserved"] == []
    second = materialize_artifacts(default_templates_dir(), tmp_path, _ctx())
    assert second["created"] == [] and len(second["preserved"]) == 11


def test_run_init_idempotent_rerun(tmp_path: Path) -> None:
    first = run_init(
        project_name="demo",
        target=tmp_path,
        yes=True,
        skip_spec_kit=True,
        username="t",
        email="t@e.com",
    )
    assert first["committed"] is True and first["validated"] is True
    snapshot = (tmp_path / "HANDOVER.md").read_text(encoding="utf-8")
    second = run_init(
        project_name="demo",
        target=tmp_path,
        yes=True,
        skip_spec_kit=True,
        username="t",
        email="t@e.com",
    )
    assert second["committed"] is False  # nothing to commit on re-run
    assert second["commit"] == first["commit"]  # same HEAD — nothing destroyed
    assert (tmp_path / "HANDOVER.md").read_text(encoding="utf-8") == snapshot


def test_validate_installation_after_init(tmp_path: Path) -> None:
    run_init(
        project_name="demo",
        target=tmp_path,
        yes=True,
        skip_spec_kit=True,
        username="t",
        email="t@e.com",
    )
    ok, problems = validate_installation(tmp_path)
    assert ok and problems == []


# --- Conductors + constitution (ADR-0050 / ATRITO-92 / ATRITO-93) -----------


def _make_base(tmp_path: Path) -> Path:
    """A fake base: templates/ + sibling .claude/skills with journey-* and a foreign skill."""
    base = tmp_path / "base"
    (base / "templates").mkdir(parents=True)
    skills = base / ".claude" / "skills"
    for name in ("journey-discover", "journey-decision", "journey-bootstrap"):
        (skills / name).mkdir(parents=True)
        (skills / name / "SKILL.md").write_text(f"# {name}", encoding="utf-8")
    (skills / "speckit-plan").mkdir(parents=True)
    (skills / "speckit-plan" / "SKILL.md").write_text("# speckit", encoding="utf-8")
    return base


def test_conductors_embark_journey_except_bootstrap(tmp_path: Path) -> None:
    base = _make_base(tmp_path)
    target = tmp_path / "proj"
    target.mkdir()
    result = materialize_conductors(base / "templates", target)
    assert set(result["copied"]) == {"journey-decision", "journey-discover"}
    assert (target / ".claude/skills/journey-discover/SKILL.md").is_file()
    assert not (target / ".claude/skills/journey-bootstrap").exists()


def test_conductors_never_touch_user_or_foreign_skills(tmp_path: Path) -> None:
    base = _make_base(tmp_path)
    target = tmp_path / "proj"
    mine = target / ".claude" / "skills" / "my-skill"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text("MINE", encoding="utf-8")
    materialize_conductors(base / "templates", target)
    assert (mine / "SKILL.md").read_text(encoding="utf-8") == "MINE"
    assert not (target / ".claude/skills/speckit-plan").exists()


def test_conductors_idempotent(tmp_path: Path) -> None:
    base = _make_base(tmp_path)
    target = tmp_path / "proj"
    target.mkdir()
    first = materialize_conductors(base / "templates", target)
    second = materialize_conductors(base / "templates", target)
    assert first == second


def test_conductors_missing_source_is_noop(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    assert materialize_conductors(tmp_path / "absent" / "templates", target) == {"copied": []}


def test_conductor_install_hint_uses_wheels_not_editable_source(tmp_path: Path) -> None:
    hint = conductor_install_hint(tmp_path / "base")
    # FR-006: instruct a wheel install (journey-core copied), never the editable source (--from).
    assert "uv build --wheel" in hint and "--find-links" in hint
    assert "--from" not in hint
    assert "journey-skill" in hint and "journey-roadmap" in hint


def test_constitution_journey_wins_over_speckit_placeholder(tmp_path: Path) -> None:
    memory = tmp_path / ".specify" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(
        "# [PROJECT_NAME] Constitution\n### [PRINCIPLE_1_NAME]\n", encoding="utf-8"
    )
    result = materialize_artifacts(default_templates_dir(), tmp_path, _ctx())
    text = (memory / "constitution.md").read_text(encoding="utf-8")
    assert "[PROJECT_NAME]" not in text
    assert ".specify/memory/constitution.md" in result["merged"]


def test_constitution_preserves_authored_content(tmp_path: Path) -> None:
    memory = tmp_path / ".specify" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text("# DashMoney autorada\n", encoding="utf-8")
    materialize_artifacts(default_templates_dir(), tmp_path, _ctx())
    assert "autorada" in (memory / "constitution.md").read_text(encoding="utf-8")


# --- Packaging: bundled resolution + curated staging (feature 024) ----------


def test_conductor_skills_source_prefers_bundled_sibling(tmp_path: Path) -> None:
    templates = tmp_path / "_bundled" / "templates"
    templates.mkdir(parents=True)
    (tmp_path / "_bundled" / "skills").mkdir()
    assert conductor_skills_source(templates) == tmp_path / "_bundled" / "skills"


def test_conductor_skills_source_falls_back_to_dot_claude(tmp_path: Path) -> None:
    templates = tmp_path / "base" / "templates"
    templates.mkdir(parents=True)
    claude_skills = tmp_path / "base" / ".claude" / "skills"
    claude_skills.mkdir(parents=True)
    assert conductor_skills_source(templates) == claude_skills


def test_run_init_curated_staging_skips_stray_dir(tmp_path: Path) -> None:
    stray = tmp_path / ".journey-base"
    stray.mkdir()
    (stray / "huge.txt").write_text("x", encoding="utf-8")
    run_init(
        project_name="demo",
        target=tmp_path,
        yes=True,
        skip_spec_kit=True,
        username="t",
        email="t@e.com",
    )
    tracked = subprocess.run(
        ["git", "-C", str(tmp_path), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert ".journey-base/huge.txt" not in tracked  # curated staging never swept the stray clone
    assert "HANDOVER.md" in tracked
    assert ".claude/skills/journey-discover/SKILL.md" in tracked
