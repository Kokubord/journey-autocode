"""journey-discover — deterministic mechanic for the Discovery workshop (feature 004).

Per ADR-0017 Decision 1, the *conversation* (workshop, hypothesis validation, gap
spotting, draft authoring, the "registrar como decisão material?" gate) is conducted by
the in-session skill ``.claude/skills/journey-discover/SKILL.md`` — a distinct system
prompt in the same chat session, not a persona (Vision §4.5.1). This module is the
deterministic mechanic that skill invokes: read context, consolidate the vision, write
ADRs (via journey-core ``models.adr``), and scaffold spec drafts.

All writes are routed through the repository runtime and UNC paths are vetoed
(ADR-0004, FR-010). The narrow-scope boundary (FR-012) is honoured: this mechanic never
runs ``speckit-*`` nor ``journey-roadmap`` — it only prepares artifacts that are handed
off to those commands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from journey_core import adr_ops
from journey_core.models.adr import Adr
from journey_core.models.spec_draft import SpecDraft
from journey_core.models.vision import Vision
from journey_core.parsers import parse_adr_index, parse_handover, parse_vision
from journey_core.writer import guard_write_target

app = typer.Typer(help="Deterministic mechanic for /journey-discover (feature 004).")

VISION_TARGET = "docs/JOURNEY-VISION.md"  # firm target (ADR-0017 Decision 3, Vision §10.2)
ADR_DIR = "docs/adr"


def next_adr_number(repo_root: str | Path) -> int:
    """Return the next free ADR number (delegates to shared adr_ops — single source)."""
    return adr_ops.next_adr_number(Path(repo_root) / ADR_DIR)


def read_context(repo_root: str | Path) -> dict[str, object]:
    """Read HANDOVER, ADR index, and any pre-existing vision (FR-005/011).

    The skill consumes this to consolidate without blind overwrite and to pick the
    next ADR number. Reading is allowed from any environment (ADR-0004).
    """
    root = Path(repo_root)
    handover = parse_handover(root / "HANDOVER.md")
    adrs = parse_adr_index(root / ADR_DIR)
    vision = parse_vision(root / VISION_TARGET)
    return {
        "handover": handover.model_dump(),
        "adrs": [ref.model_dump(mode="json") for ref in adrs],
        "next_adr_number": (adrs[-1].number + 1) if adrs else 1,
        "preexisting_vision": vision.model_dump(),
    }


def consolidate_vision(repo_root: str | Path, vision: Vision) -> Path:
    """Write the consolidated vision to its firm target (FR-005, ADR-0017 Decision 3).

    The caller (skill) must have read the pre-existing vision via :func:`read_context`
    and folded it into ``vision.content`` — consolidation is not a blind overwrite
    (FR-011).
    """
    target = guard_write_target(Path(repo_root) / vision.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(vision.content, encoding="utf-8")
    return target


def write_adr(repo_root: str | Path, adr: Adr) -> Path:
    """Write an ADR file from the canonical schema (FR-004; delegates to shared adr_ops).

    Only called after the human approves the "registrar como decisão material?" gate
    (FR-003) — the gate itself is conducted by the skill, never bypassed here.
    """
    return adr_ops.write_adr(Path(repo_root) / ADR_DIR, adr)


def scaffold_spec_draft(repo_root: str | Path, draft: SpecDraft) -> Path:
    """Write a spec draft handed to /speckit-specify (FR-006, verbete-estreito)."""
    target = guard_write_target(Path(repo_root) / draft.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(draft.content, encoding="utf-8")
    return target


# --- Typer CLI: thin wrappers the skill invokes (ADR-0017 Decision 1) -------


@app.command("read-context")
def read_context_cmd(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Print HANDOVER/ADRs/pre-existing-vision context as JSON for the skill."""
    typer.echo(json.dumps(read_context(repo_root), ensure_ascii=False, indent=2))


@app.command("consolidate-vision")
def consolidate_vision_cmd(
    payload: Annotated[Path, typer.Option(help="JSON file with the Vision fields.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Write the consolidated vision from a JSON payload authored by the skill."""
    vision = Vision.model_validate_json(payload.read_text(encoding="utf-8"))
    typer.echo(str(consolidate_vision(repo_root, vision)))


@app.command("write-adr")
def write_adr_cmd(
    payload: Annotated[Path, typer.Option(help="JSON file with the Adr fields.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Write an ADR from a JSON payload authored by the skill (post-gate)."""
    adr = Adr.model_validate_json(payload.read_text(encoding="utf-8"))
    typer.echo(str(write_adr(repo_root, adr)))


@app.command("scaffold-draft")
def scaffold_draft_cmd(
    payload: Annotated[Path, typer.Option(help="JSON file with the SpecDraft fields.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Write a spec draft from a JSON payload authored by the skill."""
    draft = SpecDraft.model_validate_json(payload.read_text(encoding="utf-8"))
    typer.echo(str(scaffold_spec_draft(repo_root, draft)))


def main() -> None:
    """Console-script entry point (`journey-discover`)."""
    app()
