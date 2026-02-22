# Repo Init Runbook

## Objetivo
Criar rapidamente novos repositórios de produto com baseline de documentação, governança e execução por agentes.

## Pré-requisitos
- `auraxis-platform` inicializado
- repositório remoto criado (quando aplicável)

## Passo a passo (por repo)
Exemplo para `auraxis-web`:

```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform/repos
mkdir auraxis-web
cd auraxis-web
git init
mkdir -p docs/adr
cp ../../.context/templates/REPO_STEERING_TEMPLATE.md ./steering.md
cp ../../.context/templates/TASKS_TEMPLATE.md ./tasks.md
cp ../../.context/templates/AGENTS_TEMPLATE.md ./AGENTS.md
cp ../../.context/templates/ADR_TEMPLATE.md ./docs/adr/ADR-000-template.md
printf "# Auraxis Web\n\nDescrição breve.\n" > README.md
git add .
git commit -m "docs: bootstrap repository governance and templates"
```

## Ajustes obrigatórios após bootstrap
- adaptar `steering.md` para o domínio do repo
- preencher backlog inicial em `tasks.md`
- registrar primeira decisão real em `docs/adr`
- configurar CI mínimo (lint, testes, segurança)

## Integração com platform (se usar submodule)
No repo `auraxis-platform`:

```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform
git submodule add <git-url-auraxis-web> repos/auraxis-web
git submodule update --init --recursive
```

## Validação final
- [ ] templates aplicados
- [ ] leitura de contexto funcionando
- [ ] regras de branch/commit documentadas
- [ ] pipeline mínimo planejado
