---
name: "journey-manuals-generate"
description: "Gera os 4 manuais canónicos do PROJETO-ALVO (user/admin/troubleshooting/technical) a partir de ADRs, specs, código, testes e Histórico. Conteúdo PT por padrão (com escolha); filenames em inglês. Comando condutor judgment-heavy (ADR-0017, pólo da 004 — skill grossa). Invocação manual; sugere revisão humana antes do commit."
argument-hint: "[--language pt-BR|en-US]"
compatibility: "Requires a Journey project (docs/adr, specs, HANDOVER, git) + journey-skill e journey-core instalados."
metadata:
  author: "journey"
  source: "specs/008-journey-manuals-generate"
  adr: "ADR-0017 (Decisão 1 — condutores; pólo de julgamento, skill grossa)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-manuals-generate` — gerar os manuais do projeto-alvo

Comando **condutor judgment-heavy** (ADR-0017, pólo da 004 — skill **grossa**, não fina): **tu** (a skill) **sintetizas** os manuais; a mecânica (`journey-manuals-generate`, pacote `journey-skill`) só **lê as fontes** e **escreve** o que tu autoras.

> **Documenta o PROJETO-ALVO, não o Journey** (FR-007). Quando o Journey está instalado no projeto de um utilizador, os manuais são do projeto **desse utilizador**. (No próprio repositório Journey — dogfooding — o projeto-alvo é o Journey-projeto.)

## O que fazer

1. **Idioma** (FR-005): o conteúdo é **PT por padrão**. **Informa** o utilizador do padrão e **oferece** outro idioma **antes de gerar** — os suportados estão em `journey_core.models.manual.SUPPORTED_LANGUAGES` (default `DEFAULT_LANGUAGE` = `pt-BR`). A escolha afeta **só o conteúdo**; o **filename** fica **sempre em inglês** (`user.md`…), independentemente da escolha (FR-006, §8.4/§8.5).

2. **Ler as fontes** (FR-003):
   ```
   journey-manuals-generate read-sources --repo-root .
   ```
   Devolve um **digest leve** (ADRs, specs, módulos, ficheiros de teste, fase atual, `sentinel_tests`). Usa-o como **índice** e **lê os ficheiros reais** (ADRs, specs, código, HANDOVER) para sintetizar — a síntese é **tua**, não do digest.

3. **Sintetizar os 4 manuais canónicos** do projeto-alvo (Vision §10.3), seguindo a **diretriz de tom** (didático/narrativo/leigo — `docs/design/roadmap-render-fase-a.md` § Tom e qualidade):
   - **`user.md`** — como o utilizador final usa o produto.
   - **`admin.md`** — instalação, configuração, operação.
   - **`troubleshooting.md`** — problemas comuns e resolução (nasce mínimo; cresce na fase Run).
   - **`technical.md`** — arquitetura e conteúdo técnico do projeto-alvo.

   Cada manual **referencia os ADRs pertinentes** (por `ADR-NNNN`) e inclui a secção **"comportamentos protegidos por testes-sentinela"** derivada do **Regression Guard** — **conceito transversal da Vision, referenciado e NÃO redefinido**. **Se `sentinel_tests` vier vazio**, a secção sai **vazia/avisada** (ex.: *"Sem testes-sentinela registados — a preencher quando existirem."*). **NÃO fabricar** comportamentos protegidos.

4. **Escrever** cada manual (autorado por ti) via a mecânica:
   ```
   journey-manuals-generate write-manual --payload <manual.json> --repo-root .
   ```
   `<manual.json>` = `{type, content, language, adr_refs}` que **tu** autoras (`type` ∈ user/admin/troubleshooting/technical).

5. **Sugerir revisão humana antes do commit** (FR-009, ADR-0005) — não commitar cego.

## Fronteiras

- **A síntese é tua** (julgamento); a mecânica só lê/escreve. **Não** delegar a síntese a templates.
- **Projeto-alvo, não o Journey** (FR-007).
- **Não fabricar** (ATRITO-32): sem fonte → secção vazia/avisada; nunca inventar.
- **Gatilho automático ao fim de Build (FR-008) é DEFERIDO** (Build não vivido) — invocação **manual**; **não** ligar à 007.
- **Veto-UNC / runtime** (ADR-0004); idioma conteúdo-PT-default / filename-EN (§8.4/§8.5).
- **4 manuais** (incl. `technical`); divergência com a methodology §9.3 = **ATRITO-49** (v2.2), **não reabrir**.
