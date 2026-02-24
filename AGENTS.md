# AGENTS - Auraxis Platform

## Entrada padrão
Todo agente deve iniciar por:
1. `.context/06_context_index.md`
2. `.context/07_steering_global.md`
3. `.context/08_agent_contract.md`

## Escopo deste repositório
- Governança global
- Contexto compartilhado
- Templates de bootstrap
- Orquestração entre repos (`repos/auraxis-api`, `repos/auraxis-web`, `repos/auraxis-app`)

## Regras de execução
- Não commitar diretamente em `main/master` dos repos de produto.
- Usar conventional branching + conventional commits.
- Não criar nem publicar branches com prefixo `codex/`.
- Manter commits pequenos e reversíveis.
- Atualizar contexto (`.context`) após decisões relevantes.
- Atualizar `tasks.md` no repositório afetado a cada bloco.
- Seguir política de contratos em `.context/16_contract_compatibility_policy.md`.
- Seguir framework de discovery em `.context/17_discovery_framework.md`.
- Rodar ritual de feedback por bloco em `.context/18_feedback_loop.md`.
- Ao concluir um bloco, reportar no terminal: status, o que foi implementado, tasks concluídas e próxima sugestão.
- Em erro/bloqueio, notificar gestor e agentes paralelos no terminal e registrar motivo em `tasks_status/<TASK_ID>.md` (local).
- `tasks_status/` é telemetria local e não deve ser commitado; fonte de verdade continua sendo `tasks.md`/`TASKS.md`.

## Handoff obrigatório
Ao finalizar um bloco, registrar:
- o que foi feito
- o que foi validado
- riscos pendentes
- próximo passo

Arquivo recomendado: `.context/05_handoff.md`
