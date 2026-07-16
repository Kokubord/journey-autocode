"""Canonical ADR write schema (ADR-0017 Decision 2 — born in feature 004).

Minimal WRITE schema for an ADR, derived from the on-disk pattern of ADRs 0001-0016:
a Campo/Valor table (Status/Data/Autor), the six canonical sections (Contexto,
Decisão + "Restrições deliberadas (não fazer)", Consequências, Alternativas
consideradas, Referências), and supersede-by-reference (ADR-0009 pattern).

Scope boundary (ADR-0017 Decision 2; anti-drift, eco do ATRITO-61): this module is
*schema + serialization only*. The automation of ``/journey-decision`` — heuristic
pre-fill, duplicate detection, commit assembly (spec 012 FR-007) — is NOT here.
Feature 012 reuses this schema; it does not recreate it.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class AdrStatus(StrEnum):
    """ADR lifecycle status (on-disk pattern; ``Aceito`` is the lived default)."""

    PROPOSTO = "Proposto"
    ACEITO = "Aceito"
    SUPERSEDED = "Superseded"


class Adr(BaseModel):
    """An Architecture Decision Record in the canonical on-disk shape.

    The model holds the fields and serializes them to the canonical Markdown; it does
    not generate content, detect duplicates, or assemble commits — those belong to
    spec 012 (ADR-0017 Decision 2).
    """

    number: int
    slug: str
    title: str
    status: AdrStatus = AdrStatus.ACEITO
    date: str
    author: str
    contexto: str
    decisao: str
    nao_fazer: str | None = None
    consequencias: str
    alternativas: str
    referencias: str
    supersedes: list[int] = []

    @property
    def filename(self) -> str:
        """Canonical file name ``NNNN-slug.md`` (zero-padded number)."""
        return f"{self.number:04d}-{self.slug}.md"

    def to_markdown(self) -> str:
        """Serialize the ADR to the canonical Markdown layout (ADRs 0001-0016)."""
        lines = [
            f"# ADR-{self.number:04d} — {self.title}",
            "",
            "| Campo  | Valor |",
            "|--------|-------|",
            f"| Status | {self.status.value} |",
            f"| Data   | {self.date} |",
            f"| Autor  | {self.author} |",
            "",
        ]
        if self.supersedes:
            refs = ", ".join(f"ADR-{n:04d}" for n in self.supersedes)
            lines += [f"> **Supersede (por referência — ADR-0009):** {refs}.", ""]
        lines += ["## Contexto", "", self.contexto, "", "## Decisão", "", self.decisao, ""]
        if self.nao_fazer:
            lines += ["### Restrições deliberadas (não fazer)", "", self.nao_fazer, ""]
        lines += [
            "## Consequências",
            "",
            self.consequencias,
            "",
            "## Alternativas consideradas",
            "",
            self.alternativas,
            "",
            "## Referências",
            "",
            self.referencias,
            "",
        ]
        return "\n".join(lines)
