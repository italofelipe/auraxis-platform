# Status Atual (snapshot)

Data: 2026-02-22

## Backend
- Bloco B4/B5/B6 concluído (recuperação de senha por link).
- REST: /auth/password/forgot e /auth/password/reset.
- GraphQL: forgotPassword e resetPassword.
- Token de reset com hash + expiração + uso único.
- Reset revoga sessão ativa (current_jti).
- Testes REST/GraphQL/paridade OpenAPI atualizados.

## Commits recentes (backend)
- 5d092c1 feat(auth): add password reset domain state and service
- 451fa13 feat(auth): expose password reset via REST and GraphQL
- 9532375 feat(auth): wire password reset endpoints and auth policies
- 54cfae2 test(auth): cover password reset flow and openapi parity
- b860ad6 docs(tasks): link b4 b5 b6 to implementation commits

## Próximo foco
- Estruturar auraxis-platform (repo orquestrador)
- Iniciar decisão formal de stack frontend/mobile
