---
name: "journey-upgrade"
description: "Migra um projeto entre tiers (Basic→Standard→Enterprise) de forma ADITIVA e não-destrutiva: deteta o tier vigente, calcula o delta e escreve só o que falta, fechando com um ADR de upgrade + commit DECISION. Reusa o instalador da 001 (ATRITO-16). Comando condutor mecânico (ADR-0017); gate humano (ADR-0005)."
argument-hint: "--to=<basic|standard|enterprise>"
compatibility: "Requires a Journey project base (journey-core/journey-skill da 001) e o pacote journey-skill (journey-upgrade CLI)."
metadata:
  author: "journey"
  source: "specs/002-journey-upgrade"
  adr: "ADR-0017 (padrão condutor) + ADR-0005 (git conduzido, gate) + ATRITO-16 (merge não-destrutivo) + ADR-0008"
user-invocable: true
disable-model-invocation: false
---

# `/journey-upgrade --to=<tier>` — migração de tier

Comando **condutor mecânico** (ADR-0017): skill **fina** — conduz e **gateia**; delega à mecânica
`journey-upgrade` (que **reusa o instalador da 001** — não reimplementa). **Não-destrutivo é a
espinha:** nunca remove nem reescreve o que o projeto já tem.

## O que fazer

1. **Pré-visualizar o delta (sem escrever):**
   ```
   journey-upgrade preview --to=standard --repo-root .
   ```
   Mostra **só o que falta** para o alvo (artefatos ausentes + `specs/`). *(Já no alvo → "idempotente".)*

2. **Gate humano** (ADR-0005). Apresente o delta; só com aprovação prossiga (o passo seguinte
   **escreve** — sempre aditivo, nunca destrutivo).

3. **Aplicar:**
   ```
   journey-upgrade apply --to=standard --repo-root .
   ```
   Materializa o delta Basic→Standard (reusa `materialize_artifacts`: escreve só o ausente; `CLAUDE.md`
   mesclado por managed-block — ATRITO-16), cria `specs/`, escreve o **ADR de upgrade** e ecoa o
   commit `DECISION(meta): upgrade to <tier> [ADR-NNNN]`. **NÃO commita** — o humano revê e commita.

## Fronteiras (o que NÃO fazer)

- **Não-destrutivo absoluto** (FR-004): nunca tocar no que o utilizador já tem; na dúvida, reporta.
- **Tier ambíguo** (só um de `.specify/`/`specs/`) → **escala**, não adivinha.
- **`--to=enterprise` = GUARD-ONLY:** o delta exato é a **fronteira open-core (ATRITO-50, decisão de
  fim)** — não materializar nada comercial; tratar os componentes Enterprise como **externos**.
- **Downgrade** (ex.: standard→basic) → **DISJUNTOR:** pára e **chama o owner** (FR-016, política
  não-cravada — não decidir aqui).
- **Dimensão "versão da metodologia" (ATRITO-15)** — carimbo de versão, deteção de defasagem,
  diff de regras, re-sync — **DEFERIDA** (não-desenhada); não construir.
- **Veto-UNC** (ADR-0004); git conduzido com gate (ADR-0005); 1 worktree por agente se paralelo (ADR-0019).
