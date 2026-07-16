# MesaPronta — Documento de Visão fictício

> **REFERÊNCIA NÃO PRESCRITIVA — EXEMPLO FICTÍCIO**
>
> Este documento demonstra como amadurecer a visão de um produto antes da
> especificação e implementação. **Não é template obrigatório, não define um padrão universal
> e não comprova demanda real.** MesaPronta, seus estabelecimentos, números, personas e cenários são
> inventados para fins didáticos. Onde ainda não existe evidência, o texto usa explicitamente
> **hipótese**, **suposição**, **meta proposta** ou **decisão em aberto**.
>
> O exemplo não fixa linguagem, framework, banco de dados, provedor, arquitetura de implantação ou
> qualquer outra escolha de stack. Essas decisões pertencem ao planejamento técnico posterior.

| Campo | Valor |
|---|---|
| Produto fictício | MesaPronta |
| Categoria | Reservas e fila de espera para pequenos restaurantes |
| Superfícies | Experiência mobile do cliente e painel web do operador |
| Versão deste exemplo | 1.0 |
| Estado | Visão para validação; não aprovada para construção |
| Idioma | Português brasileiro |
| Evidência primária disponível | Nenhuma; somente hipóteses a testar |
| Decisão de gate atual | **Amadurecer**, até executar o levantamento mínimo |

---

## Como usar este exemplo

Leia este arquivo como demonstração, não como uma lista que todo projeto precisa copiar. O valor
está no raciocínio: distinguir observação de opinião, conectar problema a requisito, declarar
limites e explicitar o que ainda precisa ser descoberto.

Uma equipe pode usá-lo de quatro maneiras:

1. **Como referência de profundidade:** comparar se problema, público, escopo e critérios de sucesso
   estão claros o bastante para uma conversa de Discovery.
2. **Como provocação:** adaptar perguntas e riscos ao próprio domínio, descartando tudo que não se
   aplica.
3. **Como mapa de lacunas:** marcar quais afirmações têm evidência, quais são hipóteses e quais
   dependem de decisão.
4. **Como exemplo de rastreabilidade:** observar como requisitos, fluxos e telas se conectam sem
   antecipar a implementação técnica.

Este documento não prova que usuários foram ouvidos. Até entrevistas, observações ou testes serem
executados e registrados, conclusões sobre comportamento permanecem hipóteses. Avançar ainda é
possível, desde que a incerteza e o risco de retrabalho sejam assumidos.

Dois mockups complementares serão produzidos separadamente:

- [Fluxo mobile do cliente](mesa-pronta-customer-flow.svg)
- [Painel web do operador](mesa-pronta-operator-dashboard.svg)

Os mockups ilustram hipóteses; não substituem pesquisa ou especificação.

---

## 1. Identidade e sumário executivo

### 1.1 Identidade

**MesaPronta** é um produto fictício para pequenos restaurantes que desejam organizar reservas e
fila de espera sem depender de cadernos, mensagens espalhadas e memória da equipe. Para o cliente,
oferece uma experiência mobile para consultar disponibilidade, solicitar reserva, entrar na fila,
acompanhar posição estimada e confirmar presença. Para o operador, oferece um painel web para
visualizar o salão, administrar reservas e fila e registrar eventos do atendimento.

O recorte inicial considera restaurantes com uma unidade, salão e equipe enxuta. O MVP não
substitui caixa, comandas, delivery, contabilidade ou gestão completa.

### 1.2 Sumário executivo

Pequenos restaurantes podem receber pedidos de reserva por telefone, redes sociais e aplicativos de
mensagem, enquanto controlam mesas e espera em papel ou planilhas. A hipótese central é que essa
fragmentação aumenta conflitos de horário, reduz a previsibilidade para clientes e sobrecarrega
quem recebe o público. MesaPronta propõe uma fonte operacional única, simples o suficiente para ser
usada durante o pico.

O MVP conecta três capacidades: agenda de reservas, fila de espera e visão operacional das mesas.
O cliente inicia e acompanha sua própria solicitação; o operador mantém controle para aceitar,
ajustar, acomodar ou cancelar. Estimativas de espera são comunicadas como estimativas, nunca como
garantias. Toda alteração relevante deve deixar um registro básico para que a equipe entenda o que
aconteceu.

Antes de construir, é preciso confirmar a frequência do problema, adoção no pico, aceitação do canal
mobile e fricção da coleta mínima.

---

## 2. Problema, fatos e hipóteses

### 2.1 Formulação do problema

Quando reservas, fila e ocupação são administradas em canais diferentes, o restaurante pode perder
a visão do compromisso assumido com cada cliente. Para o operador, isso pode significar retrabalho,
interrupções e decisões tomadas com informação incompleta. Para o cliente, pode significar espera
incerta, necessidade de perguntar repetidamente e frustração quando a expectativa não corresponde à
realidade.

A oportunidade imaginada é criar uma coordenação compartilhada sem exigir uma transformação ampla
da operação. A solução só terá valor se for mais rápida que o método atual nos momentos críticos.

### 2.2 O que é fato neste exemplo

Os únicos fatos afirmados por este documento são:

- MesaPronta é um produto inventado para fins didáticos.
- Nenhuma entrevista, observação em restaurante, análise de dados ou validação comercial foi
  realizada para este exemplo.
- Reservas, fila de espera e ocupação são processos distintos e relacionados que precisam ser
  modelados sem tratá-los como sinônimos.
- Os dois mockups citados serão artefatos separados e, por si só, não constituem evidência.

Não são tratados como fatos números de mercado, taxas de ausência, duração média de espera,
preferência de canal, disposição a pagar ou produtividade da equipe.

### 2.3 Hipóteses de problema

| ID | Hipótese a testar | Evidência necessária | Sinal que enfraquece |
|---|---|---|---|
| HYP-001 | O controle fragmentado causa erros ou retrabalho semanalmente | Relatos com episódios recentes e observação do processo | Problema raro ou já resolvido de forma satisfatória |
| HYP-002 | A incerteza da espera gera contatos repetidos e abandono | Registro de perguntas, desistências e percepção de clientes | Clientes não valorizam acompanhamento |
| HYP-003 | Um painel único reduz carga cognitiva no pico | Teste de tarefa e piloto comparativo | Operação digital demora mais que papel |
| HYP-004 | Clientes aceitam informar poucos dados pelo celular | Teste de protótipo e taxa de conclusão | Abandono alto antes da confirmação |
| HYP-005 | Restaurantes pequenos pagariam por simplicidade e redução de falhas | Entrevistas de compra e teste de oferta | Interesse sem compromisso ou orçamento |
| HYP-006 | Uma estimativa em faixa é mais confiável que um horário exato | Teste de compreensão e operação piloto | Faixa confunde ou não reduz ansiedade |

### 2.4 Hipóteses de solução

- Uma página mobile sem instalação obrigatória tende a reduzir barreira para o cliente.
- O operador precisa enxergar “agora e próximos 90 minutos” antes de relatórios históricos.
- Inserir uma pessoa na fila deve levar poucos passos e aceitar ação assistida pelo operador.
- A equipe precisa poder corrigir dados, mas correções relevantes devem ser rastreáveis.
- Notificações podem reduzir perguntas e ausências, desde que haja consentimento e conteúdo claro.
- Configurar regras de capacidade por tamanho de grupo pode ser suficiente no MVP; otimização
  automática avançada provavelmente é prematura.

Essas proposições são candidatas a teste, não compromissos de produto.

---

## 3. Objetivos, não objetivos e princípios

### 3.1 Objetivos do MVP

1. Dar ao operador uma visão única das reservas, da fila e do estado atual das mesas.
2. Permitir que clientes solicitem e acompanhem reserva ou espera com pouca fricção.
3. Reduzir ambiguidades por meio de estados explícitos, horários registrados e comunicação clara.
4. Ajudar a equipe a tomar decisões operacionais sem retirar seu controle.
5. Produzir dados mínimos para avaliar demanda, espera, comparecimento e uso do fluxo.
6. Proteger dados pessoais com coleta mínima, propósito explícito e retenção definida.

### 3.2 Não objetivos

- Automatizar integralmente a alocação de mesas.
- Garantir horário exato de acomodação.
- Substituir julgamento do anfitrião ou gerente.
- Gerenciar pedidos, comandas, pagamentos, estoque, delivery ou cozinha.
- Criar marketplace de descoberta de restaurantes.
- Oferecer programa de fidelidade, avaliações públicas ou campanhas de marketing.
- Atender redes complexas, franquias ou múltiplas unidades no MVP.
- Definir stack, topologia de infraestrutura ou fornecedor neste documento.

### 3.3 Princípios orientadores

- **Operação primeiro:** no pico, a ação principal deve ser evidente e rápida.
- **Estimativa honesta:** comunicar intervalo e incerteza; nunca prometer o que o salão não controla.
- **Controle humano:** sugestões apoiam o operador, que decide acomodação e exceções.
- **Uma fonte operacional:** o estado visível precisa refletir a última ação válida.
- **Coleta mínima:** pedir somente dados necessários ao atendimento e à comunicação consentida.
- **Acessibilidade prática:** linguagem simples, contraste adequado e operação por teclado no painel.
- **Falha recuperável:** ações equivocadas devem poder ser corrigidas sem apagar o histórico.
- **Sem evidência fabricada:** métricas e depoimentos só entram após coleta real.

---

## 4. Personas e stakeholders

As personas abaixo são **proto-personas**: sínteses hipotéticas usadas para orientar pesquisa. Não
representam segmentos confirmados.

### 4.1 Cliente planejador — Camila

Quer reservar para um pequeno grupo e saber se o pedido foi aceito. Usa o celular, evita ligações e
valoriza confirmação objetiva. Pode desistir se o formulário for longo ou se “solicitação” parecer
“reserva garantida”. Necessita alterar quantidade de pessoas ou cancelar com facilidade.

### 4.2 Cliente espontâneo — Rafael

Chega sem reserva ou decide ir em cima da hora. Aceita entrar na fila se compreender a faixa de
espera e puder acompanhar sem permanecer fisicamente na porta. Pode estar com bateria baixa,
conexão instável ou pressa.

### 4.3 Anfitriã ou atendente — Joana

Recebe clientes, telefone e mensagens ao mesmo tempo. Precisa registrar um grupo em segundos,
visualizar prioridades e corrigir exceções. Seu critério de sucesso não é “ter mais recursos”, mas
evitar que a ferramenta vire outra tarefa durante o pico.

### 4.4 Gerente-proprietário — Marcos

Configura horários, capacidade e políticas; cobre diferentes funções no restaurante. Quer reduzir
falhas e entender padrões básicos sem implantar um sistema pesado. Decide compra, acompanha adoção e
responde por privacidade e treinamento.

### 4.5 Stakeholders secundários

- **Equipe de salão:** informa quando mesas ficam disponíveis e depende de uma ocupação atualizada.
- **Responsável por privacidade ou jurídico, quando houver:** valida consentimento, retenção e
  atendimento a direitos do titular.
- **Suporte do produto:** precisa diagnosticar divergências sem acessar dados além do necessário.
- **Financeiro do restaurante:** avalia custo e retorno, mas não opera o fluxo diário.
- **Pessoas com deficiência e acompanhantes:** precisam participar dos testes para que barreiras não
  sejam descobertas somente após o lançamento.

### 4.6 Tensões entre interesses

O cliente deseja certeza, mas o operador oferece previsão. O gerente pode desejar dados, enquanto
privacidade pede minimização. Automação também precisa conviver com exceções e controle humano.

---

## 5. Roteiro realista de levantamento com usuários

### 5.1 Objetivo da coleta

Entender o processo atual, a frequência e o impacto dos problemas, as diferenças entre horários
calmos e picos, a linguagem usada por clientes e operadores e a disposição para mudar. A coleta não
serve para pedir que participantes desenhem a solução nem para confirmar a ideia do time.

### 5.2 Amostragem proposta

Uma rodada inicial pode envolver **20 participantes**, distribuídos proporcionalmente entre quem
opera e quem vivencia o atendimento:

- 4 proprietários ou gerentes de restaurantes pequenos (20%);
- 6 anfitriões, atendentes ou líderes de salão (30%);
- 8 clientes que reservaram ou aguardaram mesa nos últimos três meses (40%);
- 2 clientes com necessidades de acessibilidade relevantes ao fluxo (10%).

Buscar variedade de cidade, faixa de preço, salão, política de reservas, período e familiaridade
digital. Evitar somente conhecidos ou entusiastas de tecnologia. A amostra é exploratória, sem
generalização estatística.

Além das entrevistas, propor **quatro sessões de observação contextual** de 60 a 90 minutos: duas em
período calmo e duas em pico, em pelo menos dois estabelecimentos. Observar sem registrar dados
pessoais de clientes e somente com autorização do estabelecimento.

### 5.3 Perguntas para operadores

Começar por episódios reais e recentes:

1. Conte sobre a última noite em que houve fila. O que aconteceu do primeiro nome até a acomodação?
2. Onde entram pedidos de reserva hoje? Quem consolida e em que momento?
3. Qual foi o erro ou retrabalho mais recente? Como perceberam e como corrigiram?
4. O que muda entre um horário calmo e o pico?
5. Como estimam espera? Quais fatores tornam a estimativa errada?
6. Como tratam atraso, ausência, mudança no tamanho do grupo e preferência de mesa?
7. O que precisa estar visível de relance? O que pode ficar para depois?
8. Em quais momentos papel, mensagem ou planilha funciona melhor que uma ferramenta digital?
9. Quem poderia editar configurações e quem apenas operar?
10. Que informação vocês não gostariam de coletar ou armazenar?
11. Quanto tempo de treinamento seria aceitável? Como uma nova pessoa aprende hoje?
12. Que resultado justificaria pagar por uma solução? Como seria medido?

Evitar perguntas como “você usaria este aplicativo?” sem contexto. Preferir “mostre como fez da
última vez” e “o que aconteceu depois”.

### 5.4 Perguntas para clientes

1. Pense na última vez em que reservou ou esperou por uma mesa. Como escolheu o canal?
2. Em que momento você considerou que a reserva estava confirmada?
3. Que informação faltou enquanto aguardava?
4. Você entrou em contato novamente? Por quê?
5. O que faria você abandonar um formulário de reserva?
6. Como prefere receber uma atualização urgente? Em quais condições aceitaria notificações?
7. Como interpreta “20–30 minutos de espera”? O que espera que aconteça se a faixa mudar?
8. Que alterações gostaria de fazer sem telefonar?
9. Há alguma barreira de visão, mobilidade, linguagem, conectividade ou privacidade nesse processo?
10. O que seria uma experiência ruim mesmo que a mesa fosse liberada no fim?

### 5.5 Registro de evidências

Cada sessão registra: código do participante, papel, recrutamento, data, contexto, consentimento,
perguntas, notas literais, observações, artefatos autorizados e interpretação separada. Não registrar
nomes nem fotografar telas, cadernos ou pessoas sem consentimento.

Usar três camadas:

- **Evidência:** fala literal anonimizada, comportamento observado ou dado fornecido.
- **Interpretação:** leitura do pesquisador, marcada como tal.
- **Implicação candidata:** possível efeito no produto, ainda sujeita a triangulação.

Uma matriz de síntese deve ligar cada achado aos participantes que o sustentam e também registrar
contraexemplos. Nenhuma resposta deve ser inventada para “preencher” este documento. Após a coleta,
atualizar HYP-001 a HYP-006 como sustentada, enfraquecida ou inconclusiva.

### 5.6 Critérios para encerrar a rodada

A rodada não termina apenas por atingir 20 entrevistas. Encerrar quando houver cobertura dos perfis,
observação de pelo menos dois contextos operacionais, registro de divergências e informação
suficiente para decidir o gate. Se surgirem segmentos com processos muito diferentes, ampliar a
amostra ou reduzir o ICP do MVP.

---

## 6. Cenários e jornadas

### 6.1 Jornada A — reserva planejada

Camila abre o link do restaurante, escolhe data, faixa de horário e tamanho do grupo. O sistema
informa se está recebendo solicitações e deixa claro se a confirmação é imediata ou depende do
operador. Ela fornece nome, contato e eventual necessidade de acessibilidade, aceita o uso dos dados
para aquele atendimento e envia. Recebe um resumo com estado “solicitada”. Após análise, o
restaurante confirma, propõe outro horário ou recusa com mensagem objetiva. Antes do horário,
Camila pode confirmar presença, alterar dentro das regras ou cancelar.

**Momento crítico:** não confundir envio da solicitação com reserva confirmada.

### 6.2 Jornada B — entrada remota na fila

Rafael consulta o restaurante e vê que há espera estimada de 25–40 minutos para duas pessoas. Entra
na fila, recebe posição aproximada e um código/link de acompanhamento. A faixa muda quando a
operação registra novas informações. Ao se aproximar a vez, recebe convite para confirmar que ainda
vai comparecer. Quando chamado, vê quanto tempo tem para se apresentar.

**Momento crítico:** posição e tempo são aproximados; prioridades e mesas compatíveis podem alterar
a ordem aparente.

### 6.3 Jornada C — chegada sem cadastro prévio

Joana recebe um grupo na porta. Pergunta nome, quantidade e forma de contato opcional ou necessária
conforme a política validada. Registra a entrada assistida, informa a faixa de espera e entrega um
meio de acompanhamento. Se o cliente não puder usar celular, Joana mantém o atendimento no painel e
combina chamada presencial.

**Momento crítico:** o produto não pode excluir quem não tem smartphone ou conectividade.

### 6.4 Jornada D — acomodação e liberação

Uma mesa é marcada como disponível. O painel mostra grupos compatíveis sem decidir automaticamente.
Joana escolhe o grupo, registra “chamado” e depois “acomodado”. A reserva ou entrada de fila é
encerrada, e a mesa passa a ocupada. Quando o salão informa a saída, Joana libera a mesa. Correções
ficam no histórico operacional.

**Momento crítico:** evitar dupla acomodação e estados contraditórios.

### 6.5 Jornada E — exceção

Um grupo confirmado atrasa e aumenta de quatro para seis pessoas. Joana visualiza a política,
registra a alteração e decide manter, replanejar ou cancelar. O cliente recebe o novo estado e uma
explicação curta. O sistema não força uma solução automática incompatível com o salão.

---

## 7. Proposta de valor

### Para o restaurante

Uma visão compartilhada do atendimento, desenhada para decisões rápidas: quem reservou, quem espera,
qual mesa pode ser liberada e o que mudou. O valor esperado é menos coordenação manual, menos
ambiguidade e dados operacionais básicos sem substituir os sistemas centrais do restaurante.

### Para o cliente

Um caminho claro para solicitar, acompanhar e alterar sua intenção sem ligações repetidas. O valor
esperado é previsibilidade honesta e autonomia, não promessa de espera zero.

### Diferencial a validar

O diferencial hipotético é combinar reserva, fila e ocupação com leveza, controle humano e
incerteza explícita.

---

## 8. Escopo por horizontes

### 8.1 MVP — provar coordenação operacional

- Cadastro de um estabelecimento e suas configurações essenciais.
- Horários de atendimento e regras básicas de reserva/fila.
- Cadastro conceitual de mesas com capacidade e estado.
- Solicitação, confirmação, alteração permitida e cancelamento de reserva.
- Entrada na fila pelo cliente ou pelo operador.
- Estimativa em faixa, posição aproximada e estados da espera.
- Painel “agora e próximos” com reservas, fila e mesas.
- Ações de chamar, acomodar, marcar ausência, cancelar e liberar mesa.
- Notificações transacionais essenciais, com consentimento quando aplicável.
- Histórico operacional básico e métricas agregadas mínimas.
- Fluxos alternativos para clientes sem smartphone.

### 8.2 Horizonte seguinte — eficiência e aprendizado

- Regras de disponibilidade mais refinadas por área, combinação de mesas e duração esperada.
- Lista de clientes recorrentes com controles de privacidade.
- Relatórios de comparecimento, espera e utilização.
- Integração com canais externos, somente após validar demanda e confiabilidade.
- Lista de espera para datas futuras e confirmação antecipada.
- Permissões mais granulares e múltiplos turnos.

### 8.3 Horizonte futuro — expansão condicionada

- Múltiplas unidades.
- Recomendações operacionais baseadas em histórico, sempre explicáveis e sob controle humano.
- Integrações com sistemas de gestão do restaurante.
- Recursos comerciais avançados e experiências de descoberta.

Horizontes não são promessas; expansões dependem de evidência e riscos.

### 8.4 Fora de escopo explícito

No MVP ficam fora: pedidos e cardápio, pagamento, caixa, entrega, estoque, gestão de funcionários,
avaliações públicas, publicidade, clube de benefícios, venda de dados, precificação dinâmica,
reconhecimento facial, localização contínua do cliente e decisão totalmente automática sobre quem
será acomodado.

---

## 9. Regras de negócio candidatas

Estas regras são propostas iniciais e precisam ser validadas.

- **BR-001 — Estados de reserva:** solicitada, confirmada, alteração pendente, cancelada, concluída,
  ausência. Transições inválidas devem ser impedidas ou tratadas como correção explícita.
- **BR-002 — Confirmação inequívoca:** uma solicitação só é reserva confirmada quando o estado
  “confirmada” é comunicado ao cliente.
- **BR-003 — Capacidade:** o tamanho do grupo deve caber em uma mesa ou combinação permitida pela
  configuração; o operador pode registrar exceção justificada.
- **BR-004 — Espera estimada:** exibir faixa, horário da última atualização e linguagem de
  incerteza. Não apresentar garantia.
- **BR-005 — Ordem da fila:** usar chegada como referência, mas permitir compatibilidade de mesa,
  acessibilidade e exceções operacionais transparentes. O painel deve indicar quando a ordem não é
  estritamente sequencial.
- **BR-006 — Chamada:** ao ser chamado, o grupo recebe uma janela configurável para se apresentar.
  Expirada a janela, o operador decide chamar novamente, devolver à fila ou marcar ausência.
- **BR-007 — Idempotência operacional:** repetir uma ação por falha de conexão não pode criar duas
  reservas, duas entradas ou duas acomodações.
- **BR-008 — Uma acomodação ativa:** um grupo não pode estar simultaneamente acomodado em duas mesas,
  nem uma mesa atender dois grupos ativos sem configuração explícita.
- **BR-009 — Alterações:** mudanças de data, horário ou tamanho podem exigir nova confirmação quando
  afetarem disponibilidade.
- **BR-010 — Cancelamento:** cliente e operador podem cancelar conforme política visível; o motivo
  do cliente é opcional.
- **BR-011 — Dados mínimos:** coletar nome de chamada, tamanho do grupo e dados necessários para
  retorno. Necessidades de acessibilidade são opcionais e tratadas com cuidado.
- **BR-012 — Retenção:** dados identificáveis devem ter prazo e finalidade definidos antes do
  piloto; agregados não devem permitir reidentificação.
- **BR-013 — Auditoria:** mudança de estado registra momento, origem da ação e ator quando aplicável.
- **BR-014 — Operação degradada:** se o canal do cliente estiver indisponível, o operador mantém um
  caminho manual e reconcilia depois sem inventar eventos.

---

## 10. Modelo de domínio conceitual

O modelo descreve conceitos do negócio, não tabelas ou serviços.

- **Estabelecimento:** restaurante que define políticas, horários e capacidade.
- **Usuário operador:** pessoa autorizada a operar ou administrar o estabelecimento.
- **Área do salão:** agrupamento opcional de mesas, como interno ou varanda.
- **Mesa:** recurso físico com capacidade e estado operacional.
- **Combinação de mesas:** configuração que permite atender grupos maiores.
- **Cliente de atendimento:** identidade mínima usada numa reserva ou entrada de fila; não pressupõe
  conta permanente.
- **Grupo:** quantidade de pessoas e necessidades relevantes para acomodação.
- **Reserva:** intenção para data e horário, com estados e histórico.
- **Fila de espera:** conjunto operacional de entradas aguardando acomodação.
- **Entrada de espera:** participação de um grupo na fila, com chegada, faixa e estado.
- **Estimativa:** intervalo calculado ou informado, acompanhado de momento e premissas.
- **Acomodação:** vínculo temporal entre grupo e mesa(s).
- **Política operacional:** regras configuradas para atraso, chamada, cancelamento e capacidade.
- **Notificação:** comunicação transacional ligada a um evento e a um consentimento/base aplicável.
- **Evento operacional:** registro imutável de uma mudança relevante.

Relações essenciais: um estabelecimento possui áreas, mesas, políticas, reservas e uma fila
operacional. Reserva e entrada de espera referenciam um grupo, mas podem existir sem uma conta
persistente. Uma acomodação vincula um grupo a uma ou mais mesas. Eventos narram transições sem
substituir o estado atual.

---

## 11. Requisitos funcionais rastreáveis

### Cliente mobile

- **FR-001:** O produto deve permitir consultar datas, horários ou condição atual de espera
  disponibilizados pelo estabelecimento.
- **FR-002:** O produto deve permitir enviar solicitação de reserva com tamanho do grupo, dados
  mínimos de contato e necessidades opcionais.
- **FR-003:** O produto deve distinguir visualmente solicitação recebida de reserva confirmada.
- **FR-004:** O cliente deve poder acompanhar o estado da reserva por link ou código seguro.
- **FR-005:** O cliente deve poder cancelar e solicitar alterações dentro das políticas exibidas.
- **FR-006:** O produto deve permitir entrada remota na fila quando habilitada.
- **FR-007:** O acompanhamento da fila deve mostrar estado, faixa estimada, última atualização e
  posição aproximada quando apropriado.
- **FR-008:** O cliente deve poder confirmar que continua aguardando e responder a uma chamada.
- **FR-009:** O produto deve comunicar confirmação, mudança relevante, chamada e cancelamento pelos
  canais consentidos.
- **FR-010:** O fluxo deve oferecer instrução alternativa para quem não pode usar o canal mobile.

### Operação

- **FR-011:** O operador deve visualizar, em uma única visão temporal, reservas próximas, fila atual
  e disponibilidade de mesas.
- **FR-012:** O operador deve criar reserva ou entrada de espera em nome do cliente.
- **FR-013:** O operador deve confirmar, propor alteração, editar ou cancelar uma reserva.
- **FR-014:** O operador deve atualizar estados de uma entrada: aguardando, chamado, acomodado,
  desistente, ausente ou cancelado.
- **FR-015:** O operador deve registrar ocupação e liberação de mesa.
- **FR-016:** O produto deve alertar e impedir conflitos evidentes de acomodação, permitindo exceção
  autorizada quando a política admitir.
- **FR-017:** O operador deve visualizar grupos compatíveis com uma mesa disponível sem perder a
  decisão final.
- **FR-018:** O operador deve corrigir uma ação com registro da correção e sem apagar o evento
  anterior.
- **FR-019:** O painel deve identificar dados desatualizados ou ações ainda não sincronizadas.

### Administração e aprendizado

- **FR-020:** O administrador deve configurar horários, mesas, capacidades e políticas essenciais.
- **FR-021:** O administrador deve habilitar ou desabilitar reserva e fila remota por período.
- **FR-022:** O produto deve controlar papéis mínimos de administrador e operador.
- **FR-023:** O produto deve manter histórico de transições com momento, origem e ator aplicável.
- **FR-024:** O produto deve apresentar métricas agregadas de volume, espera, cancelamento, ausência
  e acomodação.
- **FR-025:** O administrador deve configurar texto de privacidade, consentimentos aplicáveis e prazo
  de retenção dentro das regras suportadas.
- **FR-026:** O produto deve permitir localizar e atender solicitações válidas do titular sobre seus
  dados.

---

## 12. Requisitos não funcionais

- **NFR-001 — Usabilidade no pico:** tarefas frequentes do operador devem ser testadas sob
  interrupção e pressão de tempo; a meta quantitativa será definida após medir o processo atual.
- **NFR-002 — Responsividade percebida:** ações principais devem oferecer retorno imediato e indicar
  processamento ou falha sem induzir repetição.
- **NFR-003 — Disponibilidade proporcional:** o piloto deve definir janelas críticas, tolerância de
  indisponibilidade e procedimento degradado antes de operar com clientes reais.
- **NFR-004 — Consistência:** reserva, fila e mesa não podem permanecer em estados incompatíveis sem
  alerta e mecanismo de reconciliação.
- **NFR-005 — Segurança:** acesso administrativo exige autenticação adequada, autorização por papel,
  proteção em trânsito e repouso e registros de acesso sensíveis.
- **NFR-006 — Privacidade:** aplicar minimização, finalidade, transparência, retenção e atendimento a
  direitos conforme legislação e contexto validados.
- **NFR-007 — Acessibilidade:** fluxos devem buscar conformidade com diretrizes reconhecidas,
  navegação por teclado, leitores de tela, foco visível e linguagem compreensível.
- **NFR-008 — Compatibilidade:** a experiência cliente deve funcionar em navegadores mobile atuais
  definidos na Discovery; o painel deve funcionar nos dispositivos reais observados.
- **NFR-009 — Conectividade:** falhas e reconexões não podem duplicar ações; o usuário deve saber se
  uma atualização foi registrada.
- **NFR-010 — Auditabilidade:** eventos críticos devem ser rastreáveis sem expor conteúdo pessoal
  desnecessário.
- **NFR-011 — Observabilidade:** erros, latência e falhas de comunicação devem ser mensuráveis com
  dados minimizados.
- **NFR-012 — Evolução:** regras operacionais devem poder mudar sem exigir que conceitos distintos,
  como reserva e fila, sejam fundidos.

Metas quantitativas permanecem abertas até haver contexto real de piloto; defini-las agora seria
falsa precisão.

---

## 13. Fluxos principais

### FLOW-01 — Solicitar e confirmar reserva

1. Cliente consulta disponibilidade.
2. Informa grupo e contato mínimo.
3. Revisa finalidade dos dados e envia.
4. Sistema registra como “solicitada” e fornece acompanhamento.
5. Operador confirma, propõe alternativa ou recusa.
6. Cliente recebe estado inequívoco.

Alternativas: horário indisponível, solicitação duplicada, mudança de grupo, cancelamento e
necessidade de contato assistido.

### FLOW-02 — Entrar e acompanhar fila

1. Cliente ou operador informa o grupo.
2. Sistema apresenta faixa estimada e caráter não garantido.
3. Entrada é criada como “aguardando”.
4. Cliente acompanha atualização e confirma permanência.
5. Operador chama o grupo.
6. Grupo responde e é acomodado, reordenado por decisão ou encerrado.

### FLOW-03 — Operar salão

1. Operador abre visão “agora”.
2. Confere reservas próximas, fila e mesas.
3. Atualiza mesa liberada.
4. Avalia grupos compatíveis.
5. Chama e acomoda um grupo.
6. Sistema atualiza os estados relacionados e registra o evento.

### FLOW-04 — Tratar exceção

1. Operador identifica atraso, ausência, mudança ou conflito.
2. Consulta política e contexto.
3. Escolhe ação permitida ou exceção autorizada.
4. Registra justificativa curta quando necessária.
5. Cliente recebe comunicação aplicável.
6. Histórico preserva estado anterior e correção.

### FLOW-05 — Configurar operação

1. Administrador informa horários e períodos.
2. Cadastra áreas, mesas e capacidades.
3. Define políticas de confirmação, atraso, chamada e retenção.
4. Revisa simulação básica de disponibilidade.
5. Publica configuração.
6. Operador confirma que o painel representa o salão real.

---

## 14. Mapa de telas

### Experiência mobile do cliente

- **SCR-C01 — Página do restaurante:** estado atual, ações de reservar ou entrar na fila.
- **SCR-C02 — Escolha de data/horário:** opções e indisponibilidades.
- **SCR-C03 — Dados do grupo:** quantidade, nome de chamada, contato e necessidade opcional.
- **SCR-C04 — Revisão e consentimento:** resumo, política e finalidade dos dados.
- **SCR-C05 — Acompanhamento da reserva:** estado, detalhes, alterar e cancelar.
- **SCR-C06 — Entrada na fila:** faixa estimada e confirmação.
- **SCR-C07 — Acompanhamento da espera:** estado, atualização, posição aproximada e saída.
- **SCR-C08 — Chamada:** janela para resposta e instrução de apresentação.
- **SCR-C09 — Resultado/encerramento:** acomodado, cancelado, ausência ou erro recuperável.

Referência visual: [mesa-pronta-customer-flow.svg](mesa-pronta-customer-flow.svg).

### Painel web do operador

- **SCR-O01 — Agora:** reservas próximas, fila, mesas e alertas.
- **SCR-O02 — Agenda:** reservas por data e período.
- **SCR-O03 — Detalhe do grupo:** histórico, contato mínimo e ações.
- **SCR-O04 — Cadastro rápido:** reserva ou fila assistida.
- **SCR-O05 — Mapa/lista de mesas:** capacidade, área e estado.
- **SCR-O06 — Tratamento de conflito:** alternativas, política e exceção.
- **SCR-O07 — Configurações:** horários, mesas, políticas, papéis e privacidade.
- **SCR-O08 — Histórico e métricas:** eventos e indicadores agregados.

Referência visual: [mesa-pronta-operator-dashboard.svg](mesa-pronta-operator-dashboard.svg).

---

## 15. Rastreabilidade: requisito → fluxo → tela

| Requisitos | Fluxo principal | Telas principais |
|---|---|---|
| FR-001–FR-005 | FLOW-01 | SCR-C01–SCR-C05, SCR-O02, SCR-O03 |
| FR-006–FR-010 | FLOW-02 | SCR-C01, SCR-C06–SCR-C09, SCR-O01 |
| FR-011–FR-012 | FLOW-03 | SCR-O01, SCR-O04, SCR-O05 |
| FR-013, FR-018 | FLOW-01 / FLOW-04 | SCR-O02, SCR-O03, SCR-O06 |
| FR-014–FR-017 | FLOW-02 / FLOW-03 | SCR-O01, SCR-O03, SCR-O05 |
| FR-019 | FLOW-03 / FLOW-04 | SCR-O01, SCR-O06 |
| FR-020–FR-022 | FLOW-05 | SCR-O07 |
| FR-023–FR-026 | FLOW-04 / FLOW-05 | SCR-O03, SCR-O07, SCR-O08 |

Esta matriz confirma cobertura conceitual, não completude de especificação. Cada requisito ainda
precisa de critérios de aceite, estados de erro e regras detalhadas antes da implementação.

---

## 16. Métricas de sucesso e critérios

### 16.1 Métrica norteadora candidata

**Percentual de atendimentos elegíveis coordenados no MesaPronta sem conflito operacional não
resolvido.** A definição de “elegível”, “coordenado” e “conflito” deve ser testada no piloto para
evitar uma métrica que premie apenas volume.

### 16.2 Indicadores do cliente

- Taxa de conclusão de solicitação de reserva.
- Taxa de conclusão de entrada na fila.
- Percentual que compreende corretamente “solicitada” versus “confirmada” em teste.
- Percentual que compreende faixa estimada como não garantida.
- Contatos adicionais por atendimento para perguntar estado.
- Abandono antes e depois da chamada.
- Sucesso de tarefa com tecnologias assistivas.

### 16.3 Indicadores da operação

- Tempo mediano para registrar uma entrada durante o pico.
- Percentual de reservas/fila efetivamente mantido no produto durante o piloto.
- Conflitos de mesa, duplicidades e correções por turno.
- Ações pendentes ou sem sincronização.
- Frequência de retorno a papel ou canal paralelo e motivo.
- Percepção de carga de trabalho antes/depois, coletada com método consistente.

### 16.4 Indicadores de negócio

- Restaurantes que concluem configuração e realizam turnos reais.
- Retenção de estabelecimentos após o período de teste.
- Conversão de piloto para compromisso pago, se uma oferta real for testada.
- Custo e volume de suporte por estabelecimento.

### 16.5 Critérios propostos para um piloto bem-sucedido

Definir os limiares após uma semana de linha de base. Como critérios qualitativos iniciais:

1. operadores usam o produto como fonte principal em turnos selecionados;
2. nenhuma falha crítica causa dupla acomodação ou perda irrecuperável de lista;
3. clientes distinguem solicitação de confirmação nos testes;
4. o caminho sem smartphone funciona na prática;
5. há sinal de redução de retrabalho sem aumento relevante do tempo de atendimento;
6. pelo menos parte dos decisores demonstra compromisso observável, não apenas opinião favorável.

Se a linha de base não puder ser medida, registrar a limitação em vez de fabricar comparação.

---

## 17. Riscos e mitigações

| Risco | Consequência | Mitigação proposta |
|---|---|---|
| Equipe não atualiza o painel no pico | Estado perde confiança e produto é abandonado | Observação contextual, teste sob interrupção, atalhos e piloto restrito |
| Estimativa imprecisa parece promessa | Frustração e conflito com cliente | Faixa, última atualização, linguagem clara e controle do operador |
| Duplicidade por conexão instável | Reserva ou acomodação conflitante | Operações idempotentes, estado de sincronização e reconciliação |
| Excesso de dados pessoais | Risco legal e reputacional | Minimização, retenção definida, consentimento/base validada e acesso restrito |
| Ordem da fila percebida como injusta | Discussões e perda de confiança | Explicar posição aproximada e critérios; registrar exceções |
| Produto exclui cliente sem smartphone | Atendimento desigual | Cadastro assistido e chamada presencial |
| Configuração não representa o salão | Disponibilidade incorreta | Revisão visual e confirmação operacional antes de publicar |
| Escopo cresce para gestão completa | MVP demora e perde foco | Não objetivos explícitos e gate para novas capacidades |
| Métricas incentivam velocidade sobre acolhimento | Experiência pior apesar de números melhores | Combinar eficiência, erros, compreensão e feedback qualitativo |
| Notificações falham ou incomodam | Cliente perde chamada ou revoga confiança | Preferências, confirmação no painel e canal alternativo |
| Acessibilidade tratada tarde | Barreiras estruturais | Recrutamento dedicado e testes desde o protótipo |
| Disposição a pagar é superestimada | Produto útil, negócio inviável | Teste de oferta real antes de expansão |

---

## 18. Decisões em aberto

1. O ICP deve aceitar somente restaurantes com anfitrião dedicado ou também operações em que o
   gerente acumula essa função?
2. Reserva será confirmada automaticamente em alguma condição ou sempre revisada no MVP?
3. Quais dados de contato são indispensáveis e qual base adequada para cada comunicação?
4. Como calcular a faixa de espera inicial sem criar falsa precisão?
5. Quais critérios de prioridade são legítimos, configuráveis e comunicáveis?
6. Até onde o cliente pode alterar tamanho e horário sem nova confirmação?
7. Qual é a política de atraso e quanto varia por restaurante?
8. A visão de mesas deve ser mapa visual ou lista otimizada? O ambiente real decide.
9. Qual procedimento degradado mantém a operação durante indisponibilidade?
10. Qual prazo de retenção atende operação e privacidade?
11. Que limiar de volume e complexidade torna o restaurante inadequado ao MVP?
12. Qual modelo comercial será testado e que compromisso conta como evidência?

Nenhuma dessas decisões exige escolha de stack nesta fase.

---

## 19. Plano de validação com protótipos

### Etapa 1 — compreensão do problema

Executar entrevistas e observações descritas na seção 5. Sintetizar episódios, frequência, impacto,
soluções atuais e contraexemplos. Resultado: hipóteses atualizadas e ICP refinado.

### Etapa 2 — protótipo de baixa fidelidade

Testar tarefas com esboços: solicitar reserva, distinguir confirmação, entrar na fila, interpretar
faixa, cadastrar grupo, liberar mesa e tratar atraso. Participantes devem pensar em voz alta; o
facilitador não deve ensinar o fluxo. Registrar sucesso, erros, hesitações e compreensão.

### Etapa 3 — mockups visuais

Usar os dois artefatos complementares:

- [Fluxo mobile do cliente](mesa-pronta-customer-flow.svg), para testar sequência, linguagem,
  consentimento, estados e recuperação.
- [Painel web do operador](mesa-pronta-operator-dashboard.svg), para testar hierarquia, leitura de
  relance, ações no pico e conflitos.

Realizar pelo menos cinco sessões por superfície na primeira rodada, incluindo participantes com
tecnologias assistivas. “Cinco” é ponto de partida prático, não prova de saturação; repetir após
mudanças relevantes.

### Etapa 4 — simulação operacional

Antes de clientes reais, encenar um turno com cartões ou dados fictícios: reservas simultâneas,
grupos incompatíveis, atraso, desistência, mesa bloqueada e conexão intermitente. Medir tempo, erros
e necessidade de ajuda. O objetivo é revelar falhas de coordenação, não demonstrar uma apresentação
perfeita.

### Etapa 5 — piloto controlado

Somente após revisão de privacidade, segurança e procedimento degradado, testar em poucos
estabelecimentos e períodos delimitados. Coletar linha de base, eventos, incidentes, feedback e
motivos de não uso. Definir condição de interrupção caso o produto prejudique atendimento ou dados.

### Registro e decisão

Cada etapa registra evidências, limitações, alterações, hipóteses afetadas e recomendação de gate.
Opinião favorável sem comportamento observável não comprova validação.

---

## 20. Checklist de prontidão

Marcar apenas com evidência real.

### Problema e público

- [ ] Há episódios recentes documentados, não apenas opiniões gerais.
- [ ] Frequência e impacto foram estimados com fonte e limitação.
- [ ] O ICP inicial foi confrontado com casos que não se encaixam.
- [ ] Operadores e clientes foram ouvidos em proporção adequada.
- [ ] O processo foi observado em contexto calmo e de pico.

### Proposta e experiência

- [ ] Solicitação e confirmação são compreendidas como estados diferentes.
- [ ] A faixa de espera não é interpretada como garantia.
- [ ] Tarefas críticas foram testadas sem ajuda do facilitador.
- [ ] O fluxo sem smartphone foi demonstrado.
- [ ] Participantes com necessidades de acessibilidade testaram as superfícies.
- [ ] Os mockups refletem aprendizados registrados, não preferências internas.

### Escopo e operação

- [ ] MVP e fora de escopo foram aceitos pelos responsáveis.
- [ ] Regras de atraso, fila, capacidade e exceção têm owner.
- [ ] O painel foi simulado sob interrupção e volume plausível.
- [ ] Existe procedimento degradado e reconciliação.
- [ ] Cada requisito MVP possui fluxo, tela e futuro critério de aceite.

### Privacidade, risco e negócio

- [ ] Dados mínimos, finalidade, retenção e direitos foram revisados.
- [ ] Riscos críticos têm mitigação e condição de interrupção.
- [ ] Métricas têm definição e linha de base possível.
- [ ] Há teste de compromisso comercial, se viabilidade de negócio for necessária.
- [ ] Decisões em aberto que bloqueiam o piloto foram resolvidas ou explicitamente aceitas.

---

## 21. Decisão de gate

Ao fim do Warmup/amadurecimento, escolher conscientemente uma das três opções:

### Avançar

Usar quando problema, público e proposta têm evidência suficiente; riscos críticos possuem plano;
escopo está delimitado; e as incertezas restantes podem ser resolvidas na Discovery sem invalidar a
tese. Avançar não significa que tudo está certo, apenas que o próximo investimento é justificável.

### Amadurecer

Usar quando a ideia parece promissora, mas faltam evidências essenciais, há confusão de público,
fluxos críticos não funcionam ou decisões abertas mudariam o MVP. Definir exatamente qual coleta ou
teste reduz a incerteza e uma data para nova decisão.

### Parar

Usar quando o problema não é relevante ou frequente, a solução piora a operação, o risco é
desproporcional, não existe compromisso de adoção ou outra abordagem resolve melhor. Parar é um
resultado válido e preserva aprendizado; não deve ser mascarado como “pausa” indefinida.

### Gate atual deste exemplo

**AMADURECER.** A razão é objetiva: não há pesquisa executada, evidência de problema, teste de
protótipo, linha de base ou sinal comercial. O próximo passo recomendado seria realizar a rodada da
seção 5 e testar protótipos de baixa fidelidade. Também seria possível avançar com ressalvas, desde
que a equipe declare menor confiança e maior risco de retrabalho. Este documento não impõe bloqueio.

---

## 22. Encerramento

MesaPronta ilustra como conectar hipóteses, pesquisa, escopo, domínio, requisitos, fluxos, telas,
métricas e gate sem antecipar arquitetura técnica ou inventar validação. Fatos reais devem mudar o
documento e apontar para suas fontes.

**Lembrete final:** este é um exemplo fictício e não prescritivo. Copiar sua estrutura sem adaptar o
raciocínio ao contexto produziria aparência de completude, não entendimento.
