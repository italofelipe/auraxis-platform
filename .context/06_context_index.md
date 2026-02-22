# Context Index

## Objetivo
Este índice organiza a leitura mínima para qualquer pessoa/agente retomar o projeto sem depender de histórico de conversa.

## Ordem de leitura obrigatória
1. `00_overview.md`
2. `06_context_index.md`
3. `07_steering_global.md`
4. `08_agent_contract.md`
5. `09_architecture_principles.md`
6. `10_product_operating_model.md`
7. `11_repo_map.md`
8. `12_quality_security_baseline.md`
9. `13_release_governance.md`
10. `15_workflow_conventions.md`
11. `16_contract_compatibility_policy.md`
12. `17_discovery_framework.md`
13. `18_feedback_loop.md`
14. `19_context_maintenance.md`
15. `20_decision_log.md`
16. `21_repo_init_runbook.md`
17. `01_status_atual.md`
18. `02_backlog_next.md`
19. `05_handoff.md`
20. `discovery/README.md`
21. `tech_debt/README.md`

## Templates para novos repositórios
- `templates/REPO_STEERING_TEMPLATE.md`
- `templates/TASKS_TEMPLATE.md`
- `templates/AGENTS_TEMPLATE.md`
- `templates/ADR_TEMPLATE.md`
- `templates/HANDOFF_TEMPLATE.md`
- `templates/PRODUCT_TEMPLATE.md`
- `templates/RELEASE_NOTES_TEMPLATE.md`

## Pacote de discovery atual
- `discovery/J1_exportacao_csv_xlsx.md`
- `discovery/J2_importacao_relatorios_bancarios.md`
- `discovery/J3_conciliacao_insights_llm.md`
- `discovery/J4_aba_ferramentas_conveniencia.md`
- `discovery/J5_open_finance_open_banking.md`
- `discovery/discovery_execucao_roadmap.md`

## Pacote de débito técnico atual
- `tech_debt/X3_fastapi_migration_coexistence.md`
- `tech_debt/X4_ruff_adoption_strategy.md`
- `tech_debt/tech_debt_execution_sequence.md`

## Regra de atualização
Sempre que houver decisão de produto/arquitetura/processo:
- atualizar `.context` (nível plataforma)
- atualizar `tasks.md` do repositório impactado
- atualizar `05_handoff.md` com próximos passos
