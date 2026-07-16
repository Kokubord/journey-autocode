"""journey-phase-start — deterministic mechanic for opening a phase (feature 006).

Per ADR-0017 Decision 1, /journey-phase-start is a *conducting* command. Because its
nature is mostly mechanical (validate, read/write HANDOVER state, conditional branch,
templated checklist), it follows the **mechanical-conductor sub-pattern**: a thin skill
(`.claude/skills/journey-phase-start/SKILL.md`) conducts and gates, and the bulk lives
here as tested deterministic mechanic. The checklist is templated (journey-core), not
LLM-improvised.

All file writes are routed through the repository runtime and UNC paths are vetoed
(ADR-0004). Git is conducted by Journey with a human gate; the Spec Kit auto-commit
stays off (ADR-0005). Real host execution (main protection, PR open/merge) is deferred
(FR-008 — no Build phase has been lived).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated

import typer
from git import Repo
from journey_core.exceptions import JourneyError
from journey_core.models.phase_state import Phase, PhaseState, checklist_for
from journey_core.parsers.phase import read_active_phase, set_active_phase
from journey_core.writer import guard_write_target

app = typer.Typer(help="Deterministic mechanic for /journey-phase-start (feature 006).")

HANDOVER = "HANDOVER.md"
PR_TEMPLATE = ".github/pull_request_template.md"

#: Discovery-completeness (ATRITO-41 / §3.2): each feature needs these; constitution ratified.
_DISCOVERY_FILES = ("spec.md", "plan.md", "tasks.md")
_PLACEHOLDER_MARKERS = ("(Placeholder)", "[PROJECT_NAME]", "[PRINCIPLE_1_NAME]")
_TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+", re.MULTILINE)

_PR_TEMPLATE_BODY = """## Resumo

<!-- O que esta fase/sub-fase entrega. -->

## Tasks completadas

## ADRs criados

## Decisões materiais

## Checklist de validação

- [ ] Bateria verde (ruff/format/mypy/pyright/pytest)
- [ ] HANDOVER atualizado
- [ ] Gate do owner para merge (squash — §6.4)
"""


def validate_phase(value: str) -> Phase:
    """Coerce ``value`` into a canonical :class:`Phase`, or raise (FR-001).

    Args:
        value: The phase name (case-insensitive).

    Returns:
        The matching :class:`Phase`.

    Raises:
        JourneyError: If ``value`` is not one of the six canonical phases.
    """
    try:
        return Phase(value.strip().lower())
    except ValueError as exc:
        valid = ", ".join(p.value for p in Phase)
        raise JourneyError(f"fase inválida {value!r}; use uma de: {valid}") from exc


def mark_active(repo_root: str | Path, phase: Phase, slug: str) -> PhaseState:
    """Read the previous phase and mark ``phase``/``slug`` active in HANDOVER (FR-002/003).

    The previous value is preserved on the returned state — it is not overwritten
    blindly (FR-002).
    """
    handover = Path(repo_root) / HANDOVER
    previous = read_active_phase(handover)
    state = PhaseState(phase=phase, slug=slug, active=True, previous=previous)
    set_active_phase(handover, state)
    return state


def phase_checklist(phase: Phase) -> list[str]:
    """Return the templated checklist for ``phase`` (FR-005)."""
    return checklist_for(phase)


def should_create_branch(phase: Phase, subphase_index: int) -> bool:
    """Branch governance policy (FR-004): only from the 2nd Build sub-phase onward.

    Args:
        phase: The phase being opened.
        subphase_index: 1-based sub-phase ordinal within the phase.

    Returns:
        ``True`` only when ``phase`` is Build and ``subphase_index >= 2``.
    """
    return phase is Phase.BUILD and subphase_index >= 2


def phase_branch_name(n: int, slug: str) -> str:
    """Canonical phase branch name ``feat/phase-N-<slug>`` (FR-004, CLAUDE.md §6.2)."""
    return f"feat/phase-{n}-{slug}"


def configure_pr_template(repo_root: str | Path) -> Path | None:
    """Write a PR template if absent (FR-004); return its path, or ``None`` if present."""
    target = guard_write_target(Path(repo_root) / PR_TEMPLATE)
    if target.exists():
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_PR_TEMPLATE_BODY, encoding="utf-8")
    return target


def create_phase_branch(repo_root: str | Path, name: str) -> str:
    """Create and check out a local phase branch via git (FR-004/006).

    The human gate (ADR-0005) is conducted by the skill before this is invoked; the
    branch is local only (push/PR on the host is deferred — FR-008).

    Raises:
        JourneyError: If the branch already exists.
    """
    repo = Repo(Path(repo_root))
    if name in {head.name for head in repo.heads}:
        raise JourneyError(f"branch {name!r} já existe")
    repo.git.checkout("-b", name)
    return name


def check_discovery_completeness(repo_root: str | Path) -> list[str]:
    """Return Discovery-completeness gaps (ATRITO-41 / methodology §3.2); empty list = complete.

    Discovery delivers the COMPLETE plan: every feature has spec+plan+tasks (>=1 task, ADR-0043)
    and the constitution is ratified (not a placeholder). Features left as roadmap skeleton are
    the gaps this surfaces before Build — the conductor warns and gates on them (no hard block).
    """
    root = Path(repo_root)
    gaps: list[str] = []
    constitution = root / ".specify" / "memory" / "constitution.md"
    if not constitution.is_file():
        gaps.append("constituição ausente (.specify/memory/constitution.md)")
    elif any(m in constitution.read_text(encoding="utf-8") for m in _PLACEHOLDER_MARKERS):
        gaps.append("constituição ainda é PLACEHOLDER — ratifique na Discovery")
    specs = root / "specs"
    if specs.is_dir():
        for feature in sorted(p for p in specs.iterdir() if p.is_dir()):
            missing = [f for f in _DISCOVERY_FILES if not (feature / f).is_file()]
            tasks = feature / "tasks.md"
            if not missing and not _TASK_LINE_RE.search(tasks.read_text(encoding="utf-8")):
                missing.append("tasks.md sem tarefa")
            if missing:
                gaps.append(f"{feature.name}: falta {', '.join(missing)}")
    return gaps


#: Above this many tasks in one feature, advise slicing into sub-phase branches (ATRITO-96).
_SLICE_TASK_THRESHOLD = 12


def oversized_features(
    repo_root: str | Path, *, max_tasks: int = _SLICE_TASK_THRESHOLD
) -> list[tuple[str, int]]:
    """Features whose ``tasks.md`` exceeds ``max_tasks`` — slice candidates (ATRITO-96).

    A Build sub-phase should be a small, reviewable, mergeable slice (one user story / deliverable),
    not the whole phase. Many tasks in one branch = a giant PR + a roadmap that stays stale until
    merge. This surfaces the size as ADVICE (not a block) so the conductor suggests slicing.
    """
    root = Path(repo_root)
    specs = root / "specs"
    out: list[tuple[str, int]] = []
    if specs.is_dir():
        for feature in sorted(p for p in specs.iterdir() if p.is_dir()):
            tasks = feature / "tasks.md"
            if tasks.is_file():
                count = len(_TASK_LINE_RE.findall(tasks.read_text(encoding="utf-8")))
                if count > max_tasks:
                    out.append((feature.name, count))
    return out


# --- Typer CLI: thin verbs the skill invokes (ADR-0017 mechanical-conductor) --------


@app.command("read-state")
def read_state_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print the previous ``Fase atual`` value as JSON for the skill."""
    typer.echo(
        json.dumps({"previous_phase": read_active_phase(repo_root / HANDOVER)}, ensure_ascii=False)
    )


@app.command("mark")
def mark_cmd(
    phase: Annotated[str, typer.Argument(help="One of the six canonical phases.")],
    slug: Annotated[str, typer.Argument(help="Sub-phase slug.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Mark the phase active in HANDOVER and print the templated checklist."""
    resolved = validate_phase(phase)
    state = mark_active(repo_root, resolved, slug)
    payload = {
        "marker": state.marker,
        "previous": state.previous,
        "checklist": phase_checklist(resolved),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("check-discovery")
def check_discovery_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Discovery→Build gate (ATRITO-41): print completeness gaps as JSON. Empty gaps = complete."""
    gaps = check_discovery_completeness(repo_root)
    typer.echo(json.dumps({"complete": not gaps, "gaps": gaps}, ensure_ascii=False, indent=2))


@app.command("subphase-advice")
def subphase_advice_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    max_tasks: Annotated[int, typer.Option(help="Advise slicing above this task count.")] = 12,
) -> None:
    """Advice (ATRITO-96): features big enough to warrant slicing into sub-phase branches (JSON)."""
    big = oversized_features(repo_root, max_tasks=max_tasks)
    payload = {"slice_candidates": [{"feature": n, "tasks": c} for n, c in big]}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("branch")
def branch_cmd(
    n: Annotated[int, typer.Option(help="Sub-phase ordinal N.")],
    slug: Annotated[str, typer.Option(help="Sub-phase slug.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Create ``feat/phase-N-<slug>`` + PR template (skill gated this — FR-004/006)."""
    name = create_phase_branch(repo_root, phase_branch_name(n, slug))
    configure_pr_template(repo_root)
    typer.echo(name)


@app.command("set-briefing")
def set_briefing_cmd(
    unit: Annotated[str, typer.Argument(help="Roadmap unit id (phase/sub-phase) being opened.")],
    briefing: Annotated[
        str, typer.Argument(help="Authored opening briefing (didactic; see tone directive).")
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Author the OPENING briefing of the unit being opened in roadmap.yaml (ADR-0018, Fatia 3b).

    Mirrors the journey-phase-end verb — single source ``journey_core.briefing_ops`` (anti-drift).
    Does NOT regenerate the roadmap: the briefing is persisted and shows on the next generation
    (preserved by the feature-005 ``merge_authored``). Because phase-start runs BEFORE any regen,
    it TOLERATES an absent roadmap.yaml: warns and exits 0 (não fabrica) — the opening briefing is
    applied once the roadmap exists.
    """
    from journey_core.briefing_ops import set_briefing

    roadmap = Path(repo_root) / "roadmap.yaml"
    if not roadmap.is_file():
        typer.echo(
            "roadmap.yaml ainda não existe — briefing de abertura aplicado na próxima geração.",
            err=True,
        )
        return
    typer.echo(str(set_briefing(roadmap, unit, briefing)))


def main() -> None:
    """Console-script entry point (`journey-phase-start`)."""
    app()
