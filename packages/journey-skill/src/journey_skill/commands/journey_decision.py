"""journey-decision — deterministic mechanic for registering a material decision (012).

Per ADR-0017 (mechanical-conductor sub-pattern, como a 006): a **thin skill**
(`.claude/skills/journey-decision/SKILL.md`) conducts the *"registrar como decisão
material?"* gate (ADR-0005) and authors the ADR content; this **mechanic** does the
deterministic work — next free number, render the canonical ADR **reusing**
`journey_core.models.adr.Adr` (born in 004 — NOT recreated; anti-drift ATRITO-61),
supersede-by-reference (model field), append the «Decisões frescas» entry, and propose the
`DECISION` commit message.

Deferred (spec 012 FR-007, NÃO-VIVIDO): the automation as exercised end-to-end (heuristic
duplicate detection, interactive commit assembly) — the command was never run. **Not built
here**; only the firm canonical-output pattern is implemented.

Writes are routed through the repository runtime; UNC paths are vetoed (ADR-0004).
"""

from __future__ import annotations

import json
import re
from datetime import date as date_cls
from pathlib import Path
from typing import Annotated

import typer
from journey_core.adr_ops import next_adr_number, write_adr
from journey_core.exceptions import JourneyError
from journey_core.models.adr import Adr
from journey_core.parsers import parse_adr_index, parse_handover
from journey_core.writer import guard_write_target

app = typer.Typer(help="Deterministic mechanic for /journey-decision (feature 012).")

HANDOVER = "HANDOVER.md"
ADR_DIR = "docs/adr"
_DF_HEADER = re.compile(r"^## Decisões frescas.*$", re.MULTILINE)


def read_context(repo_root: str | Path) -> dict[str, object]:
    """Read HANDOVER phase + ADR index → next free number, avoiding duplicates (FR-001)."""
    root = Path(repo_root)
    handover = parse_handover(root / HANDOVER)
    adrs = parse_adr_index(root / ADR_DIR)
    return {
        "current_phase": handover.current_phase,
        "next_adr_number": next_adr_number(root / ADR_DIR),
        "adr_count": len(adrs),
    }


def write_decision_adr(repo_root: str | Path, adr: Adr) -> Path:
    """Write the pre-filled ADR draft in the canonical pattern (FR-002), open for the human.

    Reuses the shared ADR ops; supersede-by-reference is carried by ``adr.supersedes`` and
    rendered by the schema's ``to_markdown`` — the superseded ADR is never edited (FR-005).
    """
    return write_adr(Path(repo_root) / ADR_DIR, adr)


def decision_commit_message(scope: str, summary: str, number: int) -> str:
    """Suggested commit (inglês, sem trailer — ATRITO-31): ``DECISION(scope): … [ADR-NNNN]``."""
    return f"DECISION({scope}): {summary} [ADR-{number:04d}]"


def decisao_fresca_entry(when: str, summary: str, number: int) -> str:
    """Build the «Decisões frescas» bullet (FR-003)."""
    return f"- {when} — {summary} — [ADR-{number:04d}]"


def append_decisao_fresca(repo_root: str | Path, entry: str) -> Path:
    """Insert ``entry`` as the first bullet of «Decisões frescas», preserving the rest (FR-003).

    Raises:
        JourneyError: If HANDOVER.md or the «Decisões frescas» section is absent.
    """
    path = guard_write_target(Path(repo_root) / HANDOVER)
    if not path.is_file():
        raise JourneyError(f"HANDOVER not found at {path!r}")
    text = path.read_text(encoding="utf-8")
    header = _DF_HEADER.search(text)
    if header is None:
        raise JourneyError("HANDOVER has no '## Decisões frescas' section")
    tail = text[header.end() :]
    bullet = re.search(r"^- ", tail, re.MULTILINE)
    # Insert before the first existing bullet, or right after the header block if none.
    offset = header.end() + (bullet.start() if bullet else len(tail) - len(tail.lstrip("\n")))
    new = text[:offset] + entry.rstrip() + "\n" + text[offset:]
    path.write_text(new, encoding="utf-8")
    return path


# --- Typer CLI: thin verbs the skill invokes (ADR-0017 mechanical-conductor) --------


@app.command("read-context")
def read_context_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print phase + next ADR number as JSON for the skill."""
    typer.echo(json.dumps(read_context(repo_root), ensure_ascii=False, indent=2))


@app.command("write-adr")
def write_adr_cmd(
    payload: Annotated[Path, typer.Option(help="JSON file with the Adr fields (post-gate).")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Write the ADR draft from a JSON payload authored by the skill; print its path."""
    adr = Adr.model_validate_json(payload.read_text(encoding="utf-8"))
    typer.echo(str(write_decision_adr(repo_root, adr)))


@app.command("register")
def register_cmd(
    summary_pt: Annotated[
        str,
        typer.Option("--summary-pt", help="Decision summary in PT (HANDOVER entry — ADR-0001)."),
    ],
    summary_en: Annotated[
        str,
        typer.Option("--summary-en", help="Decision summary in EN (commit message — ADR-0001)."),
    ],
    number: Annotated[int, typer.Option(help="ADR number.")],
    scope: Annotated[str, typer.Option(help="Commit scope.")] = "meta",
    when: Annotated[str, typer.Option("--date", help="ISO date.")] = "",
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Append the «Decisões frescas» entry (PT) and print the DECISION commit message (EN).

    The two summaries are **deliberately separate** (ADR-0001): docs/decisions are PT, commit
    messages are EN — a single string for both would violate the language split.
    """
    when = when or date_cls.today().isoformat()
    append_decisao_fresca(repo_root, decisao_fresca_entry(when, summary_pt, number))
    typer.echo(decision_commit_message(scope, summary_en, number))


def main() -> None:
    """Console-script entry point (`journey-decision`)."""
    app()
