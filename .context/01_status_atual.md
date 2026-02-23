# Status Atual (snapshot)

Data: 2026-02-22

## Backend (auraxis-api)
- Bloco B4/B5/B6 concluído (recuperação de senha por link).
- Bloco de perfil V1 concluído em produção de código (`B1/B2/B3/B8/B9`).
- REST: /auth/password/forgot e /auth/password/reset.
- GraphQL: forgotPassword e resetPassword.
- Token de reset com hash + expiração + uso único.
- Reset revoga sessão ativa (current_jti).
- Testes REST/GraphQL/paridade OpenAPI atualizados.
- `TASKS.md` sincronizado na rodada atual com prioridades `PLT1 -> X4 -> X3`.
- Handoff pre-migração do backend publicado em `.context/handoffs/2026-02-22_pre-migracao-auraxis-platform.md`.

## Commits recentes (auraxis-api)
- d6f03fe fix(aws): update OIDC subject hints to auraxis-api repo name
- 33f28b0 docs(runbook): update workspace recovery procedure for auraxis-api rename
- b138d11 docs(traceability): mark path/name update task as done after rename

## Platform Setup (PLT1.3) — concluído nesta rodada

**Objetivo:** configurar ambiente multi-repo para que todos os agentes operem corretamente.

- `auraxis-app` (React Native + Expo SDK 54) registrado como submodule.
- `auraxis-web` (Nuxt 3 + TypeScript) registrado como submodule.
- Governance baseline em ambos: `CLAUDE.md`, `.gitignore`, `tasks.md`, `steering.md`.
- `scripts/setup-submodules.sh` criado — onboarding one-shot para agentes e desenvolvedores.
- `scripts/check-health.sh` atualizado:
  - Detecção correta de `.git` file vs. diretório (submodule vs. repo standalone).
  - Seção dedicada para `auraxis-app` (Mobile health) e `auraxis-web` (Web health).
  - Nome correto `auraxis-app` (não `auraxis-mobile`).
- `.context/11_repo_map.md` atualizado com mapa dos 3 submodules ativos.
- `.gitmodules` com todos os 3 submodules registrados.

## Platform Setup (PLT1.2) — concluído
- `CLAUDE.md` criado na raiz do `auraxis-platform` (directive de orquestração).
- `scripts/check-health.sh`, `bootstrap-repo.sh`, `agent-lock.sh` criados.
- `.context/agent_lock.schema.json` — schema JSON formal do protocolo de lock.
- `workflows/` populado: agent-session, feature-delivery, repo-bootstrap.
- `ai_integration-claude.md`, `ai_integration-gemini.md`, `ai_integration-gpt.md` na raiz.
- `.context/06_context_index.md` atualizado com novos artefatos.

## Platform Setup (PLT1.1) — concluído
- Repo GitHub renomeado de `flask-expenses-manager` → `auraxis-api`.
- Remote local atualizado: `git@github.com:italofelipe/auraxis-api.git`.
- `auraxis-api` registrado como git submodule em `auraxis-platform` (`.gitmodules`).
- `scripts/aws_iam_audit_i8.py`: OIDC subject hints atualizados para `auraxis-api`.
- `docs/RUNBOOK.md`: procedimento de recovery atualizado para layout de submodule.
- `docs/STABILIZATION_01_TRACEABILITY.md`: task de renomeação marcada como concluída.
- `.mypy_cache` limpo (cache tinha paths absolutos do diretório antigo).
- IAM trust policy (AWS): atualizar manualmente subject hints nos roles dev/prod. ⚠️ pendente usuário
- SonarCloud: renomear project key. ⚠️ pendente usuário

## Próximo foco

Ambiente multi-repo configurado. Os agentes podem agora:
- Clonar a platform com `git clone --recurse-submodules`
- Ou rodar `scripts/setup-submodules.sh` em clone existente
- Executar `scripts/check-health.sh` para validar o ambiente

Próximas tasks de produto:
- **X4**: adoção faseada de Ruff (advisory → substituição de flake8/black/isort) em `auraxis-api`
- **B10**: questionário indicativo de perfil investidor em `auraxis-api`
- **APP1**: setup de linting em `auraxis-app`
- **WEB1**: inicialização do projeto Nuxt 3 em `auraxis-web`

## Discovery J1..J5
- Pacote de discovery consolidado em `.context/discovery/`.
- Ordem validada: J1 -> J2 -> J3 -> J4 -> J5.
- J5 mantido como blocked até fechamento de gates regulatórios/compliance.

## Tech Debt X3/X4
- Análise e ideação formalizadas em `.context/tech_debt/`.
- Estratégia: X4 (Ruff) primeiro, em migração faseada, mantendo `mypy`. X3 (FastAPI) por coexistência faseada.
