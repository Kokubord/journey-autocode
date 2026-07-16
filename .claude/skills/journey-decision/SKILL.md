---
name: "journey-decision"
description: "Registra uma decisão material como ADR: gateia 'registrar como decisão material?', gera o ADR draft no padrão canônico (próxima numeração), adiciona a entrada «Decisões frescas» e propõe o commit DECISION. Supersede por referência; conflito é detectado pelo Source Guard. Comando condutor mecânico (ADR-0017)."
argument-hint: "Opcional: a decisão a registrar"
compatibility: "Requires a Journey project (HANDOVER.md, docs/adr/) and the journey-skill package (journey-decision CLI)."
metadata:
  author: "journey"
  source: "specs/012-journey-decision"
  adr: "ADR-0017 (Decisão 1 — padrão dos condutores; D2 — reusa o schema models/adr.py da 004)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-decision` — registrar uma decisão material como ADR

Comando **condutor mecânico** (ADR-0017): skill **fina** — **gateia e autora**, delegando a
mecânica determinista ao CLI `journey-decision` (pacote `journey-skill`). O ADR usa o **schema
canônico já existente** (`journey_core.models.adr.Adr`, da 004 — **reusado, não recriado**; ADR-0017
D2 / anti-drift ATRITO-61).

## O que fazer

1. **Gate humano (FR-003 / ATRITO-32 / ADR-0005):** confirme com o owner — *"registrar como decisão
   material?"*. **Só prossiga com aprovação.** Propor, nunca afirmar.

2. **Ler o contexto** (FR-001):
   ```
   journey-decision read-context --repo-root .
   ```
   Devolve `current_phase`, `next_adr_number` (próxima numeração livre, evita duplicata) e `adr_count`.

3. **Autorar o ADR draft** no padrão canônico (FR-002). Monte os campos do `Adr`: `number`
   (= `next_adr_number`), `slug`, `title`, `status` (default `Aceito`), `date`, `author`, e as seis
   secções (`contexto`, `decisao`, `nao_fazer`, `consequencias`, `alternativas`, `referencias`).
   **Pré-preencha o essencial e deixe o ADR ABERTO para o humano completar** contexto/alternativas
   (FR-004 — não auto-finalize). Grave o JSON e:
   ```
   journey-decision write-adr --payload <adr.json> --repo-root .
   ```

4. **Supersede por referência** (FR-005), quando aplicável: ponha os números revertidos em
   `supersedes` — o `to_markdown` rende a linha "Supersede (por referência — ADR-0009)"; o ADR
   **anterior NÃO é editado** (história imutável).

5. **Conflito com ADR existente** (FR-006): a **detecção** é do **Source Guard** (ADR-0013, classe
   CONFLITA-COM-PRECEDÊNCIA) — ele alerta **antes**; o `/journey-decision` apenas **registra**
   (família detecta × registra; coerência fixada, não decisão nova).

6. **Entrada «Decisões frescas» + commit sugerido** (FR-003):
   ```
   journey-decision register --summary-pt "<resumo PT>" --summary-en "<EN summary>" --number <N> --scope <scope> --repo-root .
   ```
   Adiciona o bullet datado **em PT** (HANDOVER «Decisões frescas») e imprime `DECISION(scope): <EN summary> [ADR-NNNN]` **em inglês** — os dois são **separados** (ADR-0001: docs/decisões em PT, commits em EN), sem trailer
   `Co-Authored-By` — ATRITO-31). O git é **conduzido com gate humano** (ADR-0005); não commite cego.

## Fronteiras

- **Veto-UNC / runtime** (ADR-0004): a mecânica roteia a escrita; nunca via `\\wsl.localhost\`.
- **Decisão não-material** (trivial): **não** gere ADR — reporte.
- **Sem decisão material**: não fabrique ADR.
- **DEFERIDO (FR-007, não-vivido):** a automação como exercida end-to-end (heurística de detecção de
  duplicata, montagem interativa do commit) **não** existe — o comando nunca rodou. Use o padrão firme
  acima; não invente o fluxo deferido.
