"""Bundle the installables (templates + journey-* conductor skills) into the package.

Copies ``templates/`` and the ``journey-*`` skills into ``src/journey_skill/_bundled`` before the
build so the wheel AND the sdist are self-contained — a globally installed journey-init/upgrade
finds them without a base clone (feature 024 / ATRITO-94). A ``../../`` force-include broke
``uv build`` (the sdist cannot reference paths outside the project root, and uv builds the wheel
from the sdist); copying into the tree survives both. When building from an sdist the source dirs
are absent — the bundle is already vendored, so skip.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Vendor templates + journey-* skills into the package before each build."""

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Copy templates/ + journey-* skills into src/journey_skill/_bundled (024/ATRITO-94)."""
        root = Path(self.root)
        repo = root.parent.parent
        dest = root / "src" / "journey_skill" / "_bundled"
        templates = repo / "templates"
        if templates.is_dir():
            _replace(templates, dest / "templates")
        skills = repo / ".claude" / "skills"
        if skills.is_dir():
            target = dest / "skills"
            if target.exists():
                shutil.rmtree(target)
            for child in sorted(skills.iterdir()):
                if child.is_dir() and child.name.startswith("journey-"):
                    shutil.copytree(child, target / child.name)


def _replace(src: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target)
