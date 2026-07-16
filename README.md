# Journey AutoCode

**Metodologia + instaláveis open-source** para gerir projectos com agentes de IA (Claude Code e ecossistema Spec Kit).

Licença: **Apache License 2.0** — ver `LICENSE` e `NOTICE`.

## O que é isto

Journey define um ciclo de vida em **seis fases** (Warmup → Foundation → Discovery → Build → Release → Run), com rituais de sessão, ADRs, HANDOVER e comandos `/journey-*` que o agente conduz no teu repositório.

Este repositório é a **rota AutoCode**: o que corre **no teu git + IDE**. É grátis e ilimitado no teu disco.

## Open vs Site (1 projecto grátis)

| | AutoCode (este repo) | Site Journey (hospedado) |
|---|---|---|
| O quê | Metodologia, templates, CLIs, skills | Roadmap/Cockpit consolidados |
| Onde | O teu repositório | Serviço na nuvem |
| Preço | Grátis (Apache-2.0) | **1º projecto grátis** / 2º+ pago |

Podes usar **só** este repo — **sem** criar conta no Site. O Site é opcional: liga o teu GitHub e vê o roadmap vivo.

Mais: [`docs/open-vs-site.md`](docs/open-vs-site.md).

## Começar sem o Site (IDE)

1. Instala **git**, **Python 3.12+** e **[uv](https://docs.astral.sh/uv/)**.
2. Abre o Claude Code (ou IDE com agente) na pasta do **teu** projecto novo.
3. Cola um prompt que peça ao agente para:
   - clonar **esta** base (`https://github.com/Kokubord/journey-autocode.git`) para uma pasta irmã (ex. `.journey-base`);
   - seguir `.claude/skills/journey-bootstrap/SKILL.md`;
   - correr `journey-init` com `--templates` da base e `--target` na pasta actual.
4. Ou instala os CLIs a partir deste monorepo (wheels) e corre `journey-init` directamente — ver [`docs/getting-started.md`](docs/getting-started.md).

O agente deve **pausar** para a tua aprovação em cada passo.

## Guias por fase

Começa em [`docs/phases/00-warmup.md`](docs/phases/00-warmup.md) — inclui o capítulo sobre o
**Documento de Visão**, roteiro de levantamento com usuários, checklist de prontidão e um
[exemplo fictício preenchido](docs/examples/mesa-pronta-vision.md) com mockups de fluxos e telas.

Warmup é recomendado, mas não bloqueante: podes instalar Journey primeiro ou amadurecer a ideia
antes. Se avançares só com um prompt mínimo, a metodologia deve declarar a menor confiança nos
requisitos e o maior risco de retrabalho — nunca fingir que houve validação.

## Actualizações

- **CLIs / skills:** reinstala ou `journey-upgrade` (skills) quando houver release nova.
- **Regras da metodologia** já materializadas no teu projecto: ainda **não** há upgrade automático de versão (trabalho futuro). Acompanha as releases deste repo e o changelog.

## Não incluído

Código do **Site** (consolidação TypeScript, login, sync) — produto separado, não faz parte desta licença Apache.

## Contribuir

Ver `CONTRIBUTING.md`.
