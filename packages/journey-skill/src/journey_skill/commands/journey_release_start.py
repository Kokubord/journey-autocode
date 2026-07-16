"""Conducting mechanic for /journey-release-start (feature 009).

Deterministic CLI (mechanic conductor, like 006/007): the SKILL.md **gates** the git mutation;
this does the work. ``preview`` shows the RELEASE-NOTES + version **without mutating** (for the
human gate); ``start`` creates ``release/<version>``, bumps the version file, writes RELEASE-NOTES
and scaffolds cutover/runbook. Core/open — operates in the repo, no external service (FR-007).
FR-008 (cutover/deploy/staging) and FR-009 (release-branch × phase-branch) are **deferred —
não-vivido**.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, NoReturn

import typer
from git import Repo
from journey_core.exceptions import JourneyError
from journey_core.models.release import is_semver
from journey_core.parsers.git_state import commits_since_last_tag
from journey_core.release_ops import (
    build_release_notes,
    read_project_version,
    render_release_notes_md,
    set_project_version,
    write_release_notes,
    write_release_stubs,
)

app = typer.Typer(add_completion=False, help="Abrir a fase Release (feature 009).")

_DEFAULT_VERSION_FILE = "pyproject.toml"


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(1)


def _notes_md(version: str, repo_root: Path) -> str:
    commits = commits_since_last_tag(repo_root)
    return render_release_notes_md(build_release_notes(version, commits))


@app.command("preview")
def preview(
    version: Annotated[str, typer.Argument(help="Versão semver (ex.: v1.0.0).")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    version_file: Annotated[
        str, typer.Option(help="Ficheiro da versão (default pyproject.toml raiz).")
    ] = _DEFAULT_VERSION_FILE,
) -> None:
    """Preview the RELEASE-NOTES + version bump — NO mutation (for the human gate, ADR-0005)."""
    if not is_semver(version):
        _fail(f"versão {version!r} não é semver (ex.: v1.0.0, v1.2.3-beta.1).")
    root = Path(repo_root)
    try:
        current = read_project_version(root / version_file)
        notes = _notes_md(version, root)
    except JourneyError as exc:
        _fail(str(exc))
    typer.echo(f"# versão: {current} → {version.lstrip('v')}\n")
    typer.echo(notes)


@app.command("start")
def start(
    version: Annotated[str, typer.Argument(help="Versão semver (ex.: v1.0.0).")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    version_file: Annotated[
        str, typer.Option(help="Ficheiro da versão (default pyproject.toml raiz).")
    ] = _DEFAULT_VERSION_FILE,
) -> None:
    """Create release/<version>, bump version, write RELEASE-NOTES + cutover/runbook stubs.

    Does NOT commit — git is conducted; the human reviews and commits (ADR-0005).
    """
    if not is_semver(version):
        _fail(f"versão {version!r} não é semver (ex.: v1.0.0).")
    root = Path(repo_root)
    branch = f"release/{version}"
    repo = Repo(root)
    if branch in {head.name for head in repo.heads}:
        _fail(f"branch {branch!r} já existe.")
    try:
        notes = _notes_md(version, root)
        repo.git.checkout("-b", branch)
        set_project_version(root / version_file, version)
        notes_path = write_release_notes(root, version, notes)
        cutover, runbook = write_release_stubs(root, version)
    except JourneyError as exc:
        _fail(str(exc))
    typer.echo(f"branch {branch} criada · versão → {version.lstrip('v')} · {notes_path}")
    typer.echo(f"sugerido (preencher): {cutover} · {runbook}")


def main() -> None:
    """Entry point for the ``journey-release-start`` console script."""
    app()
