"""Canonical project manual model (feature 008, Vision §10.3).

Four canonical manuals of the TARGET project (not Journey): user / admin / troubleshooting /
technical. **Filenames are English** (FR-006, Constituição §8.4); **content is authored by the
conducting skill** (judgment) — this model only carries it. The "comportamentos protegidos por
testes-sentinela" section lives inside ``content`` and is empty/warned when no Sentinel Tests
exist (anti-fabricação; the Regression Guard is *referenced, not defined* here).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ManualType(StrEnum):
    """The 4 canonical manual types (Vision §10.3)."""

    USER = "user"
    ADMIN = "admin"
    TROUBLESHOOTING = "troubleshooting"
    TECHNICAL = "technical"


CANONICAL_MANUALS: tuple[ManualType, ...] = tuple(ManualType)

DEFAULT_LANGUAGE = "pt-BR"  # content default (Constituição §8.5); offered with a choice (FR-005)
SUPPORTED_LANGUAGES: tuple[str, ...] = ("pt-BR", "en-US")


class Manual(BaseModel):
    """One canonical manual of the target project (content authored by the skill)."""

    type: ManualType
    content: str
    language: str = DEFAULT_LANGUAGE
    adr_refs: list[int] = []

    @property
    def filename(self) -> str:
        """English filename, independent of content language (FR-006)."""
        return f"{self.type.value}.md"

    @property
    def path(self) -> str:
        """Flat ``docs/manuals/`` location (Vision §10.3)."""
        return f"docs/manuals/{self.filename}"
