---
name: "journey-phase-start"
description: "Abre uma fase/sub-fase: marca-a ativa no HANDOVER, narra o checklist do que esperar e — a partir da 2ª sub-fase de Build — cria a branch feat/phase-N-<slug> + PR template com gate humano. Comando condutor mecânico (ADR-0017)."
argument-hint: "<phase> <slug> (ex.: build dashboard)"
compatibility: "Requires a Journey project (HANDOVER.md) and the journey-skill package (journey-phase-start CLI)."
metadata:
  author: "journey"
  source: "specs/006-journey-phase-start"
  adr: "ADR-0017 (Decisão 1 — padrão dos comandos condutores; sub-padrão mecânico)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-phase-start <phase> <slug>` — abrir uma fase/sub-fase

Comando **condutor mecânico** (ADR-0017): a sua natureza é sobretudo determinista, por isso esta
skill é **fina** — **conduz, valida e gateia**, e **delega toda a mecânica** ao CLI
`journey-phase-start` (pacote `journey-skill`). O checklist é **templated** (não o improvise).

## O que fazer

1. **Ler o estado** (FR-002 — não sobrescrever cego):
   ```
   journey-phase-start read-state --repo-root .
   ```
   Considere a fase anterior antes de marcar a nova.

1b. **GATE Discovery→Build — SÓ ao abrir `build` (ATRITO-41).** Antes de marcar o Build ativo, rode:
   ```
   journey-phase-start check-discovery --repo-root .
   ```
   Se `complete=false`: **NÃO marque o Build.** Apresente os `gaps` (features só-esqueleto — sem `plan`/`tasks`, ou constituição placeholder) + a fronteira **ATRITO-41** (a Discovery entrega o **plano completo**), e **exija confirmação EXPLÍCITA** do owner para prosseguir mesmo assim — registrando o override consciente no HANDOVER (ADR-0005). **Nunca sugira/abra o Build com a Discovery incompleta sem esse gate.** Fora do `build`, pule este passo.

2. **Marcar a fase ativa + narrar o checklist** (FR-001/003/005). `<phase>` MUST ser uma das 6
   canónicas (warmup/foundation/discovery/build/release/run) — o CLI valida e alerta se inválida:
   ```
   journey-phase-start mark <phase> <slug> --repo-root .
   ```
   Apresente ao operador a confirmação (`marker`) e o `checklist` devolvido — **narre-o como está**,
   não invente itens.

3. **Autorar o briefing de ABERTURA da fase/sub-fase** (ADR-0018, Fatia 3b). Logo após o `mark`, escreva um briefing **didático, narrativo, para um leigo** — *o que é · para que serve · o que está planeado* (o *"o que aconteceu"* enche-se no fecho, pela 007). Siga a **diretriz de tom** em `docs/design/roadmap-render-fase-a.md` (§ Tom e qualidade) e ADR-0018 §3 — **não** um rótulo técnico nem o nome do comando. Depois grave-o:
   ```
   journey-phase-start set-briefing <unit-id> "<briefing>" --repo-root .
   ```
   `<unit-id>` = id da fase/sub-fase aberta no roadmap. Fonte única `journey_core.briefing_ops` (anti-drift). A 006 **não regenera** — o briefing aparece na próxima geração (no fecho pela 007, ou um `generate` manual), preservado por `merge_authored`. **Se ainda não existe `roadmap.yaml`**, o verbo avisa e sai 0 (entra quando o roadmap existir).

4. **Governança de branch — CONDICIONAL ao Build** (FR-004). **Só a partir da 2ª sub-fase de Build**
   se cria branch; em Discovery/1ª sub-fase **não force**. Você (condutor) determina:
   - se a fase é **Build** e a sub-fase é a **2ª ou posterior** (pela ordem no roadmap/HANDOVER);
   - o **N** (ordinal da sub-fase no roadmap) e o `slug`.
   Se — e só se — for o caso, **peça o gate humano** (ADR-0005) antes de criar a branch; com
   aprovação:
   ```
   journey-phase-start branch --n <N> --slug <slug> --repo-root .
   ```
   Isto cria `feat/phase-N-<slug>` (local) + o PR template. **Fora do Build, não chame `branch`.**
   - **Fatie fases grandes (ATRITO-96).** Uma sub-fase = uma **fatia mergeável** (uma US / um entregável coerente), **não a fase inteira**. Rode `journey-phase-start subphase-advice --repo-root .`; se vier `slice_candidates`, **avise o owner** e proponha quebrar a fase em várias branches `feat/phase-N-<fatia>` (setup / us1 / us2 …), cada uma um PR pequeno. PR gigante = revisão ruim + roadmap parado até o merge.

## Fronteiras

- **Veto-UNC / runtime** (ADR-0004): a mecânica já roteia a escrita; nunca escreva via `\\wsl.localhost\`.
- **git conduzido, gate humano** (ADR-0005): branch é local; **push/abertura/merge de PR no host é
  deferido** (FR-008 — nenhuma fase Build foi vivida). Não tente proteger main no host nem abrir PR.
- **`feat/phase-N-<slug>` ≠ `release/<version>`** (FR-007): a branch de release é do
  `/journey-release-start` (spec 009) — não confundir.
- **Fase anterior não encerrada?** Sugira `/journey-phase-end` antes (consistência com a spec 007).
