---
name: "journey-phase-end"
description: "Encerra uma fase/sub-fase: valida o checklist de saída (bloqueia se testes/CI falham), gera o PR estruturado (decisões materiais + ADRs do período + checklist de revisão) o roadmap é renderizado no Site (render local aposentado — feature 023/ATRITO-78). Comando condutor mecânico (ADR-0017), par da 006."
argument-hint: "<phase> <slug> (ex.: build dashboard)"
compatibility: "Requires a Journey project (HANDOVER.md, git) + journey-skill e journey-roadmap instalados."
metadata:
  author: "journey"
  source: "specs/007-journey-phase-end"
  adr: "ADR-0017 (Decisão 1 — condutores; sub-padrão mecânico, par da 006)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-phase-end <phase> <slug>` — encerrar uma fase com PR estruturado

Comando **condutor mecânico** (ADR-0017, par da 006): skill **fina** — conduz o fecho, narra o
checklist de saída e gateia; delega a mecânica ao CLI `journey-phase-end` (pacote `journey-skill`).

## O que fazer

1. **Checklist de saída** (FR-002 / SC-003 — **bloqueia** se testes/CI falham). Você fornece o estado
   (testes/CI — pode consultar `gh pr checks`):
   ```
   journey-phase-end exit-check --tests-ok --ci-ok --handover-ok [--build-end --manuals-ok]
   ```
   Se sair **BLOQUEADO** (código ≠ 0), **não encerre** — reporte as falhas e pare até corrigir. Em
   **fim de Build**, o checklist inclui *manuais* (gerados por `/journey-manuals-generate`, spec 008).

2. **PR estruturado** (FR-003/005). Determine o `<since>` (o commit de phase-start — a base da branch
   `feat/phase-N-<slug>` criada pela 006):
   ```
   journey-phase-end build-pr <phase> <slug> --since <sha-do-phase-start> --repo-root .
   ```
   Imprime o corpo do PR: **Decisões materiais desta fase** (commits `DECISION`) + **ADRs criados**
   (tags `[ADR-NNNN]` do período) + **checklist de revisão**. Use-o para abrir o PR.

3. **Autorar o briefing da sub-fase que fecha** (ADR-0018, Fatia 3). Escreva um briefing **didático, narrativo, para um leigo** — *o que é · para que serve · em que estado está · o que aconteceu* — **não** um rótulo técnico nem o nome do comando. Siga a **diretriz de tom** em `docs/design/roadmap-render-fase-a.md` (§ Tom e qualidade) e ADR-0018 §3. Grave-o **antes** do regen (para o `roadmap.html` sair já com ele):
   ```
   journey-phase-end set-briefing <unit-id> "<briefing>" --repo-root .
   ```
   `<unit-id>` = id da sub-fase/fase no roadmap (ex.: a feature fechada). A escrita é a fonte única `journey_core.briefing_ops` (anti-drift); o regen seguinte preserva-o (`merge_authored` da 005).

4. **Roadmap: render no Site (não local).** O render local de roadmap foi **aposentado** (feature 023 /
   ATRITO-78 / ADR-0032): o fim de fase **não** regenera mais um `roadmap.yaml`/`.html` local. O roadmap
   renderizado vive **no Site**, que lê os dados crus do repositório (HANDOVER/ADRs/`tasks.md`/tokens).
   Nada a fazer aqui — este passo permanece só como marcador histórico do fluxo antigo.

5. **Amarrar a sessão à fase no bloco Closing (ATRITO-43 fix-real).** Capture o id real da sessão e grave-o como `sessao_id` no bloco ` ```yaml ` que abre a entrada de «Histórico de sessões» do HANDOVER (ADR-0012 §12.1):
   ```
   journey-phase-end session-id
   ```
   Imprime o `CLAUDE_CODE_SESSION_ID` — ou **`unresolved`** EXPLÍCITO se a var não chegou ao processo (**nunca** um valor vazio que parece amarrado). É o que liga os tokens da sessão à fase no pipeline (005 FR-016) — **sem** o frágil "`.jsonl` mais recente". **Pré-requisito (ADR-0031):** a var precisa alcançar o processo do skill — `WSLENV=CLAUDE_CODE_SESSION_ID/u` ou passá-la explícita na invocação `wsl`.

6. **Oferecer a próxima fase (encadeamento — ATRITO-70).** Em vez de só sugerir, mostre uma **oferta acionável** — **nome da próxima fase + 1 linha didática do que faz + "iniciar?"** (tom §7) — com o **comando exato**: `/journey-phase-start <próxima> <slug>`. A próxima vem de `journey_core.phase_chain.build_phase_offer` (consulta a ordem canônica `Phase`, **fonte única — não** uma 2ª lista). **SUGERE, não invoca** (clarify Q1 — o **ato de rodar** é a confirmação humana; uma skill **não dispara** outra). **Recusa/adia (§7 Q2):** registre *"fase X concluída, próxima pendente"* no **HANDOVER** (reusa o existente) e **re-ofereça** na próxima sessão — recusar **nunca é beco**. **Última fase (Run):** `build_phase_offer` retorna vazio → **sem próxima**, **não fabrique** ciclo Run→Discovery (§7 Q3 / ATRITO-32). *(007 é a fronteira genérica de fim de fase — via `next_phase` cobre as 6 transições.)*

## Fronteiras

- **git conduzido, gate humano, merge sem squash** (ADR-0005/CLAUDE.md): você prepara o PR; a
  **abertura/merge/CI/proteção de main no host é DEFERIDA** (FR-008 — nenhuma fase Build foi vivida).
  Não tente executá-la.
- **Roadmap é da spec 005** (FR-004/FR-007): o phase-end **dispara**, **não redefine**; o gatilho
  canônico está decidido B (manual-só R1) na 005 — não reabrir.
- **Veto-UNC / runtime** (ADR-0004).
- **Sem commits desde o phase-start**: PR avisado/vazio, não fabricado.
