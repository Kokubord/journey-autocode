"""Shared briefing write op for the roadmap (ADR-0018, Fatia 3).

The conducting skills (``journey-phase-end`` first; the others in Fatia 3b) author a unit's
rich ``briefing`` at write-time. :func:`set_briefing` is the **single source** they reuse to
persist it — no parallel implementation (anti-drift, eco do :mod:`journey_core.adr_ops` /
ATRITO-61).

It works at the raw-YAML/dict level on purpose: ``journey-core`` does NOT depend on
``journey-roadmap`` (dependency direction), so it cannot import the roadmap schema. The
briefing is simply persisted in ``roadmap.yaml``; the feature-005 ``merge_authored`` preserves
it **by id** across regenerations. NEVER fabricates — only the given ``unit_id`` is set; no node
is created and no other field/node is touched; an unknown id (or empty briefing) raises. Writes
are routed through the repository runtime and UNC paths are vetoed (ADR-0004).

The briefing TEXT is authored by the skill following the tone directive in
``docs/design/roadmap-render-fase-a.md`` (§ Tom e qualidade) — this module only writes it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from journey_core.exceptions import JourneyError
from journey_core.writer import guard_write_target

# The three AUTHORED narrative fields of a roadmap node (ADR-0018 + Fatia 6):
# ``briefing`` (conceptual — popup "o que é/para que serve"), ``deliverable`` (popup
# "Entregável") and ``notes`` (execution history — the "informações" column + popup footnote).
NARRATIVE_FIELDS: tuple[str, ...] = ("briefing", "deliverable", "notes")


@dataclass(frozen=True)
class UnnourishedUnit:
    """A roadmap unit (phase/sub-phase/task) missing one or more authored narrative fields.

    Carries just enough for a conducting skill to author the texts from real sources: the
    ``id`` (to write back via :func:`set_briefing`/:func:`set_deliverable`/:func:`set_notes`),
    human ``name`` and ``status``, the ``level`` (0 phase, 1 sub-phase, 2 task), the
    ``summary_ref`` pointer (``ref_doc``/``ref_anchor``) so the author reads the source, and
    ``missing`` — which of :data:`NARRATIVE_FIELDS` are still empty. NEVER fabricated.
    """

    id: str
    name: str
    status: str
    level: int
    ref_doc: str | None
    ref_anchor: str | None
    missing: tuple[str, ...]


def _find_unit(doc: dict[str, Any], unit_id: str) -> dict[str, Any] | None:
    """Return the phase/sub-phase/task node whose ``id`` equals ``unit_id`` (or ``None``).

    Phase and sub-phase ids are unique; a bare task id (e.g. ``T001``) is not unique across
    features and is not the pilot's target (Fatia 3a nourishes phase/sub-phase units).
    """
    phases: list[dict[str, Any]] = doc.get("phases", [])
    for phase in phases:
        if phase.get("id") == unit_id:
            return phase
        subphases: list[dict[str, Any]] = phase.get("subphases", [])
        for sub in subphases:
            if sub.get("id") == unit_id:
                return sub
            tasks: list[dict[str, Any]] = sub.get("tasks", [])
            for task in tasks:
                if task.get("id") == unit_id:
                    return task
    return None


def _set_field(roadmap_yaml_path: str | Path, unit_id: str, field: str, text: str) -> Path:
    """Author one narrative ``field`` of unit ``unit_id`` in ``roadmap.yaml`` (single source).

    Shared write op for the three narrative fields. Sets ONLY the given field of the given
    unit; no node is created and nothing else is touched. NEVER fabricates — an empty text or
    an unknown id raises. Writes are routed through the runtime; UNC paths are vetoed (ADR-0004).
    """
    if field not in NARRATIVE_FIELDS:
        raise JourneyError(f"_set_field: {field!r} is not a narrative field {NARRATIVE_FIELDS}.")
    if not text.strip():
        raise JourneyError(f"set_{field} refuses an empty value (anti-fabrication, ADR-0018).")
    target = guard_write_target(roadmap_yaml_path)
    doc: dict[str, Any] = yaml.safe_load(target.read_text(encoding="utf-8"))
    unit = _find_unit(doc, unit_id)
    if unit is None:
        raise JourneyError(f"set_{field}: unit id {unit_id!r} not found in {target}.")
    unit[field] = text
    target.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target


def set_briefing(roadmap_yaml_path: str | Path, unit_id: str, briefing: str) -> Path:
    """Author the conceptual ``briefing`` (popup "o que é · para que serve") — ADR-0018."""
    return _set_field(roadmap_yaml_path, unit_id, "briefing", briefing)


def set_deliverable(roadmap_yaml_path: str | Path, unit_id: str, deliverable: str) -> Path:
    """Author the ``deliverable`` (popup "Entregável") — ADR-0018 Fatia 6."""
    return _set_field(roadmap_yaml_path, unit_id, "deliverable", deliverable)


def set_notes(roadmap_yaml_path: str | Path, unit_id: str, notes: str) -> Path:
    """Author the execution ``notes`` (the "informações" column — history) — ADR-0018 Fatia 6."""
    return _set_field(roadmap_yaml_path, unit_id, "notes", notes)


def _ref_of(node: dict[str, Any]) -> tuple[str | None, str | None]:
    ref: dict[str, Any] = node.get("summary_ref") or {}
    return ref.get("doc"), ref.get("anchor")


def _missing_narratives(node: dict[str, Any]) -> tuple[str, ...]:
    """Which of :data:`NARRATIVE_FIELDS` are still empty on ``node`` (document order)."""
    missing: list[str] = []
    for field in NARRATIVE_FIELDS:
        value = node.get(field)
        if not (isinstance(value, str) and value.strip()):
            missing.append(field)
    return tuple(missing)


def list_unnourished(
    roadmap_yaml_path: str | Path, *, include_tasks: bool = False
) -> list[UnnourishedUnit]:
    """Enumerate roadmap units missing any authored narrative field (ADR-0018, Fatia 5/6).

    Read-only. A unit appears if any of :data:`NARRATIVE_FIELDS` (briefing/deliverable/notes)
    is still empty, with ``missing`` listing which. Phases and sub-phases are returned by
    default; tasks are excluded unless ``include_tasks`` is set, because tasks carry a
    proportional ``name`` and no rich narrative by design (ATRITO-33). Order is document order
    (phase, then its sub-phases). This only **reports** the gap — a conducting skill
    (``journey-roadmap-nourish``) authors each field from the unit's real sources and persists
    it via the ``set_*`` ops. NEVER fabricates.

    Args:
        roadmap_yaml_path: Path to the canonical ``roadmap.yaml``.
        include_tasks: When true, also list task-level units missing a narrative field.

    Returns:
        The units missing one or more narrative fields, in document order.
    """
    target = Path(roadmap_yaml_path)
    doc: dict[str, Any] = yaml.safe_load(target.read_text(encoding="utf-8"))

    def _unit(node: dict[str, Any], level: int) -> UnnourishedUnit | None:
        missing = _missing_narratives(node)
        if not missing:
            return None
        doc_ref, anchor = _ref_of(node)
        return UnnourishedUnit(
            node["id"],
            node.get("name", ""),
            node.get("status", ""),
            level,
            doc_ref,
            anchor,
            missing,
        )

    out: list[UnnourishedUnit] = []
    for phase in doc.get("phases", []):
        unit = _unit(phase, 0)
        if unit is not None:
            out.append(unit)
        for sub in phase.get("subphases", []):
            unit = _unit(sub, 1)
            if unit is not None:
                out.append(unit)
            if include_tasks:
                for task in sub.get("tasks", []):
                    unit = _unit(task, 2)
                    if unit is not None:
                        out.append(unit)
    return out
