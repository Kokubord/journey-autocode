---
name: "journey-bootstrap"
description: "Conduz o bootstrap conduzido pelo agente (feature 016): após o pull da base, executa o journey-init com --target seguro, valida que arrancou, e ENTREGA o usuário no Warmup — reusa 001/006/007, não reimplementa fases. Entrega no Warmup e PARA (o encadeamento de fases é do ATRITO-70). Comando condutor judgment-heavy (ADR-0017)."
argument-hint: "<origin-url> <project-dir> (repo privado da base + pasta NOVA do projeto)"
compatibility: "Requires git + journey-skill (journey-bootstrap/journey-init). Multi-ambiente (ADR-0004)."
metadata:
  author: "journey"
  source: "specs/016-agent-bootstrap/conducting-skill-slice.md"
---

# `/journey-bootstrap` — conduzir o bootstrap até a metodologia (entrega no Warmup e PARA)

Comando **condutor judgment-heavy** (ADR-0017): a condução (julgamento, validação, entrega) é desta
**SKILL.md**; a mecânica é **reusada** — `journey-bootstrap` (pull + guard, fatia anterior),
`journey-init` (001) e `journey_core.pull_ops.build_conduct_plan` (a sequência de comandos). **Reusa,
não reimplementa** (anti-ATRITO-61). **Não toca docs curados** (ATRITO-71). **Última fatia da 016.**

## 0. Detectar a Rota (fast-path) — julgamento

Reconheça o usuário (clarify Q3): **experiente** (já tem visão/Warmup) → **Rota 1, fast-path** (pula a
tutela); **novo** → **Rota 2, condução completa**. **Mesmo fluxo, dois ritmos** — não há dois caminhos.

## 1. Pull da base (reusa a fatia anterior — guard de destino)

Rode o `journey-bootstrap` com a **origem configurável** (repo privado), uma **pasta-base NOVA** e a
**pasta-projeto NOVA** (`--project-dir` = `journey-init --target`):

```
journey-bootstrap --origin-url <repo-privado> --dest <base-nova> --project-dir <projeto-novo>
```

O **guard de destino** já recusa repo/pasta **existente** (segurança-por-construção); o acesso usa a
**credencial git local** — a skill **nunca** toca/imprime o segredo; **sem acesso amplo**. Se o pull
**falhar** → a mensagem honesta já orienta (autenticar a ESTE repo) → **abortar limpo** (passo 4).

## 2. Executar o `journey-init` (reusa a 001 — `--target` seguro)

O passo 1 **anuncia** o handoff exato. Rode-o — o `--target` seguro **já está garantido** pelo guard:

```
journey-init --project-name <nome> --target <projeto-novo> --templates <base-nova>/templates
```

**Reusa a 001** (não reimplementa o install; a 001 é não-destrutiva e tem o seu próprio gate de pasta).

## 2b. (Opcional) Vincular ao GitHub — INSTRUIR, nunca criar

Se o usuário quer um repositório remoto, **conduza o vínculo — sem criar o repo nem acessar a conta dele**:

1. **Instrua** o usuário a **criar o repositório no GitHub ele mesmo** — pela **web** ("New repository"), ou via `gh repo create` **se ELE quiser** (desejo do usuário, não da metodologia). Passo simples, em linguagem de não-dev.
2. Peça a **URL** (ex.: `git@github.com:usuario/projeto.git` ou `https://github.com/usuario/projeto.git`) e use-a quando ele a der.
3. Com a URL, rode o handoff **com `--remote <URL>`** — o `journey-init` (001) faz o `remote add` + push (**reusa**, não reimplementa).

> **FRONTEIRA FIRME (regra do owner):** o **Journey NUNCA cria o repo** nem **acessa a conta** do usuário — **só instrui e vincula**. Criar/automatizar é **desejo do usuário** (ele pode pedir ao IDE), **fora do escopo** do Journey, que é **neutro sobre acesso de escrita**.

**Falha honesta:** sem URL → segue **local-only** (oferece vincular depois), nada quebra. Push sem acesso → **reporta honestamente** (o projeto está local e íntegro; o push falhou — verifique o acesso ao repo), **sem vazar segredo**, **sem estado meio-feito**.

## 3. Validar que arrancou (reusa a validação da 001)

A 001 **valida o arranque** (Opening Handshake habilitado: `CLAUDE.md`/`HANDOVER.md`). Confirme que
arrancou. **Zero falso-sucesso** (SC-002): **nunca** declare entregue sem o init ter arrancado.

## 4. Falha → abortar limpo + reportar (clarify Q2)

Se o pull/init **falhar** ou a pasta for inválida: **detecta → explica → instrui**; **não deixe estado
meio-feito**; o usuário corrige e roda de novo. **Não finja prontidão.**

## 5. ENTREGAR no Warmup e PARAR

Aponte o usuário ao **ponto de partida da metodologia (Warmup/Foundation)** e **devolva o controle** às
**skills de fase EXISTENTES**. **A skill termina aqui.**

> **FRONTEIRA FIRME (costura com ATRITO-70):** **NÃO** ofereça "iniciar a próxima fase" — esse passo é
> do **padrão ATRITO-70** (§7 do blueprint `docs/plans/ATRITO-70-phase-chaining-blueprint.md`), **não**
> desta skill. Deixe o **gancho** (o ponto onde o ATRITO-70 plugará), mas **não o implemente aqui**
> (senão duplica a 1ª transição de fase).

## Fronteiras (o que NÃO fazer)

- **Não reimplementar fases** (orquestra 001/006/007 — anti-ATRITO-61).
- **Não oferecer próxima fase** (ATRITO-70).
- **Não sobrescrever** repo/pasta existente (guard) nem docs curados (ATRITO-71).
- **Sem segredo / sem acesso amplo**; credencial git local, só-URL.
- **Validação real (o init de fato rodando, o handoff conduzido) = manual** — esta skill é prompt; a
  mecânica reusada já é testada. **Não fabricar cobertura.**
