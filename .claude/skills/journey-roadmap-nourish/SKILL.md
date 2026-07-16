---
name: "journey-roadmap-nourish"
description: "Faz o backfill dos briefings ricos do roadmap: percorre os nós (fase/sub-fase) ainda sem briefing, lê as fontes reais de cada um e autora a narrativa didática, persistindo via a fonte única e regenerando o roadmap. Fecha o gap forward-only (ADR-0018, Fatia 5) — nós já concluídos na adoção também ficam ricos. Comando condutor mecânico (ADR-0017)."
argument-hint: "(sem args; opcional --include-tasks no list)"
compatibility: "Requires a Journey project (roadmap.yaml, HANDOVER.md, git) + journey-skill e journey-roadmap instalados."
metadata:
  author: "journey"
  source: "ADR-0018 (Fatia 5 — backfill)"
  adr: "ADR-0017 (condutores; sub-padrão mecânico) + ADR-0018 (nutrição rica)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-roadmap-nourish` — nutrir (backfill) os briefings do roadmap

Comando **condutor mecânico** (ADR-0017): skill **fina** — você conduz a autoria (julgamento de
LLM); a mecânica (enumerar pendentes, persistir, regenerar) é do CLI `journey-roadmap-nourish`
(pacote `journey-skill`). Reúso da fonte única `journey_core.briefing_ops` (anti-drift, ATRITO-61).

Resolve o **gap forward-only** (ADR-0018 §Consequências → Fatia 5): as skills de fronteira só
nutrem nós dali pra frente; esta skill nutre os **já concluídos / ainda sem briefing**, para que
nenhum projeto chegue ao go-live com a coluna técnica.

## O que fazer

1. **Listar os nós pendentes** (read-only). Mostra cada nó + **quais campos faltam** + a **fonte a ler**:
   ```
   journey-roadmap-nourish list --repo-root .
   ```
   Cada linha: `<id>  <nível>  <estado>  <campos-em-falta>  <nome>  <ref>`. Alvo são **fases +
   sub-fases**; tarefas ficam de fora por design (proporcional — ATRITO-33). Se quiser: `--include-tasks`.

2. **Para cada nó, autorar os TRÊS campos a partir das FONTES REAIS** (ADR-0018 Fatia 6) — nunca de
   memória, nunca fabricado. Os três são **distintos** (a coluna não repete o popup). Leia o `<ref>`
   da linha (`summary_ref` → Vision/methodology §, spec/plan/tasks) + `HANDOVER.md` + `git log` do
   período. Siga a **diretriz de tom** em `docs/design/roadmap-render-fase-a.md` (§ Tom e qualidade):
   - **`briefing`** — *o que é · para que serve* (conceitual, popup). Narrativo, para leigo.
     ```
     journey-roadmap-nourish set-briefing <unit-id> "<briefing>" --repo-root .
     ```
   - **`deliverable`** — o que o nó **entrega** (popup "Entregável").
     ```
     journey-roadmap-nourish set-deliverable <unit-id> "<entregável>" --repo-root .
     ```
   - **`notes`** — **histórico/execução**: *o que aconteceu · em que estado está* (coluna
     "informações"), do HANDOVER/git. **Não** repita o conceitual aqui.
     ```
     journey-roadmap-nourish set-notes <unit-id> "<histórico>" --repo-root .
     ```
   A escrita reusa `journey_core.briefing_ops` (anti-drift); o regen preserva via `merge_authored`.

3. **Regenerar o roadmap** para o `roadmap.html` sair com os três campos (popup + coluna):
   ```
   journey-roadmap-nourish regen-roadmap --repo-root .
   ```

4. **Sugerir revisão humana** dos textos autorados antes do commit (julgamento — gate humano).

## Fronteiras (Source Guard)

- **Anti-fabricação (ADR-0016/0018):** só nutre nós **existentes** sem briefing, **a partir das
  fontes**. Sem fonte real para um nó → não invente; deixe pendente e reporte.
- **Gerador é da spec 005:** esta skill **autora e dispara**, não redefine o gerador nem o schema.
- **Idempotente:** só toca nós sem briefing; os já autorados são preservados, nunca sobrescritos.
- **Veto-UNC / runtime** (ADR-0004); **gate humano** por WRITE/COMMIT (ADR-0005).
