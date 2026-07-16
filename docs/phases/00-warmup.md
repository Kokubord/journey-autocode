# Warmup — o estalo da ideia (e o Documento de Visão)

Warmup é a **fase 0**: podes estar **sem** Journey instalada ou ter instalado primeiro e voltado
para amadurecer a ideia. É o momento de perceber se a solução vale o esforço e se os requisitos
resistem a perguntas reais.

Não há template obrigatório nem bloqueio. É possível seguir só com um prompt contendo problema e
proposta de solução. Mas isso deixa hipóteses pouco testadas, reduz a confiança do plano e aumenta o
risco de retrabalho. O **Documento de Visão** é o gate de qualidade recomendado — não uma autorização
burocrática (ADR-0056).

---

## O Documento de Visão — o que é

É o texto que responde, com honestidade:

- **Que problema** existe (para quem)?
- Que **evidência** temos — e o que ainda é apenas hipótese?
- **O que vamos construir** (e o que **não** vamos)?
- Como a pessoa percorre os **fluxos principais**?
- Que regras e restrições mudam a solução?
- **Como sabemos** que funcionou (critérios de sucesso)?
- Quais riscos, decisões abertas e perguntas precisam de validação?

No Journey, a versão **canónica versionada** no repo vive em `docs/JOURNEY-VISION.md` — mas essa
consolidação é entregável da **Discovery**, não um PDF perfeito no dia 1.

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
2. **Fatos × hipóteses** — marque o que observaste e o que ainda precisas testar.
3. **Promessa** — “A solução faz X; não faz Y.”
4. **Personas e stakeholders** — quem usa, decide, paga, opera ou é afetado.
5. **Cenário feliz** — 5–10 passos do utilizador, do gatilho ao resultado.
6. **Exceções importantes** — cancelamento, falha, atraso, permissão, dados ausentes.
7. **Fora de âmbito** — lista explícita do que fica para depois.
8. **Regras e restrições** — negócio, privacidade, acessibilidade, orçamento e prazo.
9. **Mockups** — telas suficientes para testar o fluxo, sem pixel-perfect.
10. **Sucesso e riscos** — como medir valor; o que pode matar a ideia.
11. **Decisão de gate** — avançar, amadurecer mais ou parar.

Guarda isto onde quiseres no Warmup (notas, markdown solto, chat exportado). Na Discovery, promove a `docs/JOURNEY-VISION.md`.

---

## Roteiro de levantamento com usuários

Não uses entrevistas para vender a tua ideia. Usa-as para procurar evidência que possa contrariá-la.

1. **Escolhe perfis relevantes**, não apenas amigos: usuário principal, operador e quem decide/paga.
2. **Pergunta pelo passado**, não por promessas: “Conte a última vez em que isto aconteceu”.
3. **Observa o processo atual**: ferramentas, atalhos, esperas, erros e pessoas envolvidas.
4. **Mostra o fluxo ou mockup sem explicar demais** e pede que a pessoa diga o que faria.
5. **Registra evidência separada de interpretação**: citação/observação → hipótese → impacto.
6. **Procura padrões e divergências**. Uma opinião isolada não vira requisito universal.
7. **Atualiza visão e mockup**; volta a testar as mudanças de maior risco.

Perguntas úteis:

- “Qual foi a última situação real? O que aconteceu passo a passo?”
- “Como resolves isso hoje? O que custa tempo, dinheiro ou confiança?”
- “Quem mais participa ou precisa aprovar?”
- “O que faria você abandonar este fluxo?”
- “O que está faltando ou parece desnecessário nesta tela?”
- “Que informação seria sensível ou não poderia estar aqui?”

Não existe número mágico de entrevistas. A amostra deve ser proporcional ao risco e incluir perfis
distintos até os padrões principais se repetirem — documenta também as divergências.

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

## Checklist de prontidão

Marca com honestidade:

- [ ] O problema está descrito sem depender da solução proposta.
- [ ] Fatos observados estão separados de hipóteses.
- [ ] Usuário, operador, decisor e afetados foram considerados.
- [ ] O fluxo principal e as exceções críticas estão visíveis.
- [ ] O MVP e o fora de âmbito cabem numa frase cada.
- [ ] Regras sensíveis, privacidade e acessibilidade foram levantadas.
- [ ] Mockups foram usados para fazer perguntas a pessoas relevantes.
- [ ] Critérios de sucesso medem resultado, não apenas entregas.
- [ ] Riscos e decisões abertas têm próximo passo.
- [ ] Existe uma decisão consciente: avançar, amadurecer ou parar.

Se vários itens faltarem, ainda podes avançar — mas registra a ressalva: **baixa confiança nos
requisitos; maior risco de retrabalho**.

## Exemplo preenchido: MesaPronta

Consulta um aplicativo fictício de reservas e fila para pequenos restaurantes:

- [Documento de Visão de referência](../examples/mesa-pronta-vision.md)
- [Fluxo mobile do cliente](../examples/mesa-pronta-customer-flow.svg)
- [Painel web do restaurante](../examples/mesa-pronta-operator-dashboard.svg)

O exemplo mostra profundidade e rastreabilidade, não um formulário para copiar. Adapta a estrutura ao
risco e ao tamanho da tua solução.

---

## O que NÃO é Warmup

- Escolher framework e base de dados “a sério” (isso é **Discovery**).
- Fechar Constituição completa.
- Gerar todas as specs Spec Kit.

Warmup termina com uma decisão consciente:

- **Avançar:** instalar/confirmar Journey, ou iniciar Discovery se já instalaste.
- **Amadurecer:** continuar entrevistas, fluxos e mockups.
- **Parar:** descartar ou incubar a ideia sem custo afundado.

## Seguinte

→ [`01-foundation.md`](01-foundation.md)
