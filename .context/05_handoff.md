# Handoff (Atual)

Data: 2026-02-23 (PLT1.5 — frontend quality baseline)

## O que foi feito (rodada PLT1.5 — frontend quality baseline)

### Objetivo da rodada
Estabelecer base de qualidade de código nos repos frontend (auraxis-web e auraxis-app) equivalente ao rigor do backend (auraxis-api): manuais de codificação, pre-commit hooks, CI pipelines e documentação de gaps.

### Itens executados

| Item | Arquivo(s) criados/modificados | Descrição |
|:-----|:-------------------------------|:----------|
| CODING_STANDARDS web | `repos/auraxis-web/CODING_STANDARDS.md` | Manual canônico: TypeScript strict, Vue components (script setup), Pinia, serviços, testes Vitest, segurança, performance, naming |
| CODING_STANDARDS mobile | `repos/auraxis-app/CODING_STANDARDS.md` | Manual canônico: TypeScript strict, RN components (StyleSheet.create), hooks, Expo Router, expo-secure-store, FlatList, testes Jest, segurança |
| Pre-commit hooks app | `repos/auraxis-app/.husky/` | pre-commit (lint-staged ESLint), commit-msg (commitlint), pre-push (tsc + jest) — sintaxe husky v9 |
| Pre-commit hooks web | `repos/auraxis-web/.husky/` | pre-commit (lint-staged Biome), commit-msg (commitlint), pre-push (nuxi typecheck + vitest) — scaffold para WEB1 |
| lint-staged app | `repos/auraxis-app/package.json` | ESLint --fix em staged .ts/.tsx |
| lint-staged web | `repos/auraxis-web/package.json` | Biome check --write em staged .ts/.tsx/.vue/.json |
| commitlint app | `repos/auraxis-app/.commitlintrc.json` | Conventional Commits: 9 types, scope kebab-case, max 120 chars |
| commitlint web | `repos/auraxis-web/.commitlintrc.json` | Idêntico ao app |
| CI pipeline app | `repos/auraxis-app/.github/workflows/ci.yml` | 7 jobs: lint, typecheck, test+coverage, secret-scan (Gitleaks), dep-audit, commitlint, expo-export |
| CI pipeline web | `repos/auraxis-web/.github/workflows/ci.yml` | 7 jobs: lint (Biome), typecheck, test+coverage, build, secret-scan, dep-audit, commitlint |
| package.json scaffold web | `repos/auraxis-web/package.json` | Scripts quality-check, prepare, test:coverage prontos para WEB1 |
| Scripts app | `repos/auraxis-app/package.json` | Scripts typecheck, test:coverage, quality-check, lint:fix adicionados |
| DevDeps app | `repos/auraxis-app/package.json` | husky, lint-staged, commitlint, prettier instalados |
| Quality gaps doc | `.context/24_frontend_quality_gaps.md` | Comparativo completo backend vs frontend, gaps por prioridade (alta/média/baixa), roadmap por task |
| Status atual | `.context/01_status_atual.md` | PLT1.5 documentado, fila atualizada (APP1 → APP2) |

## O que foi validado

- `git commit` no auraxis-app: husky executou lint-staged + commitlint ✅
- Sintaxe dos hooks corrigida para husky v9 (sem shebang deprecado) ✅
- Commits em ambos os repos e no platform ✅
- `24_frontend_quality_gaps.md` criado com comparativo completo ✅

## Pendências manuais (ação do usuário)

| Pendência | Status | Detalhe |
|:----------|:-------|:--------|
| AWS IAM trust policy | ⚠️ Pendente | Subject hint: `repo:italofelipe/auraxis-api:environment:*` |
| SonarCloud project key | ⚠️ Pendente | Renomear de `italofelipe_flask-expenses-manager` para `italofelipe_auraxis-api` |
| Push auraxis-app ao GitHub | ⚠️ Pendente nesta rodada | Push dos commits `3eaa519`, `6cd59d1` |
| Push auraxis-web ao GitHub | ⚠️ Pendente nesta rodada | Push do commit `38df2ba` |
| Push platform ao GitHub | ⚠️ Pendente nesta rodada | Push dos commits na branch `docs/agent-autonomy-baseline` |
| Jest setup real (app) | ⚠️ Próxima task | APP2 — instalar jest-expo, @testing-library/react-native, coverage 80% |
| Vitest setup real (web) | ⚠️ Próxima task | WEB1 — após `npx nuxi init` |

## Próximo passo recomendado

**Task X4 — Ruff advisory em `auraxis-api`** (maior prioridade de produto)

```bash
# Início de sessão:
cd /path/to/auraxis-platform
./scripts/verify-agent-session.sh
./scripts/agent-lock.sh acquire claude auraxis-api "X4 — Ruff advisory setup"
cd repos/auraxis-api
git checkout master && git pull
git checkout -b refactor/x4-ruff-advisory
```

O que fazer:
1. Adicionar `ruff` em `requirements-dev.txt`
2. Adicionar `[tool.ruff]` em `pyproject.toml` com regras advisory (sem substituir black/isort/flake8 ainda)
3. Rodar `ruff check .` e registrar resultado (número de issues por categoria)
4. Atualizar TASKS.md com resultado e commit
5. Documentar decisão: substituição faseada ou direta

**Alternativa — Task APP2** (se preferir continuar no frontend):
```bash
./scripts/agent-lock.sh acquire claude auraxis-app "APP2 — Jest setup + testing-library"
cd repos/auraxis-app
git checkout master && git pull
git checkout -b feat/app2-jest-setup
npm install --save-dev jest-expo @testing-library/react-native @types/jest
# criar jest.config.js + testes iniciais para hooks existentes
```

## Commits desta rodada (branch docs/agent-autonomy-baseline)

- `auraxis-app` `3eaa519`: `chore(quality): add pre-commit hooks, CI pipeline, and coding standards`
- `auraxis-app` `6cd59d1`: `chore(hooks): update husky hooks to v9 syntax`
- `auraxis-web` `38df2ba`: `chore(quality): add pre-commit hooks, CI pipeline, and coding standards`
- `auraxis-platform` `4237cc9`: `docs(quality): add frontend quality gaps roadmap and advance submodule pointers`
