# Frontend Quality Gaps & Roadmap

**Data:** 2026-02-23 (atualizado: WEB1 concluído)
**Escopo:** auraxis-web (Nuxt 4) + auraxis-app (React Native/Expo)
**Referência:** `.context/23_definition_of_done.md`, `repos/*/CODING_STANDARDS.md`

---

## O que foi implementado (baseline)

### auraxis-app ✅

| Item | Estado | Arquivo |
|:-----|:-------|:--------|
| ESLint (eslint-config-expo) | ✅ ativo | `eslint.config.js` |
| TypeScript strict | ✅ configurado | `tsconfig.json` |
| Husky v9 (pre-commit, commit-msg, pre-push) | ✅ configurado | `.husky/` |
| lint-staged (ESLint fix em staged files) | ✅ configurado | `package.json#lint-staged` |
| commitlint (Conventional Commits) | ✅ configurado | `.commitlintrc.json` |
| GitHub Actions CI (7 jobs) | ✅ criado | `.github/workflows/ci.yml` |
| CODING_STANDARDS.md | ✅ criado | `CODING_STANDARDS.md` |
| FRONTEND_GUIDE.md | ✅ criado | `FRONTEND_GUIDE.md` |
| quality_gates.md | ✅ criado | `.context/quality_gates.md` |
| Jest config (scaffold) | ⚠️ pendente | Precisa `jest-expo` + config real |

### auraxis-web ✅ (WEB1 concluído — projeto Nuxt 4 inicializado)

| Item | Estado | Arquivo |
|:-----|:-------|:--------|
| Projeto Nuxt 4 inicializado | ✅ ativo | `nuxt.config.ts`, `app/app.vue` |
| package.json (pnpm) | ✅ ativo | `package.json` (packageManager: pnpm@10.30.1) |
| @nuxt/eslint | ✅ instalado | `package.json#devDependencies` + `nuxt.config.ts#modules` |
| Prettier | ✅ instalado | `package.json#devDependencies` |
| Husky v9 (pre-commit, commit-msg, pre-push) | ✅ configurado | `.husky/` |
| lint-staged (ESLint fix em staged files) | ✅ configurado | `package.json#lint-staged` |
| commitlint | ✅ configurado | `.commitlintrc.json` |
| GitHub Actions CI (7 jobs, pnpm) | ✅ atualizado | `.github/workflows/ci.yml` |
| CODING_STANDARDS.md | ✅ atualizado | `CODING_STANDARDS.md` |
| FRONTEND_GUIDE.md | ✅ atualizado | `FRONTEND_GUIDE.md` |
| nuxt.config.ts com módulos registrados | ✅ configurado | `nuxt.config.ts` |
| Vitest + @nuxt/test-utils | ⚠️ instalado, config pendente | Precisa de `vitest.config.ts` (WEB2) |
| Coverage thresholds enforcement | ⚠️ pendente | Depende de `vitest.config.ts` (WEB2) |

---

## Gaps identificados — não implementáveis agora

### 🔴 Alta prioridade (implementar em APP3/WEB3)

| Gap | Descrição | Bloqueador | Task sugerida |
|:----|:----------|:-----------|:--------------|
| **Jest setup real** (app) | `jest-expo` não está instalado + `jest.config.js` não existe | Precisa inicializar suite de testes | APP2 |
| **vitest.config.ts** (web) | Vitest instalado mas sem config de coverage thresholds | Criar `vitest.config.ts` com `defineVitestConfig` | WEB2 |
| **Coverage thresholds enforcement** | Jest/Vitest instalados, sem config de threshold real | Depende de config files | APP2/WEB2 |
| **@testing-library/react-native** | Não está nas devDeps do app | Precisa instalar + configurar | APP2 |
| **expo-secure-store** | Não está nas deps — necessário para auth segura | Instalar antes de qualquer tela de auth | APP2 |

### 🟡 Média prioridade (implementar em APP4/WEB4+)

| Gap | Descrição | Quando implementar |
|:----|:----------|:------------------|
| **SonarCloud** | Análise estática cloud (ratings A obrigatório no backend) | APP4/WEB4 — requer conta SonarCloud + token |
| **Stryker** (mutation testing) | Mutation testing para verificar qualidade dos testes | APP5/WEB5 |
| **Detox** (E2E mobile) | Testes end-to-end em device/emulator | Beta — exige emuladores no CI |
| **Playwright** (E2E web) | Testes end-to-end no browser | WEB4 |
| **Sentry** (error tracking) | Monitoramento de erros em produção | APP3/WEB3 |
| **Bundle size budget** | Bloquear CI se bundle exceder threshold | APP3/WEB3 — definir threshold primeiro |
| **React Native Performance** (Flipper/Profiler) | Gate automatizado de performance | APP5 |
| **Lighthouse CI** (web) | Performance, accessibility, SEO automatizados | WEB3 |
| **Trivy** (container scan) | Scan de imagem Docker (se houver containerização) | N/A por enquanto |

### 🟢 Baixa prioridade (fase Beta+)

| Gap | Descrição | Quando implementar |
|:----|:----------|:------------------|
| **OWASP Mobile Top 10** | Checklist de segurança mobile (equivalente ao OWASP S3 do backend) | Pré-launch |
| **EAS Build CI** | Build nativo iOS/Android no CI (caro — requer EAS paid plan) | APP5 |
| **EAS Update (OTA)** | Deploy over-the-air sem nova build | APP5 |
| **Certificate pinning** | Pinning de certificado SSL em produção | Pré-launch |
| **React Native Hermes profiling** | Gate de startup time < 2s | Beta |
| **Accessibility audit** | `@testing-library` + automated a11y checks | Beta |

---

## Comparativo backend vs frontend

| Capacidade | auraxis-api | auraxis-web | auraxis-app |
|:-----------|:-----------:|:-----------:|:-----------:|
| Lint | ✅ Flake8 | ✅ @nuxt/eslint (ativo) | ✅ ESLint |
| Format | ✅ Black | ✅ Prettier (instalado) | ✅ Prettier (instalado) |
| Type check | ✅ Mypy strict | ✅ nuxi typecheck (ativo) | ✅ tsc --noEmit |
| Pre-commit hooks | ✅ 7 hooks | ✅ 3 hooks | ✅ 3 hooks |
| Commit lint | ✅ commitlint | ✅ commitlint | ✅ commitlint |
| Tests | ✅ Pytest | ⚠️ Vitest instalado, config pendente (WEB2) | ⚠️ Jest (não configurado, APP2) |
| Coverage | ✅ 85% enforced | ⚠️ 85% (vitest.config.ts pendente) | ⚠️ 80% (jest.config.js pendente) |
| CI pipeline | ✅ 11 jobs | ✅ 7 jobs (pnpm) | ✅ 7 jobs |
| Secret scan | ✅ Gitleaks + detect-private-key | ✅ Gitleaks | ✅ Gitleaks |
| Dep audit | ✅ pip-audit | ✅ pnpm audit | ✅ npm audit |
| SAST | ✅ Bandit | ❌ gap | ❌ gap |
| Mutation testing | ✅ Cosmic Ray (0% survival) | ❌ gap | ❌ gap |
| SonarCloud | ✅ ratings A | ❌ gap | ❌ gap |
| E2E tests | ✅ Schemathesis | ❌ gap | ❌ gap |
| Container scan | ✅ Trivy | N/A | N/A |
| OWASP checks | ✅ 17 evidências | ❌ gap | ❌ gap |

**Legenda:** ✅ Implementado | ⚠️ Scaffold/Parcial | ❌ Gap

---

## Próximas ações prioritárias

### APP2 (próxima task app)
```bash
# 1. Instalar suite de testes
npm install --save-dev jest-expo @testing-library/react-native @types/jest

# 2. Criar jest.config.js
# 3. Configurar coverage thresholds (80%)
# 4. Instalar expo-secure-store
npx expo install expo-secure-store

# 5. Escrever testes iniciais para hooks e utilitários existentes
```

### WEB2 (próxima task web — config de testes)
```bash
# 1. Criar vitest.config.ts com defineVitestConfig + coverage thresholds
# 2. Instalar @testing-library/vue + happy-dom (já no package.json)
pnpm install
# 3. Escrever primeiros testes de composables e utils
# 4. Verificar que pnpm test:coverage passa com threshold 85%
```

> WEB1 ✅ concluído: projeto Nuxt 4 inicializado com pnpm, módulos registrados,
> @nuxt/eslint + Prettier configurados, husky hooks e CI atualizados.

---

*Relacionado: `23_definition_of_done.md`, `02_backlog_next.md`, `repos/*/CODING_STANDARDS.md`*
