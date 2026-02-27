# Agentic Maturity Remediation Plan

Data: 2026-02-23
Owner: Platform Engineering (humano + agentes)

## Objetivo

Eliminar deficiências que reduzem a confiabilidade do trabalho autônomo com CrewAI, Agentic Workflows e SDD no ecossistema Auraxis.

## Deficiências identificadas

| ID | Severidade | Deficiência | Evidência | Estratégia de correção | Status |
|:---|:-----------|:------------|:----------|:------------------------|:-------|
| RM-01 | P0 | `check-health.sh` aborta no primeiro warning e não entrega diagnóstico completo | `scripts/check-health.sh` | Corrigir funções de severidade para não retornar erro sob `set -e`; adicionar detecção explícita de repo aninhado em `repos/.git` | Concluído |
| RM-02 | P1 | Política de lock inconsistente: doc diz TTL 4h, script/schema não implementam expiração | `workflows/agent-session.md`, `scripts/agent-lock.sh`, `.context/agent_lock.schema.json` | Implementar `expires_at` no lock, validação de expiração e política de stale lock | Concluído |
| RM-03 | P1 | Contrato exige handoff, mas `ai_squad` não pode escrever em `.context/handoffs` | `ai_squad/tools/tool_security.py` | Expandir allowlist para `.context/handoffs` e `.context/reports` | Concluído |
| RM-04 | P1 | Drift de nomenclatura (`auraxis-mobile` vs `auraxis-app`) em docs/workflows | `AGENTS.md`, `README.md`, `CLAUDE.md`, `workflows/*`, `.context/*` | Atualizar referências para `auraxis-app` | Concluído |
| RM-05 | P1 | Workflow de sessão contém gate web obsoleto (Biome) | `workflows/agent-session.md` | Alinhar comandos com stack real (`pnpm lint/typecheck/test:coverage`) | Concluído |
| RM-06 | P1 | Desalinhamento entre status global e tasks locais (especialmente app) | `.context/01_status_atual.md`, `repos/auraxis-app/tasks.md` | Sincronizar status e tasks com estado real do repo | Concluído |
| RM-07 | P2 | Docs do backend citam Ariadne enquanto código usa Graphene | `repos/auraxis-api/steering.md`, `repos/auraxis-api/CLAUDE.md` | Corrigir documentação para Graphene | Concluído |
| RM-08 | P2 | Nomes de secret Sonar inconsistentes entre docs e CI | `repos/*/.context/quality_gates.md`, `repos/*/.github/workflows/ci.yml` | Padronizar CI com `SONAR_AURAXIS_WEB_TOKEN` e `SONAR_AURAXIS_APP_TOKEN` | Concluído |
| RM-09 | P2 | `bootstrap-repo.sh` referencia script inexistente (`apply-templates.sh`) | `scripts/bootstrap-repo.sh` | Remover referência inválida e substituir por instrução executável | Concluído |
| RM-10 | P3 | Higiene operacional: artefatos gerados e repo aninhado em `repos/` | `repos/.git`, `repos/*/coverage`, `repos/auraxis-web/.nuxtrc` | Limpar artefatos e ajustar `.gitignore` local | Concluído |

## Plano de execução

1. Confiabilidade de scripts de orquestração (RM-01, RM-02, RM-09).
2. Coerência de governança global e workflows (RM-04, RM-05).
3. Coerência backend/CrewAI e contratos de handoff (RM-03, RM-07).
4. Coerência de CI e higiene de workspace (RM-08, RM-10).
5. Sincronização final de status/tasks (RM-06) e validação pós-correções.

## Critério de conclusão

- Scripts de plataforma executam fim-a-fim sem abortos prematuros.
- Lock de agente possui TTL implementado e comportamento documentado.
- Nenhum documento operacional crítico referencia `auraxis-mobile` quando o repo real é `auraxis-app`.
- Gates em workflow refletem comandos reais dos repos.
- Drifts de stack (Ariadne/Graphene) e secrets Sonar eliminados.
- Contexto global e tasks locais sincronizados com o estado real.

## Evidência de execução

- `./scripts/check-health.sh` executa todas as seções e retorna warnings sem abortar prematuramente.
- `AGENT_LOCK_TTL_SECONDS=1 ./scripts/agent-lock.sh acquire ...` seguido de `status` validou auto-liberação de lock expirado.
- `./scripts/verify-agent-session.sh --quiet` validado com saída silenciosa e exit code consistente.
- `rg \"auraxis-mobile\"` nos artefatos operacionais da platform sem ocorrências.
- `rg \"Ariadne\"` nos artefatos canônicos de backend sem ocorrências incorretas.
