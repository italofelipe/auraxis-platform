# X3/X4 Executive Snapshot

Data: 2026-02-22

## Decisão executiva
- Prioridade técnica: **X4 antes de X3**.
- Racional: X4 reduz complexidade de tooling com baixo risco arquitetural; X3 exige pré-requisitos de desacoplamento.

## X4 (Ruff)
- Objetivo: substituir `flake8`, `black`, `isort` em fases.
- Regra: manter `mypy` como gate obrigatório de tipagem neste ciclo.
- Estratégia:
  1. advisory
  2. gate parcial
  3. substituição completa de lint/format/import

## X3 (Flask -> FastAPI)
- Objetivo: migração gradual sem downtime.
- Estratégia: coexistência por prefixo/roteamento, sem big-bang.
- Pré-condições obrigatórias (fase 0):
  - auth adapter agnóstico de framework
  - context adapter (request_id/client_ip/headers)
  - camada de contrato de erro compartilhada

## No-go explícito
- Não iniciar migração de endpoints para FastAPI sem fase 0 concluída.

## Critério de reavaliação
- Após PLT1 concluído e X4 em fase estável de rollout.
