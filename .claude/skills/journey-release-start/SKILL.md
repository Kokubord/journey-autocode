---
name: "journey-release-start"
description: "Abre a fase Release: valida a versão semver, cria a branch release/<version>, atualiza a versão e gera RELEASE-NOTES-<version>.md (agrupado por tipo, linkando ADRs) a partir dos commits desde a última tag — sugere cutover-plan/runbook. Comando condutor mecânico (ADR-0017); core/open, git conduzido com gate humano."
argument-hint: "<version> (semver, ex.: v1.0.0)"
compatibility: "Requires a Journey project (git, docs/adr/, um pyproject.toml com [project].version) e o pacote journey-skill (journey-release-start CLI)."
metadata:
  author: "journey"
  source: "specs/009-journey-release-start"
  adr: "ADR-0017 (padrão condutor mecânico) + ADR-0005 (git conduzido, gate humano) + ADR-0008 (rota AutoCode)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-release-start <version>` — abrir a fase Release

Comando **condutor mecânico** (ADR-0017): a sua natureza é determinista, por isso esta skill é
**fina** — **conduz e gateia o git**, e **delega a mecânica** ao CLI `journey-release-start`. É
**core/open**: opera dentro do repositório, **sem serviço externo** (FR-007).

## O que fazer

1. **Pré-visualizar (sem mutação)** — mostre ao operador o que vai acontecer:
   ```
   journey-release-start preview <version> --repo-root .
   ```
   Devolve: a **versão atual → nova** e as **RELEASE-NOTES** que seriam geradas (commits desde a
   última tag, agrupados em *Features / Fixes / Decisões / Outros*, decisões a linkar `[ADR-NNNN]`).
   **Não escreve nada.** *(Sem tag ainda? É o caso normal da 1ª release — usa todo o histórico.)*

2. **Gate humano** (ADR-0005). Apresente o preview; **só com aprovação** prossiga — o passo
   seguinte **muta o repo** (cria branch, altera a versão, escreve ficheiro).

3. **Iniciar o release:**
   ```
   journey-release-start start <version> --repo-root .
   ```
   Cria `release/<version>`, atualiza a versão (`--version-file`, default `pyproject.toml` raiz) e
   escreve `RELEASE-NOTES-<version>.md`. **NÃO commita** — o git é conduzido; o **humano revê e
   commita** (ADR-0005).

4. **Sugerir** `cutover-plan`/`runbook` em `docs/release/` (US2).

## Fronteiras

- **`<version>` é semver** (ex.: `v1.0.0`, `v1.2.3-beta.1`); fora disso, o CLI rejeita.
- **Monorepo:** o bump toca **só o `--version-file` dado** (default raiz). A política de
  versionamento multi-pacote **não é cravada** aqui (project-specific).
- **FR-008 (cutover/deploy/staging) e FR-009 (`release/` × `feat/phase`) — DEFERIDOS** (fase
  Release não vivida); **não fabricar**.
- **Veto-UNC** (ADR-0004); **git conduzido com gate** (ADR-0005); **1 worktree por agente** se
  houver paralelismo (ADR-0019).
