"""Tests for the release models + release_ops (feature 009)."""

from datetime import UTC, datetime
from pathlib import Path

from journey_core.models.release import is_semver
from journey_core.parsers.git_state import CommitInfo
from journey_core.release_ops import (
    build_release_notes,
    read_project_version,
    render_release_notes_md,
    set_project_version,
    write_release_notes,
    write_release_stubs,
)


def _c(summary: str) -> CommitInfo:
    return CommitInfo(
        sha="abcdef1234567", authored_at=datetime(2026, 6, 18, tzinfo=UTC), summary=summary
    )


def test_is_semver() -> None:
    assert is_semver("v1.0.0")
    assert is_semver("1.2.3-beta.1")
    assert not is_semver("1.0")
    assert not is_semver("abc")


def test_build_release_notes_groups_by_prefix_and_parses_adr() -> None:
    notes = build_release_notes(
        "v1.0.0",
        [
            _c("feat(x): nova coisa"),
            _c("fix: corrige y"),
            _c("DECISION(z): escolha [ADR-0019]"),
            _c("chore: limpeza"),
        ],
    )
    assert [e.summary for e in notes.features] == ["feat(x): nova coisa"]
    assert [e.summary for e in notes.fixes] == ["fix: corrige y"]
    assert notes.decisions[0].adr_refs == [19]
    assert [e.summary for e in notes.others] == ["chore: limpeza"]  # unknown prefix -> others


def test_render_includes_sections_and_adr_and_short_sha() -> None:
    md = render_release_notes_md(build_release_notes("v1.0.0", [_c("DECISION(z): x [ADR-0019]")]))
    assert "# RELEASE NOTES — v1.0.0" in md
    assert "## Decisões arquiteturais" in md
    assert "ADR-0019" in md
    assert "abcdef1" in md  # short sha (7)


def test_render_empty_notes_states_no_commits() -> None:
    md = render_release_notes_md(build_release_notes("v1.0.0", []))
    assert "Sem commits desde a última tag" in md


def test_version_read_and_write_strips_leading_v(tmp_path: Path) -> None:
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nname = "x"\nversion = "0.0.0"\n', encoding="utf-8")
    assert read_project_version(p) == "0.0.0"
    set_project_version(p, "v1.2.3")
    assert read_project_version(p) == "1.2.3"  # leading v stripped (PEP 440)


def test_write_release_notes(tmp_path: Path) -> None:
    path = write_release_notes(tmp_path, "v1.0.0", "# x\n")
    assert path == tmp_path / "RELEASE-NOTES-v1.0.0.md"
    assert path.read_text(encoding="utf-8") == "# x\n"


def test_release_stubs_are_scaffolds_not_fabricated(tmp_path: Path) -> None:
    cutover, runbook = write_release_stubs(tmp_path, "v1.0.0")
    assert cutover == tmp_path / "docs" / "release" / "cutover-plan-v1.0.0.md"
    ct = cutover.read_text(encoding="utf-8")
    assert "# Cutover plan — v1.0.0" in ct
    assert "preencher" in ct  # operator's responsibility — scaffold, not content
    assert "## Passos" in ct
    assert "## Rollback" in ct
    rb = runbook.read_text(encoding="utf-8")
    assert "# Runbook — v1.0.0" in rb
    assert "## Procedimento" in rb
