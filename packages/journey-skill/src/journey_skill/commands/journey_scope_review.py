"""Conducting mechanic for /journey-scope-review — the Scope Guard (feature 014, ATRITO-34).

``journey-skill`` reuses ``journey-core`` (``parse_vision``/``parse_adr_index``) and does NOT
redefine the roadmap (updated via spec 005). The **rite is conducted by the SKILL.md** (judgment +
IDE Plan mode as motor — FR-006); this mechanic only **gathers the read context**. The scope
decision is recorded as a regular ADR (reuse ``adr_ops``). **FR-007** (auto-drift detector, exact
scope-ADR format, exact reentrant step-by-step) is **deferred — H2**; not built here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from journey_core.models.scope import RITE_STAGES
from journey_core.parsers import parse_adr_index, parse_vision

from journey_skill.commands.journey_discover import VISION_TARGET

app = typer.Typer(add_completion=False, help="Scope Guard — re-entrada Visão/Discovery (014).")


@app.callback(invoke_without_command=True)
def read_context(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Emit the read context for the reentrant rite as JSON (FR-003) — never decides scope.

    Gathers the firm inputs the conducting skill needs (pre-existing Vision, ADR index, roadmap
    presence, the 4 firm rite stages). The escala judgment and the rite itself are the skill's
    (Plan mode as motor). Reads only — no fabrication.
    """
    root = Path(repo_root)
    vision = parse_vision(root / VISION_TARGET)
    adrs = parse_adr_index(root / "docs" / "adr")
    payload = {
        "vision_present": vision.exists,
        "vision_path": vision.path,
        "adr_count": len(adrs),
        "latest_adr": adrs[-1].number if adrs else None,
        "roadmap_present": (root / "roadmap.yaml").is_file(),
        "rite_stages": list(RITE_STAGES),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    """Entry point for the ``journey-scope-review`` console script."""
    app()
