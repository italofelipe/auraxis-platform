# Auraxis Platform

Repositório orquestrador para contexto, governança e automações do ecossistema Auraxis (API, Web e Mobile).

## Objetivo
Centralizar regras de execução e contexto compartilhado para trabalho humano + IA (Agentic Workflows), evitando perda de histórico decisório entre repositórios.

## Estrutura
```text
auraxis-platform/
  .context/                 # base de conhecimento e governança
  repos/                    # auraxis-api, auraxis-web, auraxis-mobile
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

## Bootstrap dos repositórios

### Opção recomendada: submodules
```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform

git submodule add <git-url-backend> repos/auraxis-api
git submodule add <git-url-web> repos/auraxis-web
git submodule add <git-url-mobile> repos/auraxis-mobile

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
Ao criar `repos/auraxis-web` e `repos/auraxis-mobile`, iniciar com:
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

## Próximo passo sugerido
1. Adicionar os repositórios de produto em `repos/` (preferencialmente com submodule).
2. Aplicar templates mínimos em cada repo novo.
3. Configurar CI de cada repo com baseline de qualidade e segurança.
4. Configurar rotina de revisão de contexto (`.context/19_context_maintenance.md`).
