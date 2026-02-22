# Tech Debt Execution Sequence (X3 + X4)

## Ordem recomendada
1. X4 (Ruff) - menor risco arquitetural e ganho rápido de DX.
2. X3 fase 0 (desacoplamentos) - preparar terreno para coexistência Flask/FastAPI.
3. X3 fase 1 (coexistência por prefixo) - iniciar migração de novos endpoints.

## Racional
- X4 entrega melhoria de fluxo sem alterar runtime.
- X3 exige pré-condições para evitar regressão sistêmica.

## Gates antes de iniciar implementação X3
- Auth adapter framework-agnostic definido.
- Error contract shared layer definida.
- Observabilidade cross-framework definida.
- ADR de coexistência aprovada.

## Definition of Ready para implementação
- Escopo por fase quebrado em tarefas pequenas e reversíveis.
- Plano de validação de contrato por rota.
- Plano de rollback por roteamento.
