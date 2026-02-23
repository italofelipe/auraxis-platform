# Status Atual (snapshot)

Data: 2026-02-23

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

## PLT1.4 — Governança e calibragem de agentes (concluído nesta rodada)

**Objetivo:** deixar Claude, Gemini e GPT completamente autônomos, com guardrails que impeçam regressão, vazamento e desvio de padrão.

### O que foi feito

| Item | Arquivo(s) | Descrição |
|:-----|:-----------|:----------|
| Quality gates web | `repos/auraxis-web/steering.md` | Biome + nuxi typecheck + vitest — comandos concretos e thresholds |
| Quality gates mobile | `repos/auraxis-app/steering.md` | ESLint + tsc --noEmit + jest — comandos concretos e thresholds |
| Contexto local web | `repos/auraxis-web/.context/` | README, architecture.md, quality_gates.md |
| Contexto local mobile | `repos/auraxis-app/.context/` | README, architecture.md, quality_gates.md |
| Lock obrigatório | `workflows/agent-session.md` | Tabela explícita: quando acquire é obrigatório vs. opcional |
| Gates por repo no workflow | `workflows/agent-session.md` | Comandos de gate por stack embutidos no passo de commit |
| Script de prereqs | `scripts/verify-agent-session.sh` | Valida git, SSH, Python, submodules, .context antes de começar |
| Handoffs históricos | `.context/handoffs/` | Diretório criado + protocolo documentado |
| Interop CrewAI | `repos/auraxis-api/ai_squad/CLAUDE.md` | Protocolo de lock e handoff para o squad automatizado |

### Commits desta rodada (platform)

- `docs/agent-autonomy-baseline` — branch com todos os itens acima

---

## Próxima task para agentes autônomos

> **Esta seção deve ser atualizada ao final de cada sessão.** É o ponto de entrada para qualquer agente que começa uma nova sessão sem contexto anterior.

### Agora — tarefa imediata

| Campo | Valor |
|:------|:------|
| **Task ID** | `X4` |
| **Repo** | `auraxis-api` |
| **Descrição** | Adoção faseada de Ruff — fase advisory (adicionar Ruff sem remover black/isort/flake8 ainda) |
| **Branch** | `refactor/x4-ruff-advisory` |
| **Entrada** | `master` de `auraxis-api` — commits recentes em `d6f03fe`, `33f28b0`, `b138d11` |
| **Critério de saída** | Ruff instalado, configurado em `pyproject.toml`, rodando sem erros em modo advisory, resultado documentado em TASKS.md |
| **Risco** | Baixo — advisory não substitui nada, apenas adiciona |

> ⚠️ **WEB1 concluído** (2026-02-23): Nuxt 4.3.1 inicializado com pnpm@10.30.1, @nuxt/eslint substituiu Biome, quality-check verde. Próxima task web: **WEB2** (vitest.config.ts + coverage ≥ 85%).

### Fila (ordem de prioridade)

| # | Task | Repo | Descrição curta |
|:--|:-----|:-----|:----------------|
| 1 | `X4` | `auraxis-api` | Ruff advisory |
| 2 | `X3` | `auraxis-api` | Flask/FastAPI coexistence fase 0 |
| 3 | `B10` | `auraxis-api` | Questionário de perfil investidor (5-10 perguntas) |
| 4 | `APP2` | `auraxis-app` | Jest setup real (jest-expo + coverage thresholds + @testing-library/react-native) |
| 5 | `WEB2` | `auraxis-web` | vitest.config.ts com defineVitestConfig + coverage ≥ 85% |

---

## PLT1.5 — Frontend quality baseline (concluído nesta rodada)

**Objetivo:** estabelecer base de qualidade nos repos frontend equivalente ao rigor do backend.

### O que foi feito

| Item | Arquivo(s) | Descrição |
|:-----|:-----------|:----------|
| CODING_STANDARDS.md web | `repos/auraxis-web/CODING_STANDARDS.md` | Manual canônico: TypeScript, Vue components, Pinia, serviços, testes, segurança |
| CODING_STANDARDS.md mobile | `repos/auraxis-app/CODING_STANDARDS.md` | Manual canônico: TypeScript, RN components, hooks, Expo Router, segurança |
| Pre-commit hooks app | `repos/auraxis-app/.husky/` | pre-commit (lint-staged), commit-msg (commitlint), pre-push (tsc+jest) |
| Pre-commit hooks web | `repos/auraxis-web/.husky/` | pre-commit (lint-staged), commit-msg (commitlint), pre-push (nuxi+vitest) |
| lint-staged config | ambos repos | ESLint fix (app) / Biome check (web) em staged files |
| commitlint config | ambos repos | Conventional Commits com types explícitos |
| CI pipeline app | `repos/auraxis-app/.github/workflows/ci.yml` | 7 jobs: lint, typecheck, test+coverage, secret-scan, dep-audit, commitlint, expo-export |
| CI pipeline web | `repos/auraxis-web/.github/workflows/ci.yml` | 7 jobs: lint, typecheck, test+coverage, build, secret-scan, dep-audit, commitlint |
| Quality gaps doc | `.context/24_frontend_quality_gaps.md` | Comparativo completo backend vs frontend, gaps por prioridade, roadmap de implementação |
| package.json scaffold web | `repos/auraxis-web/package.json` | Scripts prontos para WEB1 (prepare, quality-check, typecheck, test:coverage) |
| Scripts app | `repos/auraxis-app/package.json` | typecheck, test:coverage, quality-check, lint:fix adicionados |

### Gaps documentados (não implementáveis agora)
Ver `.context/24_frontend_quality_gaps.md` para roadmap completo.
Principais gaps: Jest setup real (APP2), Vitest config (WEB2), SonarCloud (APP4/WEB4), Stryker (APP5/WEB5), Detox E2E (Beta).

### Commits desta rodada
- `auraxis-app`: `3eaa519`, `6cd59d1` (quality baseline + hook syntax fix)
- `auraxis-web`: `38df2ba` (quality baseline scaffold)
- `auraxis-platform`: `4237cc9` (gap doc + submodule pointers)

---

## WEB1 — Inicialização Nuxt 4 + quality stack (concluído 2026-02-23)

**Objetivo:** Inicializar o projeto auraxis-web com Nuxt 4, substituir Biome por @nuxt/eslint e validar quality-check completo.

### O que foi feito

| Item | Arquivo(s) | Descrição |
|:-----|:-----------|:----------|
| Nuxt 4 init | `nuxt.config.ts`, `app/app.vue`, `tsconfig.json`, `pnpm-lock.yaml` | `nuxi init . --force` com pnpm@10.30.1 |
| 21 módulos registrados | `nuxt.config.ts` | @nuxt/eslint, @nuxt/image, @nuxt/content, @pinia/nuxt, @pinia/colada-nuxt, @nuxtjs/i18n, @nuxtjs/seo, @nuxt/ui, e mais |
| Apollo comentado | `nuxt.config.ts` | `@nuxtjs/apollo@4.0.1-rc.5` incompatível com Nuxt 4 — aguarda versão compatível |
| Biome → @nuxt/eslint | `lint-staged.config.js`, `eslint.config.mjs`, `package.json` | Migração completa — ESLint é o linter oficial Nuxt |
| Docs atualizadas | `steering.md`, `CODING_STANDARDS.md`, `FRONTEND_GUIDE.md`, `.context/quality_gates.md` | Todas as referências a Biome substituídas por @nuxt/eslint + Prettier |
| quality-check validado | `package.json` scripts | `pnpm lint ✅ pnpm typecheck ✅ pnpm test ✅` |
| better-sqlite3 adicionado | `package.json` | Peer dep obrigatória de @nuxt/content |

### Commits desta rodada
- `auraxis-web` `cd807f3`: `feat(web): initialize Nuxt 4 project with pnpm and full quality stack`
