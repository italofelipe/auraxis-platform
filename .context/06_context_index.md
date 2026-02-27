# Context Index

Última atualização: 2026-02-26

## Objetivo

Este índice organiza a leitura mínima para qualquer pessoa ou agente retomar o projeto sem depender de histórico de conversa.

---

## Ordem de leitura obrigatória (session bootstrap)

| # | Arquivo | O que fornece |
|:--|:--------|:--------------|
| 1 | `00_overview.md` | Visão geral do produto e do ecossistema |
| 1.1 | `../product.md` | Fonte única de produto (estratégia e direção canônica) |
| 2 | `07_steering_global.md` | Princípios imutáveis de entrega |
| 3 | `08_agent_contract.md` | Contrato de comportamento de agentes |
| 4 | `23_definition_of_done.md` | DoD canônico — critérios de conclusão |
| 5 | `09_architecture_principles.md` | Princípios de arquitetura de software |
| 6 | `10_product_operating_model.md` | Como priorizar e classificar trabalho |
| 7 | `11_repo_map.md` | Mapa dos repos, stacks e remotes |
| 8 | `12_quality_security_baseline.md` | Gates de qualidade e segurança por stack |
| 9 | `13_release_governance.md` | Fluxo de release e aprovação |
| 10 | `15_workflow_conventions.md` | Branch, commit e PR conventions |
| 11 | `16_contract_compatibility_policy.md` | Política de versionamento de contratos de API |
| 12 | `20_decision_log.md` | Log de decisões com rationale |
| 13 | `01_status_atual.md` | **Estado atual** — ler sempre antes de agir |
| 14 | `02_backlog_next.md` | **Próximas prioridades** — o que fazer |
| 15 | `05_handoff.md` | **Handoff** — continuidade entre sessões |

### Leitura complementar (conforme necessidade)

| Arquivo | Quando ler |
|:--------|:-----------|
| `25_quality_security_playbook.md` | **Ao trabalhar em qualquer repo frontend** — manual completo de quality + security |
| `26_frontend_architecture.md` | **Antes de qualquer trabalho em auraxis-app ou auraxis-web** — arquitetura, tokens, feature-based, zero `any`, PWA |
| `30_design_reference.md` | **Obrigatorio para tarefas de UI/layout no app e web** — referencia visual canonica dos assets em `designs/` |
| `32_frontend_unified_guideline.md` | **Obrigatorio para tarefas frontend** — regras canônicas unificadas web/app |
| `27_agentic_maturity_remediation_plan.md` | Ao acompanhar as correções de maturidade operacional para autonomia de agentes |
| `28_autonomous_delivery_readiness.md` | Antes de iniciar novos blocos de feature com agentes autônomos (baseline de prontidão) |
| `29_feature_flags_foundation.md` | Ao operar PLT4 (base de governança de feature toggles) |
| `31_feature_flag_lifecycle.md` | Ao criar/alterar flags em web/app/api |
| `feature_contracts/README.md` | Antes de integrar frontend com feature backend recém-entregue |
| `openapi/README.md` | Antes de sincronizar tipos de API no frontend (`contracts:sync`) |
| `17_discovery_framework.md` | Ao avaliar novas features/ideias |
| `18_feedback_loop.md` | Ao encerrar um ciclo de trabalho |
| `19_context_maintenance.md` | Ao atualizar arquivos de `.context/` |
| `21_repo_init_runbook.md` | Ao criar um novo repositório de produto |
| `22_workspace_migration_checklist.md` | Ao mover ou renomear repos |
| `03_decisoes_arquitetura.md` | Ao tomar decisão com impacto arquitetural |
| `04_agent_playbook.md` | Referência rápida de protocolos de agente |
| `14_repo_bootstrap_checklist.md` | Checklist ao bootstrapar novo repo |

---

## Templates para novos repositórios

| Template | Uso |
|:---------|:----|
| `templates/AGENTS_TEMPLATE.md` | Base para `CLAUDE.md` de um novo repo de produto |
| `templates/TASKS_TEMPLATE.md` | Base para `tasks.md` de um novo repo |
| `templates/REPO_STEERING_TEMPLATE.md` | Base para `steering.md` de um novo repo |
| `templates/ADR_TEMPLATE.md` | Registro de decisão arquitetural |
| `templates/HANDOFF_TEMPLATE.md` | Handoff entre sessões/agentes |
| `templates/PRODUCT_TEMPLATE.md` | Documento de produto (discovery/spec) |
| `templates/RELEASE_NOTES_TEMPLATE.md` | Release notes estruturadas |

---

## Scripts de automação (platform)

| Script | O que faz |
|:-------|:----------|
| `../scripts/check-health.sh` | Diagnóstico completo de saúde pré-sessão |
| `../scripts/setup-submodules.sh` | Setup one-shot de todos os submodules (onboarding) |
| `../scripts/bootstrap-repo.sh` | Cria novo repo de produto com governance baseline |
| `../scripts/agent-lock.sh` | Mutex de coordenação entre agentes concorrentes |

---

## Workflows de orquestração

| Workflow | O que descreve |
|:---------|:---------------|
| `../workflows/agent-session.md` | Protocolo completo de sessão de agente (7 passos) |
| `../workflows/feature-delivery.md` | Ciclo SDD de entrega de feature (SPEC → CLOSE) |
| `../workflows/multi-front-agent-orchestration.md` | Modelo de execução paralela API/Web/App com CrewAI + Claude + Gemini + GPT |
| `../workflows/repo-bootstrap.md` | Criação de novo repo de produto (opções A e B) |

---

## Guias de integração por agente (platform)

| Arquivo | Agente | Papel |
|:--------|:-------|:------|
| `../ai_integration-claude.md` | Claude | Governança, orquestração, revisão |
| `../ai_integration-gemini.md` | Gemini | Revisão arquitetural, análise alternativa |
| `../ai_integration-gpt.md` | GPT/Codex | Implementação, code generation |

---

## Schema de coordenação

- `agent_lock.schema.json` — contrato JSON Schema do mutex entre agentes

---

## Pacote de discovery atual

| Arquivo | Tema |
|:--------|:-----|
| `discovery/J1_exportacao_csv_xlsx.md` | Exportação de relatórios |
| `discovery/J2_importacao_relatorios_bancarios.md` | Importação bancária |
| `discovery/J3_conciliacao_insights_llm.md` | Conciliação + LLM |
| `discovery/J4_aba_ferramentas_conveniencia.md` | Ferramentas de conveniência |
| `discovery/J5_open_finance_open_banking.md` | Open Finance (bloqueado) |
| `discovery/J6_web_paginas_publicas_privadas_seo.md` | Arquitetura web pública/privada + SEO |
| `discovery/J7_ferramentas_publica_privada_simulacao.md` | Ferramentas híbridas (público/logado) |
| `discovery/J8_newsletter_growth_loop.md` | Newsletter e growth loop |
| `discovery/J9_integracao_meios_pagamento.md` | Integração de meios de pagamento no Brasil |
| `discovery/J10_feed_noticias_economia_ia_scrapers.md` | Feed de notícias econômicas com IA/scrapers |
| `discovery/J11_alertas_email_pendencias_vencimentos.md` | Alertas por email de pendências/vencimentos |
| `discovery/discovery_execucao_roadmap.md` | Roadmap consolidado de discovery |

---

## Pacote de débito técnico atual

| Arquivo | Tema |
|:--------|:-----|
| `tech_debt/X3_fastapi_migration_coexistence.md` | Migração Flask → FastAPI |
| `tech_debt/X4_ruff_adoption_strategy.md` | Adoção faseada do Ruff |
| `tech_debt/tech_debt_execution_sequence.md` | Ordem de execução X3/X4 |
| `tech_debt/X3_X4_executive_snapshot.md` | Resumo executivo X3/X4 |

---

## Regra de atualização

Sempre que houver decisão de produto, arquitetura ou processo:
1. Registrar em `20_decision_log.md` com rationale.
2. Atualizar `01_status_atual.md` com o novo estado.
3. Atualizar `tasks.md` do repositório impactado.
4. Registrar handoff em `05_handoff.md` com próximos passos.
