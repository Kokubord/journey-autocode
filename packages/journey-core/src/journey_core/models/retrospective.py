"""Models for /journey-retrospective (feature 013): the structured retrospective document.

The document has the **four canonical sections** (FR-003): what worked, what did not, lessons,
learning-ADRs. Each observation is a :class: anchored in a **citable source** — the same
anti-fabrication spine as feature 003 (propose-never-assert, ATRITO-32): an item without a source
is invalid by construction, and the operational-metrics slot (FR-006) stays "pendente" (the
token pipeline IS built — #123 — but 013 does not wire it yet; deferred), never a fabricated number.

The learning-ADR *materialization* reuses :class:
(and adr_ops) — not recreated here. This module is the document schema + serialization only.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator

#: FR-006 — operational metrics need /journey-report (011) + the token pipeline (#123) — both
#: BUILT — wired into 013, which is DEFERRED. The slot is honest, never fabricated (ATRITO-32).
METRICS_PENDING = (
    "pendente — o /journey-report (011) e o pipeline de tokens (#123) existem; "
    "a retrospetiva (013) ainda não os fia (deferido, FR-006). Nunca fabricado."
)

_SECTIONS = (
    ("funcionou", "O que funcionou"),
    ("nao_funcionou", "O que não funcionou"),
    ("licoes", "Lições aprendidas"),
    ("adrs_aprendizado", "ADRs de aprendizado (sugeridos)"),
)
_EMPTY = "_(sem registos nesta secção — não fabricado)_"


class RetroItem(BaseModel):
    """A single retrospective observation, anchored in a citable source (anti-fabrication).

    source records the origin (a Closing block, an ADR, an atrito, a commit sha) and MUST be
    non-empty — a lesson recomposed from memory rather than from a versioned input is invalid by
    construction (anchored-in-source, FR-002/SC-002, ATRITO-32).
    """

    text: str
    source: str

    @field_validator("source")
    @classmethod
    def _source_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError(
                "RetroItem requires a citable source (anchored-in-source, FR-002/ATRITO-32)"
            )
        return value


class Retrospective(BaseModel):
    """The structured retrospective document (FR-003): four sections, written from real inputs.

    The four section lists carry :class: observations the workshop distilled from the
    versioned inputs. The operational-metrics slot is rendered as METRICS_PENDING (FR-006), not
    a number. number is assigned by the write op (sequential, first = 001) — not stored here.
    """

    slug: str
    scope: str
    date: str
    funcionou: list[RetroItem] = []
    nao_funcionou: list[RetroItem] = []
    licoes: list[RetroItem] = []
    adrs_aprendizado: list[RetroItem] = []

    def filename(self, number: int) -> str:
        """Canonical file name NNN-slug.md (3-digit sequential, first = 001)."""
        return f"{number:03d}-{self.slug}.md"

    def to_markdown(self, number: int) -> str:
        """Serialize to the canonical layout: four sections + honest metrics slot (FR-003)."""
        lines = [
            f"# Retrospectiva {number:03d} — {self.scope}",
            "",
            "| Campo | Valor |",
            "| --- | --- |",
            f"| Data | {self.date} |",
            f"| Escopo | {self.scope} |",
            "",
            "> Retrospectiva estruturada (Journey §10.4). Lições ancoradas em fonte; "
            "o indisponível fica «pendente», nunca fabricado (ATRITO-32).",
            "",
        ]
        for attr, title in _SECTIONS:
            items: list[RetroItem] = getattr(self, attr)
            lines.append(f"## {title}")
            lines.append("")
            if not items:
                lines.append(_EMPTY)
            else:
                lines.extend(f"- {it.text} — _fonte: {it.source}_" for it in items)
            lines.append("")
        lines.append("## Métricas operacionais")
        lines.append("")
        lines.append(METRICS_PENDING)
        lines.append("")
        return "\n".join(lines)
