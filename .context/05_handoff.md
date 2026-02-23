# Handoff (Atual)

Data: 2026-02-23 (WEB1 — Nuxt 4 init + quality stack)

## O que foi feito (rodada WEB1 — inicialização auraxis-web)

### Objetivo da rodada
Inicializar o projeto Nuxt 4 em `auraxis-web`, substituir Biome por `@nuxt/eslint`, validar `pnpm quality-check` completo e sincronizar contexto.

### Itens executados

| Item | Arquivo(s) criados/modificados | Descrição |
|:-----|:-------------------------------|:----------|
| Nuxt 4.3.1 init | `app/app.vue`, `tsconfig.json`, `pnpm-lock.yaml`, `public/` | `npx nuxi@latest init . --force --package-manager pnpm` |
| package.json restaurado | `repos/auraxis-web/package.json` | Scripts quality-check, prepare, lint, typecheck, test, test:coverage; devDeps corretas; packageManager definido |
| nuxt.config.ts criado | `repos/auraxis-web/nuxt.config.ts` | 21 módulos registrados; apollo comentado (incompatível Nuxt 4); typescript.strict=true |
| Biome removido | `lint-staged.config.js` | Migrado para `eslint --fix` (staged .ts/.tsx/.vue) + `prettier --write` (.json/.md) |
| CI atualizado | `.github/workflows/ci.yml` | npm → pnpm/action-setup; Biome → eslint; pnpm audit |
| Docs migradas | `CODING_STANDARDS.md`, `FRONTEND_GUIDE.md`, `steering.md`, `.context/quality_gates.md` | Todas as referências Biome → @nuxt/eslint + Prettier |
| 24_frontend_quality_gaps | `.context/24_frontend_quality_gaps.md` | WEB1 marcado concluído; WEB2 como próximo passo |
| better-sqlite3 | `package.json` dependencies | Peer dep obrigatória de @nuxt/content |
| eslint.config.mjs | `eslint.config.mjs` | Auto-gerado por `nuxt prepare` via @nuxt/eslint |
| quality-check verde | — | `pnpm lint ✅ pnpm typecheck ✅ pnpm test ✅` |

## O que foi validado

- `pnpm quality-check` passa com exit 0 (lint + typecheck + test) ✅
- `nuxt prepare` executa sem erros — todos os módulos compatíveis (apollo exceto) ✅
- Commit `feat(web): ...` aceito por husky + commitlint + lint-staged ✅
- Prettier reformatou .md/.json staged corretamente ✅

## Pendências manuais (ação do usuário)

| Pendência | Status | Detalhe |
|:----------|:-------|:--------|
| AWS IAM trust policy | ⚠️ Pendente | Subject hint: `repo:italofelipe/auraxis-api:environment:*` |
| SonarCloud project key | ⚠️ Pendente | Renomear de `italofelipe_flask-expenses-manager` para `italofelipe_auraxis-api` |
| Push auraxis-web ao GitHub | ⚠️ Pendente | Push dos commits `38df2ba`, `cd807f3` |
| Push auraxis-app ao GitHub | ⚠️ Pendente | Push dos commits `3eaa519`, `6cd59d1` |
| Push platform ao GitHub | ⚠️ Pendente | Push da branch `docs/agent-autonomy-baseline` |
| @nuxtjs/apollo Nuxt 4 compat | ⚠️ Bloqueado | Aguardar versão compatível; tracking em nuxt.config.ts |

## Próximo passo recomendado

**Task X4 — Ruff advisory em `auraxis-api`** (maior prioridade de produto)

```bash
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

**Alternativa — Task WEB2** (se continuar no frontend):
```bash
cd repos/auraxis-web
git checkout -b feat/web2-vitest-config
# criar vitest.config.ts com defineVitestConfig de @nuxt/test-utils/config
# configurar coverage: threshold: { lines: 85, functions: 85, branches: 85, statements: 85 }
# criar primeiro teste de componente
```

## Commits desta rodada

- `auraxis-web` `cd807f3`: `feat(web): initialize Nuxt 4 project with pnpm and full quality stack`
- `auraxis-platform` — **pendente commit** (atualização de submodule pointer + context sync)
