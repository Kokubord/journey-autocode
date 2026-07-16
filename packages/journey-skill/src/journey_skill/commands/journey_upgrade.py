"""Conducting mechanic for /journey-upgrade (feature 002).

Deterministic + strong gates (like 001/init). **NON-DESTRUCTIVE is the spine:** it reuses 001's
``materialize_artifacts`` (writes only what's missing; never overwrites; CLAUDE.md merged via the
managed block — ATRITO-16) — nothing reimplemented. ``preview`` shows the delta without writing;
``apply`` materializes the Basic→Standard delta + writes the upgrade ADR (reuse ``adr_ops``) for
the human to commit. Enterprise is **GUARD-ONLY** (exact delta = open-core, deferred ATRITO-50);
downgrade is a **CIRCUIT-BREAKER** (policy deferred — FR-016); the methodology-version dimension
(ATRITO-15) is not built. Ambiguous tier → escalate, never guess.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from journey_core.adr_ops import next_adr_number, write_adr
from journey_core.models.adr import Adr, AdrStatus
from journey_core.models.project_state import Tier
from journey_core.models.upgrade import TierDelta

from journey_skill.commands.journey_init import (
    ARTIFACTS,
    default_templates_dir,
    materialize_artifacts,
    materialize_conductors,
)

app = typer.Typer(add_completion=False, help="Migração de tier (feature 002).")

_TIER_RANK = {Tier.BASIC: 0, Tier.STANDARD: 1, Tier.ENTERPRISE: 2}
_ADR_DIR = "docs/adr"


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(1)


def detect_tier(target: Path) -> Tier | None:
    """Infer the current tier from artifacts (FR-001). Ambiguous → ``None`` (escalate, never guess).

    Standard = both ``.specify/`` and ``specs/`` present; Basic = neither; only one → ambiguous.
    """
    spec_kit = (target / ".specify").is_dir()
    specs = (target / "specs").is_dir()
    if spec_kit and specs:
        return Tier.STANDARD
    if not spec_kit and not specs:
        return Tier.BASIC
    return None


def compute_delta(target: Path, from_tier: Tier, to_tier: Tier) -> TierDelta:
    """What's MISSING for the target tier (FR-002): absent canonical artifacts (+ ``specs/``)."""
    missing = [dest for _, dest in ARTIFACTS if not (target / dest).exists()]
    if not (target / "specs").is_dir():
        missing.append("specs/")
    return TierDelta(from_tier=from_tier, to_tier=to_tier, missing=missing)


def _resolve(target: Path, to: str) -> tuple[Tier, Tier]:
    """Validate the transition (ambiguous/downgrade/enterprise) before any work."""
    try:
        to_tier = Tier(to)
    except ValueError:
        _fail(f"--to inválido: {to!r} (basic/standard/enterprise).")
    current = detect_tier(target)
    if current is None:
        _fail("tier vigente AMBÍGUO (só um de .specify//specs/ presente) — confirme; não adivinho.")
    if _TIER_RANK[to_tier] < _TIER_RANK[current]:
        _fail(
            f"DOWNGRADE {current.value}→{to_tier.value} não suportado (FR-016, política "
            "não-cravada) — chame o owner (disjuntor ATRITO-54)."
        )
    if to_tier is Tier.ENTERPRISE:
        _fail(
            "--to=enterprise: o delta exato é a fronteira open-core (ATRITO-50, decisão de fim). "
            "Guard-only: nada comercial é materializado; componentes Enterprise = externos."
        )
    return current, to_tier


@app.command("preview")
def preview(
    to: Annotated[str, typer.Option("--to", help="basic/standard/enterprise.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Show the delta (what's missing) — NO write (FR-001/002, for the human gate, ADR-0005)."""
    root = Path(repo_root)
    current, to_tier = _resolve(root, to)
    delta = compute_delta(root, current, to_tier)
    if not delta.missing:
        typer.echo(f"# {current.value}→{to_tier.value}: nada a fazer (idempotente — já no alvo).")
        return
    typer.echo(f"# delta {current.value}→{to_tier.value} — escreveria só o que falta (aditivo):")
    for dest in delta.missing:
        typer.echo(f"- {dest}")


@app.command("apply")
def apply(
    to: Annotated[str, typer.Option("--to", help="basic/standard/enterprise.")],
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Materialize the delta + write the upgrade ADR (non-destructive; post gate, ADR-0005)."""
    root = Path(repo_root)
    current, to_tier = _resolve(root, to)
    specs_created = not (root / "specs").is_dir()
    context = {"project_name": root.resolve().name, "date": date.today().isoformat()}
    result = materialize_artifacts(default_templates_dir(), root, context)
    conductors = materialize_conductors(default_templates_dir(), root)
    (root / "specs").mkdir(exist_ok=True)
    created = list(result.get("created", []))
    if specs_created:
        created.append("specs/")
    if conductors["copied"]:
        typer.echo(f"condutores: {len(conductors['copied'])} skill(s) journey-* propagada(s)")
    if not created:
        typer.echo(f"# {current.value}→{to_tier.value}: idempotente — nada faltava, nada escrito.")
        return
    adr = Adr(
        number=next_adr_number(root / _ADR_DIR),
        slug=f"upgrade-{current.value}-{to_tier.value}",
        title=f"Upgrade de tier {current.value}→{to_tier.value}",
        status=AdrStatus.ACEITO,
        date=date.today().isoformat(),
        author="journey",
        contexto=f"Upgrade de tier {current.value}→{to_tier.value}: delta aditivo materializado; "
        "artefatos pré-existentes preservados (não-destrutivo).",
        decisao=f"Adotar o tier {to_tier.value}; instalado apenas o que faltava (delta).",
        consequencias="Capacidades do tier alvo disponíveis; nada pré-existente foi tocado.",
        alternativas="Manter o tier atual (rejeitado — o operador pediu o upgrade).",
        referencias="Vision §3.1.1/§3.2; FR-001-009; reuso do instalador da 001.",
    )
    adr_path = write_adr(root / _ADR_DIR, adr)
    typer.echo(f"criados: {', '.join(created)}")
    typer.echo(f"ADR de upgrade: {adr_path}")
    typer.echo(
        f"commit sugerido: DECISION(meta): upgrade to {to_tier.value} [ADR-{adr.number:04d}]"
    )


def main() -> None:
    """Entry point for the ``journey-upgrade`` console script."""
    app()
