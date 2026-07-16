---
name: "journey-retrospective"
description: "Conduz um workshop estruturado de retrospectiva ao fim de fase (Run, ou fim de sub-fase de Build grande): facilita as 4 secções (o que funcionou / não funcionou / lições / ADRs de aprendizado) a partir dos insumos REAIS versionados (Histórico de sessões, ADRs, incidentes) e escreve docs/retrospectives/NNN-<slug>.md. Princípio-raiz: lições ancoradas em fonte, propor-nunca-afirmar. Comando condutor judgment-heavy (ADR-0017); gate humano (ADR-0005)."
argument-hint: "[--since=YYYY-MM-DD] [--dry-run] (default 30 dias)"
compatibility: "Requires a Journey project (git, docs/adr/, HANDOVER com Closing blocks) e o pacote journey-skill (journey-retrospective CLI)."
metadata:
  author: "journey"
  source: "specs/013-journey-retrospective"
  adr: "ATRITO-32 (anchored-in-source) + ADR-0017 (padrão condutor) + ADR-0005 (git conduzido, gate)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-retrospective` — workshop estruturado de retrospectiva

Comando **condutor judgment-heavy** (ADR-0017): o **julgamento é teu** (o que funcionou, o que não,
que lições ficam, que aprendizados merecem virar ADR). Esta skill é **grossa** — conduz o workshop;
a mecânica é **fina e local** (`journey-retrospective read-context`/`record`/`propose-adr`).
**Princípio-raiz (ATRITO-32): lição só de fonte citável — propor, nunca afirmar.**

> **Nunca fabricar.** Cada item das 4 secções **cita a origem** (Closing block, ADR, atrito, sha de
> commit). Onde não há fonte, **não inventes** — omite ou marca incerto. Métricas operacionais
> (FR-006) ficam **«pendente»** (o pipeline de tokens, ADR-0010, não existe); nunca um número falso.

## Quando rodar

Ao **final de fase**: Run (o projeto inteiro) ou o **fim de uma sub-fase de Build grande** (FR-001).
O mesmo comando serve aos dois — só muda o escopo que tu defines.

## O que fazer

1. **Ler o contexto (local, sem escrever):**
   ```
   journey-retrospective read-context --since=YYYY-MM-DD --repo-root .
   ```
   Devolve os insumos **versionados** da fase: os **Closing blocks** do Histórico (fase/subfase/ADRs
   criados), o **índice de ADRs**, e os **commits** do período (default 30 dias). As métricas vêm
   marcadas **«pendente»** (FR-006) — não as preenchas à mão.

2. **Conduzir o workshop (o teu trabalho):** a partir dos insumos REAIS, facilita as **4 secções**.
   Para cada observação, autora um item **com a sua fonte**:
   - **O que funcionou** · **O que não funcionou** · **Lições aprendidas** · **ADRs de aprendizado**;
   - cada item = `{text, source}` — `source` **obrigatório** (sha, ADR-NNNN, atrito, spec);
   - sem fonte, **não há item** (anchored-in-source, FR-002).

3. **Pré-visualizar o documento (não escreve):**
   ```
   journey-retrospective record --payload <retro.json> --dry-run --repo-root .
   ```
   Mostra a `docs/retrospectives/NNN-<slug>.md` (nº sequencial seguinte; 1ª = `001`) com as 4 secções.

4. **Sugerir ADRs de aprendizado** (FR-004) — opcional, reusa a `RetroProposal` da arqueologia:
   ```
   journey-retrospective propose-adr --payload <proposta.json> --dry-run --repo-root .
   ```
   `sources` **obrigatório**; `uncertain: true` quando a fonte não basta — marca, não inventa.

5. **Gate humano** (ADR-0005, Constituição §6.4). Só com aprovação explícita, escreve:
   ```
   journey-retrospective record --payload <retro.json> --repo-root .          # escreve o doc
   journey-retrospective propose-adr --payload <proposta.json> --repo-root .  # draft do ADR (Proposto)
   ```
   `docs/retrospectives/` é **versionado (tracked)** — registo permanente de aprendizado. **Nunca
   commitar automaticamente** — o humano revê e commita.

## Fronteiras (o que NÃO fazer)

- **Ancorar em fonte, nunca afirmar** — sem origem citável, não há item nem proposta (FR-002, ATRITO-32).
- **FR-006 (métricas operacionais) DEFERIDO** — dependem do `/journey-report` (011) + pipeline de
  tokens (ADR-0010), **não construídos**. Exibe «pendente», nunca um número. **Não construir a coleta.**
- **FR-007 (facilitação fina + registro de incidentes `docs/incidents/`) DEFERIDO** — fase Run não
  vivida; o comando criador de incidentes não está nesta spec. Se te vires a desenhar isto, **pára**.
- **Core/open** (FR-005) — opera no repositório, sem serviço externo, sem flag Enterprise.
- **Veto-UNC** (ADR-0004); git conduzido com gate (ADR-0005); 1 worktree por agente se paralelo (ADR-0019).
