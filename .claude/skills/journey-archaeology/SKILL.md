---
name: "journey-archaeology"
description: "Destilação retrospectiva de decisões: vasculha git log do período, specs antigas (e PRs via gh, se disponível) e PROPÕE ADRs retroativos + entradas de histórico para aprovação humana. Princípio-raiz: propor, nunca afirmar — marca incerteza, nunca fabrica justificativa. Comando condutor judgment-heavy (ADR-0017); --dry-run + gate humano (ATRITO-32, ADR-0005)."
argument-hint: "[--since=YYYY-MM-DD] [--dry-run] (default 30 dias)"
compatibility: "Requires a Journey project (git, docs/adr/, HANDOVER com «Histórico da arqueologia») e o pacote journey-skill (journey-archaeology CLI)."
metadata:
  author: "journey"
  source: "specs/003-journey-archaeology"
  adr: "ATRITO-32 (propor-nunca-afirmar) + ADR-0017 (padrão condutor) + ADR-0005 (git conduzido, gate)"
user-invocable: true
disable-model-invocation: false
---

# `/journey-archaeology` — destilação retrospectiva de decisões

Comando **condutor judgment-heavy** (ADR-0017): o **julgamento é teu** (que decisões antigas são
materiais, o que o ADR diz, o que é incerto). Esta skill é **grossa** — conduz; a mecânica é
**fina e local** (`journey-archaeology read-context`/`propose-adr`/`record`). **Princípio-raiz
(ATRITO-32): propor, nunca afirmar.**

> **Nunca fabricar.** Onde a fonte não sustenta o *porquê* de uma decisão antiga, **marca incerto e
> pede confirmação** — não inventes contexto. Toda proposta **cita as fontes** que a ancoram.

## O que fazer

1. **Ler o contexto (local, sem escrever):**
   ```
   journey-archaeology read-context --since=YYYY-MM-DD --repo-root .
   ```
   Devolve os commits do período (default 30 dias) + as specs antigas. *(Comentários de PR são
   enriquecimento opcional: lê via `gh` **se** disponível; senão, omite honestamente — não fabriques.)*

2. **Julgar (o teu trabalho):** das fontes, identifica **decisões materiais** que nunca viraram ADR
   (escolha com trade-off, pivot, contrato, convenção). Para cada uma, **autora uma `RetroProposal`**:
   - o `Adr` (status **Proposto**), com a **nota canónica** no contexto: *"ADR criado
     retroativamente em YYYY-MM-DD após auditoria"* (a data é a da **auditoria**, não a da decisão);
   - `sources`: **as evidências** (sha do commit, spec, PR) — **obrigatório**; sem fonte, não há proposta;
   - `uncertain: true` quando a fonte **não** basta para reconstruir o porquê.

3. **Pré-visualizar cada proposta (não escreve):**
   ```
   journey-archaeology propose-adr --payload <proposta.json> --dry-run --repo-root .
   ```
   Mostra o ADR proposto (nº livre seguinte) + as fontes + a marca `[INCERTO]` se for o caso.

4. **Gate humano** (ADR-0005, Constituição §6.4). Só com aprovação explícita:
   ```
   journey-archaeology propose-adr --payload <proposta.json> --repo-root .   # escreve o draft (Proposto)
   journey-archaeology record --scope "<período/tema>" --author <a> --sources "<…>" --repo-root .
   ```
   `record` regista a operação em «Histórico da arqueologia» (data+escopo+autor). **Nunca commitar
   automaticamente** — o humano revê e commita.

## Fronteiras (o que NÃO fazer)

- **Propor, nunca afirmar** — sem fonte citável, não há proposta; incerteza → marca, não inventa (FR-007).
- **Não-destrutivo** (FR-006): ADRs retroativos recebem o **próximo número livre**; nunca reescrever
  ADRs/HANDOVER/commits existentes.
- **US3 (FR-011/012/013) DEFERIDA** — heurística automática de deteção, retrofit de legado e
  projeto-sem-convenção **não estão desenhados**; o retrofit pertence ao **init/Lite** (spec 001 FR-017).
  Se te vires a desenhar isto, **pára**.
- **Veto-UNC** (ADR-0004); git conduzido com gate (ADR-0005); 1 worktree por agente se paralelo (ADR-0019).
