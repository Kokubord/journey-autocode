---
name: "journey-scope-review"
description: "Scope Guard: o rito pesado de re-entrada Visão/Discovery quando o escopo muda. Um mecanismo, três gatilhos (deriva detectada · pedido manual · detalhe emergente no Build), o mesmo rito de 4 etapas (reabrir Visão delimitada → Discovery/ADRs → plano de impacto+roadmap → ADR de escopo). Escala a partir do Source Guard. Comando condutor judgment-heavy (ADR-0017); Plan mode do IDE = motor, condução = Journey."
argument-hint: "(sem args — gatilho manual; também aciona por deriva detectada ou detalhe emergente no Build)"
compatibility: "Requires a Journey project (HANDOVER.md, docs/adr/, roadmap.yaml) and the journey-skill package (journey-scope-review CLI)."
metadata:
  author: "journey"
  source: "specs/014-journey-scope-review"
  adr: "ATRITO-34 (Scope Guard — fonte primária) + ADR-0013 (Source Guard, escala) + ADR-0017 (padrão condutor)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-scope-review` — Scope Guard (re-entrada Visão/Discovery)

Comando **condutor judgment-heavy** (ADR-0017): a sua essência é **conduzir um rito**, não
executar mecânica. Esta skill é **grossa** — ela **conduz**; a mecânica Python só **lê o contexto**
(`journey-scope-review read-context`) e o registo da decisão **reusa** o caminho de ADR existente
(`/journey-decision` / `journey_core.adr_ops`). **O motor do rito é o Plan mode do IDE; a condução
é do Journey** (FR-006, ATRITO-34).

> **Fonte:** ATRITO-34 (Scope Guard) + ADR-0013 (Source Guard). **Não há verbete Vision §10** —
> não invente um (ATRITO-53).

## Quando dispara — um mecanismo, três gatilhos (FR-001)

O **mesmo rito** é conduzido nos três casos (SC-001):

1. **Deriva detectada** (automático) — o agente percebe que o trabalho está a sair do escopo
   combinado. *(O detetor automático de deriva é **FR-007 — H2, não desenhado**; por agora o
   reconhecimento é do condutor, não de um mecanismo.)*
2. **Pedido explícito** (manual) — alguém invoca `/journey-scope-review`.
3. **Detalhe emergente no Build** — a construção revela algo que muda o âmbito.

## Escala a partir do Source Guard (FR-002, ADR-0013)

O **Source Guard** (triagem leve, a cada coisa nova) **escala** para aqui **só quando classifica
"adição/mudança de escopo real"**. Trivial **não** escala (fica na triagem leve). É a fronteira
leve↔pesado da **família Guards** (Regression protege comportamento; Source, afirmações; **Scope,
escopo**).

> **Exemplo vivido (não resolver aqui):** o **ATRITO-50** (revisão do modelo open-core) foi uma
> escalada real — algo grande entrou, **não virou spec**, virou **decisão estratégica
> registada/adiada**. Cite-o como exemplo; **não** decida o open-core neste rito.

## O rito — 4 etapas, reentrante e CONTIDO (FR-003/004)

Primeiro, **leia o contexto** (não decide nada):

```
journey-scope-review --repo-root .
```

Devolve: Visão presente (caminho), nº de ADRs + último, roadmap presente, e as 4 etapas. Com isso,
conduza — **delimitado, sem recomeçar do zero**:

1. **Reabrir a Visão (delimitada).** Reabre-se **só a questão em causa**, nunca a Visão inteira — recorte ao ponto. Pergunta-guia: *esta mudança **cabe** no que já foi combinado (Visão / ICP / princípios) ou **contradi-lo**?* Se **cabe**, segue o rito (vira esforço novo **dentro** do plano); se **contradiz**, é o **ADR de escopo** (etapa 4) que assume a contradição **explicitamente** — não se contorna em silêncio.
2. **Discovery → ADRs.** As decisões materiais que emergirem viram ADRs (use `/journey-decision`).
3. **Plano de impacto + roadmap.** Análise de impacto (spec nova/revisada) **e** atualização do
   **planeado** do roadmap — escopo (planeado vs. adicionado) **e** cronograma/postergação —
   **via spec 005** (`roadmap.yaml`), incorporando o novo esforço **DENTRO** das fases/tarefas.
   **Não redefina** o roadmap; consuma-o no nível de design (**não nomeie campo concreto** —
   coerência-005, como a 011). **Carimbo da Origem (Passo 3):** ao **gerar a spec** da fatia emergente, escreve no cabeçalho `**Origem**: emergente (scope-review, ADR-NNNN)` (espelha o `**Status**:`), citando o ADR de escopo da etapa 4. É o que torna a subfase **distinguível** de uma planejada no roadmap — ver «A marca emergente» abaixo.
4. **ADR de escopo.** Registe a decisão de escopo como um **ADR** (reuse o caminho de ADR —
   `/journey-decision` / `adr_ops`), datado e rastreável (SC-003).

**Resultado pode não ser spec:** como no ATRITO-50, a re-entrada pode concluir por **decisão
estratégica registada/adiada**, não necessariamente uma spec nova.

## A marca emergente — o carimbo `**Origem**:` (Passo 3 do Motor)

**O quê.** Uma fatia que nasce **deste rito** (scope-review, no Build) é **emergente** — não estava no plano da Discovery. Para o roadmap **distinguir** trabalho emergente de planejado, a spec gerada leva, no cabeçalho, um campo **`Origem`** (irmão do `**Status**:`):

```
**Origem**: emergente (scope-review, ADR-NNNN)
```

**A REGRA (simples e sem retroagir).**
- **Presença** de `**Origem**: emergente` → a subfase é **EMERGENTE**.
- **Ausência** do campo → a subfase é **PLANEJADA**. (As ~17 features existentes **não** são retroagidas: ausência **já significa** planejado — é o default correto, zero migração.)
- O `ADR-NNNN` citado é o **ADR de escopo** (etapa 4) que originou a fatia — dá rastreabilidade (quem decidiu, quando, porquê).

**O PORQUÊ.** Sem a marca, o sub-plano emergente aparece **indistinguível** do planejado no roadmap (o owner viu isto ao vivo no teste do 018). A marca deixa o roadmap **honesto sobre o que era plano vs. o que emergiu** — base para, no futuro, medir desvio de escopo (liga ao ATRITO-79 fundo / ATRITO-76; **não** é medido agora).

**A PONTE (dependência crítica — não quebrar um lado sem o outro).** Este carimbo é gravado **aqui** (metodologia, no projeto do usuário) e **lido pelo Site** (consolidação → marca a subfase no `view_json` → render mostra o badge). É a mesma fronteira do **ADR-0032** (coleta/metodologia ↔ consolidação/Site). **Se mudares o nome/formato do campo `Origem` aqui, o leitor do Site quebra** (e vice-versa) — a especificação do lado Site vive em `docs/MOTOR-FLUXO-PLANO-EMERGENTE.md`. Mantém os dois em sincronia.

**Como AJUSTAR (para um IDE futuro).** O comportamento é deliberadamente simples para ser mexível:
- Mudar a **redação/idioma** do valor → ok, desde que o **leitor do Site** reconheça (hoje: começa por `emergente`).
- Mudar o **nome do campo** (`Origem` → outro) → **mudança de contrato**: atualiza A (aqui) **e** B (o reader do Site) **no mesmo PR**, senão a marca some em silêncio.
- Adicionar outras origens (ex.: `migração`, `hotfix`) → estende a regra; o default (ausência = planejado) **não** muda.

## Fronteiras (o que NÃO fazer)

- **FR-007 — H2, deferido:** o **detetor automático de deriva**, o **formato fino do ADR de
  escopo** e o **passo-a-passo reentrante exato** **não estão desenhados**. Se te vires a
  desenhá-los, **pára** — é desenho-sem-fonte (ATRITO-53/0008). O que está firme é o **shape**
  acima.
- **Não decidir o ATRITO-50** (open-core) — a 014 é o **guarda**, não a decisão.
- **Não redefinir o roadmap** (é da 005) nem nomear campos do `roadmap.yaml` (coerência-005).
- **Veto-UNC / runtime** (ADR-0004): a escrita é roteada; nunca via `\\wsl.localhost\`.
- **git conduzido, gate humano** (ADR-0005): o ADR de escopo e o roadmap entram por PR, com gate.

## Modo: Reconciliação fonte×realidade (ATRITO-74)

Além da deriva de **escopo** (rito de 4 etapas acima), a 014 opera um **modo de reconciliação** — irmão, não idêntico. Quando o **estado real diverge da FONTE** (trabalho feito mas não registrado em `tasks.md`/`Status`; **incremento órfão** = feature com trabalho sem citação; roadmap stale; superseded não refletido), o agente:

1. **DETECTA** — roda `journey-roadmap reconcile` (mecânica determinista; **lista** as divergências fonte×realidade — **nunca decide nem edita**).
2. **MOSTRA** ao usuário as divergências, **com a evidência** do detector — **nunca afirma sem fonte** (Source Guard).
3. **CONDUZ** o registro **na FONTE** (marcar `tasks.md`/`Status`; citar a feature no ADR/atrito) com **CONFIRMAÇÃO humana** — **nunca auto-dispara**.
4. **REGENERA** via `journey-roadmap generate` (a 005). **NUNCA edita o `roadmap.yaml` à mão** — corrige a **fonte**, regenera.

**Gatilho (ATRITO-74/C3):** **oferecido** (a skill detecta e **oferece** reconciliar) **+ manual** (o usuário invoca); **nunca automático**.

**Invariante:** detectar → mostrar → conduzir → **humano confirma** → regenerar. A deriva de **escopo** pergunta *"isto cabe na Visão?"*; a reconciliação pergunta *"a FONTE reflete o que já foi feito?"*. O **incremento órfão** (achado da 75 — ex.: a 016, cujo ADR-0024 não cita "016") é um dos casos que este modo reconcilia.
