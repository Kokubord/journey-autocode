"""Project the canonical roadmap.yaml into the report, and read decisions from the ADR files.

The ``roadmap.yaml`` **is** the product of feature-005's passive collection
(``journey_roadmap.consolidate``). :func:`project_report` is a **PROJECTION**, not a collector — it
derives the 15-column table from that single source (FR-009: consumes/derives, does NOT redefine),
mirroring :mod:`journey_core.briefing_ops` at the raw-YAML level so ``journey-core`` need not depend
on ``journey-roadmap``. It **never** re-collects from git/HANDOVER (drift) and **never** fabricates.

:func:`project_decisions` lists the material decisions for the ``decisions`` report by reading the
ADR files in ``docs/adr/`` (a passive source — FR-005), reusing :func:`parse_adr_index` and a light
header read; it does NOT touch git or HANDOVER. :func:`write_report` writes a rendered report to
``docs/reports/`` (FR-006), mirroring ``journey_core.manuals_ops`` (UNC veto — ADR-0004).

**Guard-005:** only keys feature-005 already serializes are read; no new schema field is introduced.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from journey_core.exceptions import JourneyError
from journey_core.models.report import DecisionRow, ReportLevel, ReportRow, ReportTable
from journey_core.parsers.adr import parse_adr_index
from journey_core.writer import guard_write_target

_DONE = "done"  # only the exact ``done`` slug counts as completed (mirrors the 005 cockpit)


def _is_done(status: str | None) -> bool:
    """Completed iff the slug is exactly ``done`` — done_prod/done_early/merged_staging do NOT."""
    return status == _DONE


def _task_statuses(node: dict[str, Any]) -> list[str]:
    """Collect the status of every descendant task (across nested sub-phases)."""
    out: list[str] = []
    subphases: list[dict[str, Any]] = node.get("subphases", []) or []
    for sub in subphases:
        out.extend(_task_statuses(sub))
    tasks: list[dict[str, Any]] = node.get("tasks", []) or []
    for task in tasks:
        status = task.get("status")
        if status:
            out.append(str(status))
    return out


def _derive_progress(status: str | None, task_statuses: list[str]) -> int | None:
    """% avanço, mirroring the 005 cockpit exactly (anti-drift).

    # Mirrors journey-roadmap/render.py:115,203 (exact 'done'; no-tasks binary).
    # Keep in sync — divergence = roadmap reports progress two ways (anti-drift).
    """
    if status == "superseded":
        return None  # ATRITO-73/C3: out of scope — not counted toward progress
    if task_statuses:
        done = sum(1 for s in task_statuses if _is_done(s))
        return round(100 * done / len(task_statuses))
    return 100 if _is_done(status) else 0


def _variance_days(planned_end: str | None, actual_end: str | None) -> int | None:
    """Variação = real − planejado (dias). ``None`` if either end date is missing."""
    if not planned_end or not actual_end:
        return None
    return (date.fromisoformat(actual_end) - date.fromisoformat(planned_end)).days


def _row(node: dict[str, Any], level: ReportLevel, phase_name: str) -> ReportRow:
    """Project a phase or sub-phase node into a full 15-column row + narrative fields."""
    planned: dict[str, Any] = node.get("planned") or {}
    metrics: dict[str, Any] = node.get("metrics") or {}
    status = node.get("status")
    planned_end = planned.get("end")
    actual_end = metrics.get("actual_end")
    return ReportRow(
        level=level,
        phase=phase_name,
        unit="" if level is ReportLevel.PHASE else str(node.get("name", "")),
        status=str(status) if status else "",
        progress_pct=_derive_progress(status, _task_statuses(node)),
        planned_start=planned.get("start"),
        planned_end=planned_end,
        actual_start=metrics.get("actual_start"),
        actual_end=actual_end,
        variance_days=_variance_days(planned_end, actual_end),
        material_decisions=metrics.get("material_decisions"),
        commits=metrics.get("commits"),
        sessions=metrics.get("sessions"),
        tokens=metrics.get("tokens"),
        cost_usd=metrics.get("cost_usd"),
        relevant_info=node.get("notes"),
        briefing=node.get("briefing"),
        deliverable=node.get("deliverable"),
    )


def _task_row(task: dict[str, Any], phase_name: str) -> ReportRow:
    """Project a task node: name + status + narrative; per-task metrics are pendente (decision)."""
    status = task.get("status")
    return ReportRow(
        level=ReportLevel.TASK,
        phase=phase_name,
        unit=str(task.get("name", "")),
        status=str(status) if status else "",
        relevant_info=task.get("notes"),
        briefing=task.get("briefing"),
        deliverable=task.get("deliverable"),
    )


def project_report(roadmap_yaml_path: str | Path) -> ReportTable:
    """Project ``roadmap.yaml`` into the 15-column :class:`ReportTable`.

    Raises:
        JourneyError: If ``roadmap.yaml`` does not exist.
    """
    path = Path(roadmap_yaml_path)
    if not path.is_file():
        raise JourneyError(f"project_report: roadmap.yaml not found at {path}.")
    doc: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows: list[ReportRow] = []
    phases: list[dict[str, Any]] = doc.get("phases", []) or []
    for phase in phases:
        name = str(phase.get("name", ""))
        rows.append(_row(phase, ReportLevel.PHASE, name))
        subphases: list[dict[str, Any]] = phase.get("subphases", []) or []
        for sub in subphases:
            rows.append(_row(sub, ReportLevel.SUBPHASE, name))
            tasks: list[dict[str, Any]] = sub.get("tasks", []) or []
            for task in tasks:
                rows.append(_task_row(task, name))
    return ReportTable(project=str(doc.get("project", "")), rows=rows)


_TITLE_RE = re.compile(r"^#\s*ADR-\d+\s*[—-]\s*(?P<title>.+?)\s*$")
_FIELD_RE = re.compile(r"^\|\s*(?P<key>\w+)\s*\|\s*(?P<val>.+?)\s*\|\s*$")


def _adr_header(path: Path) -> tuple[str | None, str | None, str | None]:
    """Read an ADR file header → (title, status, date). Missing fields → None (never fabricated)."""
    title: str | None = None
    status: str | None = None
    adr_date: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if title is None:
            m = _TITLE_RE.match(line)
            if m is not None:
                title = m.group("title")
                continue
        f = _FIELD_RE.match(line)
        if f is not None:
            key = f.group("key").lower()
            if key == "status":
                status = f.group("val")
            elif key in {"data", "date"}:
                adr_date = f.group("val")
    return title, status, adr_date


def project_decisions(repo_root: str | Path) -> list[DecisionRow]:
    """List the material decisions (ADRs in ``docs/adr/``) for the ``decisions`` report (FR-004).

    Reuses :func:`parse_adr_index` (ordered by number) + a light header read; reads only the ADR
    files (never git/HANDOVER). Title falls back to the slug when no ``# ADR-N — …`` line is found.
    """
    refs = parse_adr_index(Path(repo_root) / "docs" / "adr")
    decisions: list[DecisionRow] = []
    for ref in refs:
        title, status, adr_date = _adr_header(ref.path)
        decisions.append(
            DecisionRow(number=ref.number, title=title or ref.slug, status=status, date=adr_date)
        )
    return decisions


def write_report(repo_root: str | Path, filename: str, content: str) -> Path:
    """Write a rendered report to ``docs/reports/<filename>`` (FR-006); return its path.

    Mirrors ``journey_core.manuals_ops.write_manual`` — routed write, UNC vetoed (ADR-0004).
    """
    target = guard_write_target(Path(repo_root) / "docs" / "reports" / filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target
