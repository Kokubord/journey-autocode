"""Light source digest for /journey-manuals-generate (feature 008, FR-003).

A **LIGHT inventory** of the repository sources (ADRs, specs, modules, tests, current phase)
that the conducting skill reads to **synthesize** the manuals — the deep synthesis is the
skill's judgment, NOT this code. Sentinel Tests are *referenced, not defined* (the Regression
Guard is a transversal Vision concept without a spec): a test counts as sentinel only if
explicitly tagged (``sentinel`` in its filename); none tagged → empty list → the skill's
"comportamentos protegidos" section is empty/warned (anti-fabricação).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from journey_core.parsers.adr import parse_adr_index
from journey_core.parsers.handover import parse_handover


class SourceRef(BaseModel):
    """A light reference to a source artifact (id + human title)."""

    id: str
    title: str


class SourceDigest(BaseModel):
    """A light inventory of the repository sources the skill synthesizes the manuals from."""

    project: str
    current_phase: str | None = None
    adrs: list[SourceRef] = []
    specs: list[SourceRef] = []
    modules: list[str] = []
    tests: list[str] = []
    sentinel_tests: list[str] = []


def _spec_title(spec_md: Path) -> str:
    for line in spec_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].removeprefix("Feature Specification:").strip()
    return spec_md.parent.name


def source_digest(repo_root: str | Path) -> SourceDigest:
    """Build a LIGHT digest of repository sources (FR-003) for the skill to synthesize from."""
    root = Path(repo_root)
    adrs = [
        SourceRef(id=f"ADR-{ref.number:04d}", title=ref.slug.replace("-", " "))
        for ref in parse_adr_index(root / "docs" / "adr")
    ]
    specs: list[SourceRef] = []
    specs_dir = root / "specs"
    if specs_dir.is_dir():
        for child in sorted(specs_dir.iterdir()):
            spec_md = child / "spec.md"
            if child.is_dir() and spec_md.is_file():
                specs.append(SourceRef(id=child.name, title=_spec_title(spec_md)))
    modules = sorted(
        str(p.relative_to(root))
        for p in root.glob("packages/*/src/**/*.py")
        if p.name != "__init__.py"
    )
    tests = sorted(str(p.relative_to(root)) for p in root.glob("packages/*/tests/test_*.py"))
    sentinel_tests = [t for t in tests if "sentinel" in Path(t).name.lower()]
    return SourceDigest(
        project=root.resolve().name,
        current_phase=parse_handover(root / "HANDOVER.md").current_phase,
        adrs=adrs,
        specs=specs,
        modules=modules,
        tests=tests,
        sentinel_tests=sentinel_tests,
    )
