from journey_core.models import Adr, AdrStatus


def _base_adr(**kw: object) -> Adr:
    fields: dict[str, object] = dict(
        number=17,
        slug="padrao-comandos-condutores",
        title="Padrão de comandos condutores",
        date="2026-06-17",
        author="rkokubo",
        contexto="Contexto.",
        decisao="Decisão.",
        consequencias="Consequências.",
        alternativas="Alternativas.",
        referencias="Referências.",
    )
    fields.update(kw)
    return Adr(**fields)  # type: ignore[arg-type]


def test_default_status_is_aceito() -> None:
    assert _base_adr().status is AdrStatus.ACEITO


def test_filename_is_zero_padded() -> None:
    assert _base_adr().filename == "0017-padrao-comandos-condutores.md"


def test_to_markdown_has_canonical_sections() -> None:
    md = _base_adr().to_markdown()
    assert md.startswith("# ADR-0017 — Padrão de comandos condutores")
    for marker in (
        "| Status | Aceito |",
        "| Data   | 2026-06-17 |",
        "| Autor  | rkokubo |",
        "## Contexto",
        "## Decisão",
        "## Consequências",
        "## Alternativas consideradas",
        "## Referências",
    ):
        assert marker in md


def test_nao_fazer_section_optional() -> None:
    assert "Restrições deliberadas" not in _base_adr().to_markdown()
    md = _base_adr(nao_fazer="Não fabricar.").to_markdown()
    assert "### Restrições deliberadas (não fazer)" in md
    assert "Não fabricar." in md


def test_supersede_rendered_by_reference() -> None:
    md = _base_adr(supersedes=[6]).to_markdown()
    assert "Supersede (por referência — ADR-0009):** ADR-0006." in md
