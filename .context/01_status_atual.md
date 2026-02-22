# Status Atual (snapshot)

Data: 2026-02-22

## Backend
- Bloco B4/B5/B6 concluído (recuperação de senha por link).
- Bloco de perfil V1 concluído em produção de código (`B1/B2/B3/B8/B9`).
- REST: /auth/password/forgot e /auth/password/reset.
- GraphQL: forgotPassword e resetPassword.
- Token de reset com hash + expiração + uso único.
- Reset revoga sessão ativa (current_jti).
- Testes REST/GraphQL/paridade OpenAPI atualizados.
- `TASKS.md` sincronizado na rodada atual com prioridades `PLT1 -> X4 -> X3`.
- Handoff pre-migração do backend publicado em `.context/handoffs/2026-02-22_pre-migracao-auraxis-platform.md`.

## Commits recentes (backend)
- 5d092c1 feat(auth): add password reset domain state and service
- 451fa13 feat(auth): expose password reset via REST and GraphQL
- 9532375 feat(auth): wire password reset endpoints and auth policies
- 54cfae2 test(auth): cover password reset flow and openapi parity
- b860ad6 docs(tasks): link b4 b5 b6 to implementation commits

## Platform Setup (PLT1.2) — concluído nesta rodada
- `CLAUDE.md` criado na raiz do `auraxis-platform` (directive de orquestração).
- `scripts/check-health.sh` — diagnóstico de saúde pré-sessão para qualquer agente.
- `scripts/bootstrap-repo.sh` — criação automatizada de novos repos com governance.
- `scripts/agent-lock.sh` — mutex de coordenação entre agentes concorrentes.
- `.context/agent_lock.schema.json` — schema JSON formal do protocolo de lock.
- `workflows/` populado: agent-session, feature-delivery, repo-bootstrap.
- `ai_integration-claude.md`, `ai_integration-gemini.md`, `ai_integration-gpt.md` na raiz.
- `.context/06_context_index.md` atualizado com novos artefatos.

## Próximo foco
- Concluir `PLT1.1`: resolver submodule do backend (remote do auraxis-api ainda aponta para flask-expenses-manager).
- Iniciar execução técnica de `X4` e, depois, `X3` fase 0.
- Iniciar `B10` (questionário indicativo de perfil investidor).

## Discovery J1..J5 (rodada atual)
- Pacote de discovery consolidado em `.context/discovery/`.
- Ordem validada: J1 -> J2 -> J3 -> J4 -> J5.
- J5 mantido como blocked até fechamento de gates regulatórios/compliance.

## Tech Debt X3/X4 (rodada atual)
- Análise e ideação formalizadas em `.context/tech_debt/`.
- Estratégia proposta:
  - X4 (Ruff) primeiro, em migração faseada, mantendo `mypy`.
  - X3 (FastAPI) por coexistência faseada com Flask, sem migração big-bang.
