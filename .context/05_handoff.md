# Handoff (Atual)

Data: 2026-02-23 (Documentação de qualidade + segurança — documentação completa para agentes)

## O que foi feito (rodada atual — quality + security docs)

### Objetivo da rodada

Garantir que todos os agentes entendam e executem o processo completo de qualidade e segurança — não apenas entregam código. Documentar toda a toolchain, gates, o que testar, como rodar cada ferramenta, e decisões técnicas (Vitest vs Jest no mobile).

### Itens executados

| Item | Arquivo(s) | Descrição |
|:-----|:-----------|:----------|
| Governança global | `.context/07_steering_global.md` | Quality e security como princípios imutáveis; tabela de gates por stack; proibições expandidas |
| Contrato de agente | `.context/08_agent_contract.md` | Reescrito: checklist antes de commitar, gates obrigatórios por repo, rationale jest-expo, referências operacionais |
| Playbook unificado | `.context/25_quality_security_playbook.md` | Manual completo: stacks, como rodar gates, thresholds, o que testar, diagramas CI (12 + 10 jobs), ferramenta a ferramenta, mocks, checklist segurança, setup manual, troubleshooting |
| CODING_STANDARDS web | `repos/auraxis-web/CODING_STANDARDS.md` | Seção 10 expandida: estrutura co-localizada, exemplos Vitest + Playwright, vitest.config.ts correto |
| CODING_STANDARDS app | `repos/auraxis-app/CODING_STANDARDS.md` | Seção 9 reescrita: rationale jest-expo, jest.config.js correto, mocks table, exemplos RNTL; seção 12 reescrita: quality-check, diagrama 10 jobs |
| steering.md web | `repos/auraxis-web/steering.md` | Diagrama 12 jobs, thresholds, exemplos teste |
| steering.md app | `repos/auraxis-app/steering.md` | Diagrama 10 jobs, rationale jest-expo, exemplos RNTL |
| quality_gates.md web | `repos/auraxis-web/.context/quality_gates.md` | 12 jobs + Lighthouse + bundle + troubleshooting |
| quality_gates.md app | `repos/auraxis-app/.context/quality_gates.md` | 10 jobs + mocks table + Detox + troubleshooting |
| Context index | `.context/06_context_index.md` | 25_quality_security_playbook.md adicionado com prioridade |
| Status atual | `.context/01_status_atual.md` | Sessão documentada + decisão Vitest vs jest-expo registrada |

### Decisão técnica registrada

**Vitest NÃO é compatível com React Native.** Decisão definitiva:
- `vitest-react-native` abandonado (2 anos, 0 dependentes)
- `@testing-library/react-native` incompatível com Vitest runtime
- jest-expo é obrigatório para resolução de módulos por plataforma (`.ios.tsx`/`.android.tsx`)
- Documentado em: `08_agent_contract.md`, `25_quality_security_playbook.md`, `CODING_STANDARDS.md` do app

### Commits desta rodada

- `auraxis-web` `f5e59e0`: `docs(quality): expand agent docs with full quality + security stack`
- `auraxis-app` `52f9528`: `docs(quality): expand agent docs with full quality + security stack`
- `auraxis-platform` `9ea7641`: `docs(context): enforce quality + security as platform-wide principles`

## O que foi validado

- Commits aceitos por husky + commitlint em auraxis-web e auraxis-app ✅
- Platform commit com 5 arquivos incluindo submodule pointers avançados ✅
- Todos os docs cross-referenciam corretamente o playbook unificado ✅

## Riscos pendentes

- SonarCloud: requer setup manual (conta + SONAR_TOKEN em cada repo)
- Lighthouse CI GitHub App: requer instalação manual + LHCI_GITHUB_APP_TOKEN
- GitHub settings: auto-merge precisa ser habilitado manualmente nas configurações do repo
- Detox E2E: scaffold pronto, mas requer macOS self-hosted runner para rodar no CI

## Próximo passo sugerido

| Opção | Repo | Descrição |
|:------|:-----|:----------|
| **X4** | `auraxis-api` | Adoção faseada de Ruff — fase advisory (prioridade) |
| **WEB3/APP3** | ambos | Primeiros testes reais (componentes, hooks, composables) |
| **B10** | `auraxis-api` | Questionário de perfil investidor |

---

## Handoff anterior (WEB1 — Nuxt 4 init + quality stack)

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
