# Warmup — o estalo da ideia (e o Documento de Visão)

Warmup é a **fase 0**: ainda podes estar **sem** Journey instalada, ou acabaste de instalar e o agente entregou-te aqui. É o momento de perceber se a ideia **vale o esforço** de um projecto real.

Não há template obrigatório. Há, porém, um artefacto que vais precisar em breve: o **Documento de Visão**.

---

## O Documento de Visão — o que é

É o texto que responde, com honestidade:

- **Que problema** existe (para quem)?
- **O que vamos construir** (e o que **não** vamos)?
- **Como sabemos** que funcionou (critérios de sucesso)?
- Que restrições existem (tempo, stack preferida, conformidade, orçamento)?

No Journey, a versão **canónica versionada** no repo costuma viver em `docs/JOURNEY-VISION.md` — mas isso é entregável da **Discovery**, não um PDF perfeito no dia 1.

No Warmup trabalhas o **rascunho**: notas, conversas com IA, esboços, mockups.

---

## Por que importa tanto

Sem visão partilhável:

- a Foundation cria repo e estrutura **à volta de uma ideia ainda mole** → retrabalho;
- a Discovery vira conversa sem âncora;
- o agente inventa âmbito porque ninguém escreveu as fronteiras.

Com um rascunho claro (mesmo imperfeito):

- sabes dizer “ainda não estou pronto para Foundation”;
- na Discovery, o `/journey-discover` (e workshops) **consolidam** em vez de inventar do zero;
- mockups e testes com utilizadores têm um alvo.

---

## Como montar (prática)

1. **Problema em uma frase** — “Para [persona], o problema é…”  
2. **Promessa** — “A solução faz X; não faz Y.”  
3. **Persona** — quem sofre o problema (mesmo que sejas tu).  
4. **Cenário feliz** — 5–10 passos do utilizador.  
5. **Fora de âmbito** — lista explícita do que fica para depois.  
6. **Riscos** — o que pode matar a ideia.  
7. **Decisão de gate** — “Vale iniciar Foundation? Sim / Não / Ainda não.”

Guarda isto onde quiseres no Warmup (notas, markdown solto, chat exportado). Na Discovery, promove a `docs/JOURNEY-VISION.md`.

---

## Mockups e modelos para validar requisitos

Recomendação forte: **antes** de cravar stack e specs, **mostra** a ideia.

| Artefacto leve | Para quê |
|---|---|
| Wireframes (papel, Excalidraw, Figma rough) | Fluxos e ecrãs sem pixel-perfect |
| Protótipo clicável mínimo | Validar navegação com alguém real |
| Modelo de dados em caixas | Entidades e relações óbvias |
| “Fake door” / landing | Medir interesse sem construir o produto |

Usa-os para **perguntas**, não para fingir que o produto está pronto:

- “Isto resolve o teu problema?”  
- “O que falta nesta tela?”  
- “Onde desistirias?”

Se ninguém conseguir explicar o mockup em 60 segundos, a visão ainda está confusa — continua no Warmup.

---

## O que NÃO é Warmup

- Escolher framework e base de dados “a sério” (isso é **Discovery**).  
- Fechar Constituição completa.  
- Gerar todas as specs Spec Kit.

Warmup termina com uma decisão consciente: **seguir para Foundation** (instalar/confirmar Journey + repo) ou **parar / incubar mais**.

## Seguinte

→ [`01-foundation.md`](01-foundation.md)
