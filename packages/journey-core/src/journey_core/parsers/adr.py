"""Parser for the docs/adr/ index used in state detection."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

_ADR_FILE = re.compile(r"^(?P<num>\d{4})-(?P<slug>.+)\.md$")


class AdrRef(BaseModel):
    """A reference to an ADR file discovered on disk."""

    number: int
    slug: str
    path: Path


def parse_adr_index(adr_dir: str | Path) -> list[AdrRef]:
    """Scan a docs/adr/ directory and return the ADRs found, ordered by number.

    Args:
        adr_dir: Path to the ADR directory.

    Returns:
        ADRs sorted by their numeric prefix; empty when the directory is absent.
    """
    directory = Path(adr_dir)
    if not directory.is_dir():
        return []
    refs: list[AdrRef] = []
    for child in directory.iterdir():
        match = _ADR_FILE.match(child.name)
        if match is not None:
            refs.append(
                AdrRef(number=int(match.group("num")), slug=match.group("slug"), path=child)
            )
    return sorted(refs, key=lambda ref: ref.number)
