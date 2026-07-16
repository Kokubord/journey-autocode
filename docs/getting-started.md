# Começar com Journey AutoCode

## Pré-requisitos

- Git
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Um IDE com agente (hoje o caminho mais testado é **Claude Code**)

## Caminho A — Prompt no IDE (recomendado a quem começa)

1. Cria uma pasta vazia para o teu projecto e abre-a no IDE.
2. Pede ao agente para clonar a base:

   `https://github.com/Kokubord/journey-autocode.git`

   para uma pasta **nova** (ex. `.journey-base` ou pasta irmã) — **não** misturar com o teu código.
3. Pede para ler e seguir `.claude/skills/journey-bootstrap/SKILL.md` dentro da base.
4. Confirma cada checkpoint. No fim deves estar na fase **Warmup**, com `HANDOVER.md` e artefatos Journey no teu projecto.

## Caminho B — CLIs no PATH

A partir de um clone deste repo:

```bash
uv sync --all-packages
uv build --package journey-core --package journey-skill
uv tool install --find-links dist journey-skill
```

(Ajusta conforme a estrutura de wheels do release; o objectivo é `journey-init` no PATH **sem** depender do monorepo privado.)

Depois:

```bash
journey-init --target /caminho/do/teu/projecto --templates /caminho/desta/base/templates
```

## O que NÃO precisas

- Conta no Site Journey
- Acesso ao repositório privado de desenvolvimento do Journey
- Token especial (este repo é público)

## Depois do install

Lê [`phases/00-warmup.md`](phases/00-warmup.md) e decide se já tens clareza para a Foundation.
