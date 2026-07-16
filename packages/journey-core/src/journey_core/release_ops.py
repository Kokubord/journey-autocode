"""Build + render RELEASE-NOTES, read/write the version, and scaffold cutover/runbook (feature 009).

Deterministic: groups commits-since-last-tag by their **conventional prefix** (feat / fix /
DECISION), links ADR refs parsed from the message, and **never fabricates** — a commit without a
known prefix goes to "Outros" (never dropped, never guessed). Reuses
:mod:`journey_core.parsers.git_state` (``CommitInfo``). Writes are routed; UNC is vetoed (ADR-0004).
The version bump touches **only the given file** — the monorepo multi-package policy is NOT decided
here (FR-004 underspecified). The cutover/runbook are **scaffolds only** (headings + TODO); the
deploy content is the operator's and is never fabricated (FR-006; FR-007/FR-008 deferred).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from journey_core.exceptions import JourneyError
from journey_core.models.release import ReleaseEntry, ReleaseNotes
from journey_core.parsers.git_state import CommitInfo
from journey_core.writer import guard_write_target

_ADR_REF_RE = re.compile(r"\[ADR-(\d+)\]")
_VERSION_LINE_RE = re.compile(r'^(version\s*=\s*")[^"]*(")', re.MULTILINE)

_CUTOVER_STUB = """# Cutover plan — {version}

> Esqueleto a **preencher** (responsabilidade do operador). Os passos de cutover/deploy/staging são
> project-specific e **não** são gerados pelo Journey (FR-007/FR-008, não-vivido).

## Pré-requisitos

## Passos

## Rollback
"""

_RUNBOOK_STUB = """# Runbook — {version}

> Esqueleto a **preencher** (responsabilidade do operador). A execução de deploy é project-specific
> e **não** é gerada pelo Journey (FR-007/FR-008, não-vivido).

## Pré-requisitos

## Procedimento

## Verificação

## Rollback
"""


def _entry(commit: CommitInfo) -> ReleaseEntry:
    refs = [int(n) for n in _ADR_REF_RE.findall(commit.summary)]
    return ReleaseEntry(sha=commit.sha[:7], summary=commit.summary, adr_refs=refs)


def build_release_notes(version: str, commits: list[CommitInfo]) -> ReleaseNotes:
    """Group commits by conventional prefix (FR-005). Unknown prefix → 'others' (never dropped)."""
    notes = ReleaseNotes(version=version)
    for commit in commits:
        entry = _entry(commit)
        summary = commit.summary
        if summary.startswith("feat"):
            notes.features.append(entry)
        elif summary.startswith("fix"):
            notes.fixes.append(entry)
        elif summary.startswith("DECISION"):
            notes.decisions.append(entry)
        else:
            notes.others.append(entry)
    return notes


def _section(title: str, entries: list[ReleaseEntry]) -> list[str]:
    if not entries:
        return []
    lines = [f"## {title}", ""]
    for e in entries:
        adr = f" ({', '.join(f'ADR-{n:04d}' for n in e.adr_refs)})" if e.adr_refs else ""
        lines.append(f"- `{e.sha}` {e.summary}{adr}")
    lines.append("")
    return lines


def render_release_notes_md(notes: ReleaseNotes) -> str:
    """Render the RELEASE-NOTES Markdown grouped by type; empty groups are omitted (FR-005)."""
    lines = [f"# RELEASE NOTES — {notes.version}", ""]
    lines += _section("Features", notes.features)
    lines += _section("Fixes", notes.fixes)
    lines += _section("Decisões arquiteturais", notes.decisions)
    lines += _section("Outros", notes.others)
    total = len(notes.features) + len(notes.fixes) + len(notes.decisions) + len(notes.others)
    if total == 0:
        lines.append("_Sem commits desde a última tag._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def read_project_version(version_file: str | Path) -> str:
    """Read ``[project].version`` from a pyproject.toml (FR-003)."""
    path = Path(version_file)
    if not path.is_file():
        raise JourneyError(f"version file not found: {path}")
    data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    project: dict[str, Any] = data.get("project", {})
    version = project.get("version")
    if version is None:
        raise JourneyError(f"no [project].version in {path}")
    return str(version)


def set_project_version(version_file: str | Path, new_version: str) -> Path:
    """Update ``[project].version`` in a pyproject.toml (FR-004); leading ``v`` stripped (PEP 440).

    Touches only the given file; monorepo multi-package versioning is NOT decided here.

    Raises:
        JourneyError: If no ``version = "..."`` line is present.
    """
    target = guard_write_target(version_file)
    text = target.read_text(encoding="utf-8")
    clean = new_version.lstrip("v")
    updated, n = _VERSION_LINE_RE.subn(rf"\g<1>{clean}\g<2>", text, count=1)
    if n == 0:
        raise JourneyError(f'no version = "..." line to update in {target}')
    target.write_text(updated, encoding="utf-8")
    return target


def write_release_notes(repo_root: str | Path, version: str, content: str) -> Path:
    """Write ``RELEASE-NOTES-<version>.md`` at the repo root (FR-005); return its path."""
    target = guard_write_target(Path(repo_root) / f"RELEASE-NOTES-{version}.md")
    target.write_text(content, encoding="utf-8")
    return target


def write_release_stubs(repo_root: str | Path, version: str) -> tuple[Path, Path]:
    """Write empty cutover-plan/runbook **scaffolds** in ``docs/release/`` (FR-006); return paths.

    SCAFFOLD ONLY — headings + empty TODO sections. The content (deploy steps) is the operator's and
    is **never fabricated** (FR-007/FR-008 deferred). Creates ``docs/release/`` if absent.
    """
    base = Path(repo_root) / "docs" / "release"
    cutover = guard_write_target(base / f"cutover-plan-{version}.md")
    runbook = guard_write_target(base / f"runbook-{version}.md")
    base.mkdir(parents=True, exist_ok=True)
    cutover.write_text(_CUTOVER_STUB.format(version=version), encoding="utf-8")
    runbook.write_text(_RUNBOOK_STUB.format(version=version), encoding="utf-8")
    return cutover, runbook
