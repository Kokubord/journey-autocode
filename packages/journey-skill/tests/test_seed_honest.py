"""ATRITO-72 fix — the new-project seed is HONEST (no fabricated done phases)."""

from typing import Any

import yaml
from journey_skill.commands.journey_init import default_templates_dir, render


def test_seed_has_no_fabricated_done_phases() -> None:
    raw = (default_templates_dir() / "roadmap.seed.yaml.jinja").read_text(encoding="utf-8")
    data: dict[str, Any] = yaml.safe_load(
        render(raw, {"project_name": "demo", "date": "2026-01-01"})
    )
    phases: list[dict[str, Any]] = data["phases"]
    statuses: list[str] = [str(ph["status"]) for ph in phases]
    for ph in phases:
        subs: list[dict[str, Any]] = ph.get("subphases") or []
        statuses += [str(sp["status"]) for sp in subs]
    # A brand-new project never did any product phase → nothing "done*" (ATRITO-32/72).
    assert not any(s.startswith("done") for s in statuses), statuses
    # Warmup is the honest starting point.
    assert phases[0]["id"] == "warmup"
    assert phases[0]["status"] == "next"


def test_seed_handover_readme_have_no_foundation_done_narrative() -> None:
    tdir = default_templates_dir()
    for name in ("handover.md.jinja", "readme.md.jinja"):
        text = (tdir / name).read_text(encoding="utf-8")
        assert "Foundation concluída" not in text, name
