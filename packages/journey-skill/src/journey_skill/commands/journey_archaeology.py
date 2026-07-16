"""Conducting mechanic for /journey-archaeology (feature 003).

Judgment-heavy: the SKILL.md decides which old decisions are material, authors the proposals and
marks uncertainty — **propose, never assert** (ATRITO-32). This mechanic is thin & **local** (no
network): ``read-context`` gathers the audit window (commits + old specs); ``propose-adr`` writes a
PROPOSED ADR draft (``status=Proposto``, next free number — non-destructive FR-006) or prints it
with ``--dry-run`` (FR-005); ``record`` appends to «Histórico da arqueologia» (on human approval,
SC-004). PR comments (FR-001) are optional skill-side enrichment via ``gh``; the mechanic stays
local. Reuses ``journey_core.adr_ops`` and ``parsers.git_state`` — nothing recreated.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from journey_core.adr_ops import next_adr_number, write_adr
from journey_core.exceptions import JourneyError
from journey_core.models.archaeology import RetroProposal
from journey_core.parsers.git_state import commits_since_date
from journey_core.writer import guard_write_target

app = typer.Typer(add_completion=False, help="Arqueologia retrospectiva de decisões (feature 003).")

_ADR_DIR = "docs/adr"
_HANDOVER = "HANDOVER.md"
_ARCH_HEADER = "## Histórico da arqueologia"
_PLACEHOLDER = "- _(vazio)_"
_DEFAULT_DAYS = 30


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(1)


def _since_date(since: str) -> date:
    if since:
        try:
            return date.fromisoformat(since)
        except ValueError:
            _fail(f"--since inválido: {since!r} (use YYYY-MM-DD).")
    return date.today() - timedelta(days=_DEFAULT_DAYS)


@app.command("read-context")
def read_context(
    since: Annotated[str, typer.Option("--since", help="Data ISO (default 30 dias atrás).")] = "",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Emit the audit window (commits + old specs) as JSON for the skill — local, no write."""
    root = Path(repo_root)
    start = _since_date(since)
    try:
        commits = commits_since_date(root, start)
    except JourneyError as exc:
        _fail(str(exc))
    specs_dir = root / "specs"
    specs = sorted(p.name for p in specs_dir.iterdir() if p.is_dir()) if specs_dir.is_dir() else []
    payload = {
        "since": start.isoformat(),
        "commit_count": len(commits),
        "commits": [{"sha": c.sha[:7], "summary": c.summary} for c in commits],
        "specs": specs,
        "note": "PR comments via gh = enriquecimento opcional do skill (local-only aqui).",
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("propose-adr")
def propose_adr(
    payload: Annotated[Path, typer.Option(help="JSON com a RetroProposal autorada pelo skill.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Mostra sem escrever (FR-005).")
    ] = False,
) -> None:
    """Propose a retroactive ADR draft (status=Proposto, next free number). ``--dry-run`` prints."""
    try:
        proposal = RetroProposal.model_validate_json(payload.read_text(encoding="utf-8"))
    except ValueError as exc:  # includes the non-empty-sources guard (FR-007)
        _fail(f"proposta inválida: {exc}")
    adr = proposal.adr
    adr.number = next_adr_number(Path(repo_root) / _ADR_DIR)  # non-destructive (FR-006)
    flag = " [INCERTO — confirmar]" if proposal.uncertain else ""
    if dry_run:
        typer.echo(f"# PROPOSTA (dry-run — nada escrito) ADR-{adr.number:04d}{flag}")
        typer.echo(f"fontes: {', '.join(proposal.sources)}\n")
        typer.echo(adr.to_markdown())
        return
    path = write_adr(Path(repo_root) / _ADR_DIR, adr)
    typer.echo(f"proposto (status=Proposto){flag}: {path}")
    typer.echo(f"fontes: {', '.join(proposal.sources)}")


@app.command("record")
def record(
    scope: Annotated[str, typer.Option(help="Escopo da auditoria.")],
    author: Annotated[str, typer.Option(help="Autor.")],
    sources: Annotated[str, typer.Option(help="Fontes (texto).")] = "",
    when: Annotated[str, typer.Option("--date", help="Data ISO.")] = "",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Append a «Histórico da arqueologia» record (data+escopo+autor), on approval (SC-004)."""
    when = when or date.today().isoformat()
    target = guard_write_target(Path(repo_root) / _HANDOVER)
    text = target.read_text(encoding="utf-8")
    if _ARCH_HEADER not in text:
        _fail("HANDOVER sem secção «Histórico da arqueologia».")
    src = f" (fontes: {sources})" if sources else ""
    entry = f"- {when} — {scope} — {author}{src}"
    if _PLACEHOLDER in text:
        new = text.replace(_PLACEHOLDER, entry, 1)
    else:
        start = text.index(_ARCH_HEADER)
        nxt = text.find("\n## ", start + len(_ARCH_HEADER))
        at = nxt if nxt != -1 else len(text)
        new = text[:at].rstrip("\n") + "\n" + entry + "\n" + text[at:]
    target.write_text(new, encoding="utf-8")
    typer.echo(f"registado: {entry}")


def main() -> None:
    """Entry point for the ``journey-archaeology`` console script."""
    app()
