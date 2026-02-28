# Auraxis Platform

Repositório orquestrador para contexto, governança e automações do ecossistema Auraxis (API, Web e Mobile).

## Objetivo
Centralizar regras de execução e contexto compartilhado para trabalho humano + IA (Agentic Workflows), evitando perda de histórico decisório entre repositórios.

## Branch principal
- Branch principal oficial: `master`.
- Branches de trabalho: seguir conventional branching (`feat/...`, `fix/...`, `docs/...`, etc.).

## Estrutura
```text
auraxis-platform/
  .context/                 # base de conhecimento e governança
  repos/                    # auraxis-api, auraxis-web, auraxis-app
  workflows/                # esteiras e automações
  scripts/                  # utilitários de orquestração
  docs/                     # documentação transversal
```

## Leitura obrigatória
Comece por:
1. `.context/06_context_index.md`
2. `.context/07_steering_global.md`
3. `.context/08_agent_contract.md`
4. `.context/01_status_atual.md`
5. `.context/02_backlog_next.md`

Complementares (obrigatórios para setup completo):
- `.context/15_workflow_conventions.md`
- `.context/16_contract_compatibility_policy.md`
- `.context/17_discovery_framework.md`
- `.context/18_feedback_loop.md`
- `.context/19_context_maintenance.md`
- `.context/20_decision_log.md`
- `.context/21_repo_init_runbook.md`
- `.context/22_workspace_migration_checklist.md`

## Bootstrap dos repositórios

### Opção recomendada: submodules
```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform

git submodule add <git-url-backend> repos/auraxis-api
git submodule add <git-url-web> repos/auraxis-web
git submodule add <git-url-app> repos/auraxis-app

git submodule update --init --recursive
```

### Alternativa: pastas locais (sem submodule)
Use apenas se não quiser versionar ponteiros de commit dos repos no `auraxis-platform`.

## Convenções globais
- Não commitar em `master/main` diretamente.
- Conventional branching + conventional commits.
- Commits pequenos e reversíveis.
- Toda decisão relevante deve atualizar `.context`.
- Cada repo mantém seu `tasks.md` local.

## Definição de pronto por bloco
- Implementação concluída.
- Testes e gates aplicáveis passando.
- `tasks.md` atualizado com rastreabilidade.
- Handoff registrado.

## Setup dos novos repositórios (agnóstico de stack)
Ao criar um novo repo em `repos/` (ex.: `auraxis-web`, `auraxis-app`), iniciar com:
- `README.md` curto
- `steering.md` (a partir do template)
- `tasks.md` (a partir do template)
- `AGENTS.md` (a partir do template)
- `docs/adr/` com `ADR_TEMPLATE.md`

Templates disponíveis em `.context/templates`.

## Templates
Modelos prontos em `.context/templates` para inicializar novos repositórios:
- `REPO_STEERING_TEMPLATE.md`
- `TASKS_TEMPLATE.md`
- `AGENTS_TEMPLATE.md`
- `ADR_TEMPLATE.md`
- `HANDOFF_TEMPLATE.md`

## Fluxo operacional recomendado
1. Priorizar bloco atual (`tasks.md` repo alvo).
2. Implementar em branch de feature/fix.
3. Validar local + CI.
4. Atualizar contexto e backlog.
5. Registrar handoff para continuidade.

## DX rápida (orquestrador)

Comandos curtos para executar agentes sem export manual:

```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform
make help
```

Setup inicial do `ai_squad`:

```bash
make squad-setup
```

Setup one-shot do runtime local (Node 22 + venv + dependências de api/web/app):

```bash
make runtime-setup
```

Executar com comando único (master + paralelismo api/web/app + lock automático):

```bash
make next-task
```

Alias equivalente:

```bash
make next-task-safe
```

Dry-run de planejamento (sem escrita/commit):

```bash
make next-task-plan
```

Executar em repo específico:

```bash
make next-task-api
make next-task-web
make next-task-app
```

Com briefing/prompt custom:

```bash
BRIEFING="Execute a tarefa" make next-task
```

## Próximo passo sugerido
1. Rodar `./scripts/verify-agent-session.sh`.
2. Rodar `./scripts/check-health.sh`.
3. Ler `.context/01_status_atual.md` e seguir a próxima task prioritária.
4. Trabalhar em branch dedicada e atualizar `tasks.md` + `.context/05_handoff.md` ao fechar bloco.
