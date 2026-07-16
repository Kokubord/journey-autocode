"""journey-phase-end — deterministic mechanic for closing a phase (feature 007).

ADR-0017 mechanical-conductor sub-pattern (par da 006): a **thin skill**
(`.claude/skills/journey-phase-end/SKILL.md`) conducts the closure, narrates the exit
checklist and gates; this **mechanic** does the deterministic work — read the commits
since phase-start (reusing ``journey_core.parsers.git_state``), build the exit checklist,
assemble the structured PR body.

Render local de roadmap **aposentado** (feature 023 / ATRITO-78 / ADR-0032): antes o fim de
fase disparava o gerador 005 (``journey-roadmap generate``) para produzir ``roadmap.yaml``/``.html``
localmente; agora o roadmap renderizado vive **no Site** e ``trigger_roadmap_regen`` é inerte.
Real host execution (PR open/merge, CI, main protection) is deferred (FR-008 — no Build
phase lived).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer
from journey_core.models.exit_checklist import ExitCheckItem, ExitChecklist
from journey_core.models.phase_state import Phase
from journey_core.models.structured_pr import StructuredPR
from journey_core.parsers.git_state import CommitInfo, read_git_state

app = typer.Typer(help="Deterministic mechanic for /journey-phase-end (feature 007).")

_ADR_TAG = re.compile(r"\[ADR-(\d{1,4})\]")

#: Markers of the Foundation no-op CI placeholder — while present, "CI verde" is hollow (ATRITO-97).
_CI_PLACEHOLDER_MARKERS = ("intentionally a no-op", "Foundation placeholder")


def ci_is_placeholder(repo_root: str | Path) -> bool:
    """Whether ``.github/workflows/ci.yml`` is still the Foundation no-op placeholder (ATRITO-97).

    The template ships a no-op CI (stack unknown at Foundation); once Discovery fixes the stack it
    must be made real. A no-op keeps ``exit-check`` "CI verde" hollow — this detects it so the gate
    warns instead of giving false confidence. Absent CI → ``False`` (not this concern).
    """
    ci = Path(repo_root) / ".github" / "workflows" / "ci.yml"
    if not ci.is_file():
        return False
    text = ci.read_text(encoding="utf-8")
    return any(marker in text for marker in _CI_PLACEHOLDER_MARKERS)


def commits_since(
    repo_root: str | Path, since_sha: str | None = None, max_commits: int = 500
) -> list[CommitInfo]:
    """Commits since the phase-start point (FR-001), reusing :func:`read_git_state`.

    Args:
        repo_root: Repository root.
        since_sha: The phase-start commit; commits up to (excluding) it are returned.
            When ``None``, all read commits are returned.
        max_commits: Upper bound passed to :func:`read_git_state`.
    """
    commits = read_git_state(repo_root, max_commits=max_commits).commits
    if not since_sha:
        return commits
    result: list[CommitInfo] = []
    for commit in commits:  # newest first
        if commit.sha.startswith(since_sha) or since_sha.startswith(commit.sha):
            break
        result.append(commit)
    return result


def material_decisions(commits: list[CommitInfo]) -> list[str]:
    """Summaries of the ``DECISION`` commits in the period (FR-003)."""
    return [c.summary for c in commits if c.summary.startswith("DECISION")]


def adrs_in(commits: list[CommitInfo]) -> list[int]:
    """ADR numbers tagged ``[ADR-NNNN]`` across the period's commits (FR-003)."""
    found: list[int] = []
    for commit in commits:
        for match in _ADR_TAG.finditer(commit.summary):
            number = int(match.group(1))
            if number not in found:
                found.append(number)
    return sorted(found)


def build_structured_pr(phase: Phase, slug: str, commits: list[CommitInfo]) -> StructuredPR:
    """Assemble the structured PR body for the closed phase (FR-003)."""
    return StructuredPR(
        title=f"Phase {phase.label} — {slug}",
        material_decisions=material_decisions(commits),
        adrs=adrs_in(commits),
    )


def build_exit_checklist(
    *,
    tests_ok: bool,
    ci_ok: bool,
    handover_ok: bool,
    build_end: bool = False,
    manuals_ok: bool = False,
) -> ExitChecklist:
    """Build the exit checklist (FR-002); tests/CI are blocking (SC-003)."""
    items = [
        ExitCheckItem(label="Testes a passar", ok=tests_ok, blocking=True),
        ExitCheckItem(label="CI verde", ok=ci_ok, blocking=True),
        ExitCheckItem(label="HANDOVER consolidado", ok=handover_ok, blocking=False),
    ]
    if build_end:
        items.append(
            ExitCheckItem(
                label="Manuais gerados (fim de Build — spec 008)", ok=manuals_ok, blocking=False
            )
        )
    return ExitChecklist(items=items)


def trigger_roadmap_regen(repo_root: str | Path) -> None:
    """Render local de roadmap **APOSENTADO** (feature 023 / ATRITO-78 / ADR-0032).

    O roadmap renderizado passou a viver **no Site** (consolidação+render hospedados; o Site
    lê os dados crus do repo). Antes esta função invocava ``journey-roadmap generate`` para
    produzir ``roadmap.yaml``/``.html`` localmente; agora é **inerte** (não gera nada). Mantida
    (não deletada) para reversibilidade — reativar = restaurar a invocação do gerador.
    """
    return None


# --- Typer CLI: thin verbs the skill invokes (ADR-0017 mechanical-conductor) --------


@app.command("exit-check")
def exit_check_cmd(
    tests_ok: Annotated[bool, typer.Option(help="Tests passing?")] = True,
    ci_ok: Annotated[bool, typer.Option(help="CI green?")] = True,
    handover_ok: Annotated[bool, typer.Option(help="HANDOVER consolidated?")] = True,
    build_end: Annotated[bool, typer.Option(help="End of a Build phase?")] = False,
    manuals_ok: Annotated[bool, typer.Option(help="Manuals generated (build end)?")] = False,
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print the exit checklist; exit non-zero (blocks closure) if a blocking item fails."""
    checklist = build_exit_checklist(
        tests_ok=tests_ok,
        ci_ok=ci_ok,
        handover_ok=handover_ok,
        build_end=build_end,
        manuals_ok=manuals_ok,
    )
    for item in checklist.items:
        typer.echo(f"[{'x' if item.ok else ' '}] {item.label}")
    if ci_ok and ci_is_placeholder(repo_root):
        typer.echo(
            "Aviso: o CI ainda é o placeholder no-op da Foundation — 'CI verde' NÃO valida nada "
            "(não roda os testes). Torne o CI real (rodar os testes do stack) antes de confiar "
            "neste gate; até lá o gate protege a main só com testes locais. (Não bloqueia.)",
            err=True,
        )
    if checklist.blocked:
        typer.echo(f"BLOQUEADO: {', '.join(checklist.blocking_failures)}", err=True)
        raise typer.Exit(code=1)


@app.command("build-pr")
def build_pr_cmd(
    phase: Annotated[str, typer.Argument(help="One of the six canonical phases.")],
    slug: Annotated[str, typer.Argument(help="Sub-phase slug.")],
    since: Annotated[str, typer.Option(help="Phase-start commit sha (boundary).")] = "",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print the structured PR body for the period since ``--since`` (FR-003/005)."""
    commits = commits_since(repo_root, since or None)
    pr = build_structured_pr(Phase(phase.strip().lower()), slug, commits)
    typer.echo(pr.to_markdown())


@app.command("regen-roadmap")
def regen_roadmap_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Render local aposentado (feature 023/ATRITO-78) — o roadmap é renderizado no Site."""
    trigger_roadmap_regen(repo_root)  # inerte (no-op)
    typer.echo(
        "Render local de roadmap aposentado (feature 023 / ATRITO-78 / ADR-0032) — "
        "o roadmap é renderizado no Site, não localmente."
    )


@app.command("set-briefing")
def set_briefing_cmd(
    unit: Annotated[str, typer.Argument(help="Roadmap unit id (phase/sub-phase) to nourish.")],
    briefing: Annotated[
        str, typer.Argument(help="Authored briefing text (didactic; see tone directive).")
    ],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Author the closed unit's briefing in roadmap.yaml (ADR-0018), BEFORE regen-roadmap.

    The briefing TEXT is authored by the conducting skill following the tone directive
    (docs/design/roadmap-render-fase-a.md, secao Tom e qualidade); this verb only persists it,
    reusing the single source ``journey_core.briefing_ops``. The next regen preserves it via the
    feature-005 ``merge_authored``.
    """
    from journey_core.briefing_ops import set_briefing

    typer.echo(str(set_briefing(Path(repo_root) / "roadmap.yaml", unit, briefing)))


@app.command("session-id")
def session_id_cmd() -> None:
    """Print the Claude Code session id for the Closing block ``sessao_id`` (ATRITO-43 fix-real).

    Captures ``CLAUDE_CODE_SESSION_ID`` (ADR-0031). Prints ``unresolved`` EXPLICITLY when the
    variable is absent — never a blank that looks bound. The conducting skill embeds this value
    as ``sessao_id`` in the Closing block so the token pipeline (005 FR-016) can bind the session
    to its phase. The env var must reach this process — see ADR-0031 (WSLENV/passthrough).

    When the id is ``unresolved`` a non-blocking WARNING goes to stderr (the binding will be
    ``unattributed``; how to fix via WSLENV — ATRITO-91). stdout still carries the sentinel, so
    the Closing contract is preserved and the session is never blocked.
    """
    from journey_core.session import UNRESOLVED, capture_session_id

    sid = capture_session_id()
    typer.echo(sid)  # stdout: the value the skill embeds as `sessao_id` (sentinel preserved)
    if sid == UNRESOLVED:
        typer.echo(
            "Aviso: session-id nao resolveu (CLAUDE_CODE_SESSION_ID ausente) — o binding de "
            "tokens desta sessao ficara 'unattributed'. Em Windows+WSL: configure "
            "WSLENV=CLAUDE_CODE_SESSION_ID/u (ADR-0031 / ATRITO-91) e abra nova sessao; "
            "ou grave o id a mao no bloco Closing. (Nao bloqueia.)",
            err=True,
        )


def main() -> None:
    """Console-script entry point (`journey-phase-end`)."""
    app()
