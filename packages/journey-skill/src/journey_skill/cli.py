"""journey-skill CLI — exposes the journey-init command."""

from __future__ import annotations

import typer

from journey_skill.commands.journey_init import init


def main() -> None:
    """Console-script entry point (`journey-init`)."""
    typer.run(init)
