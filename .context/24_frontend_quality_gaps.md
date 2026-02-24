# Frontend Quality Gaps & Roadmap

**Data:** 2026-02-23 (atualizado: WEB1 + APP2 + security tooling concluídos)
**Escopo:** auraxis-web (Nuxt 4) + auraxis-app (React Native/Expo)
**Referência:** `.context/23_definition_of_done.md`, `repos/*/CODING_STANDARDS.md`

---

## O que foi implementado (baseline completo)

### auraxis-app ✅

| Item | Estado | Arquivo |
|:-----|:-------|:--------|
| ESLint (eslint-config-expo) | ✅ ativo | `eslint.config.js` |
| TypeScript strict | ✅ configurado | `tsconfig.json` |
| Husky v9 (pre-commit, commit-msg, pre-push) | ✅ configurado | `.husky/` |
| lint-staged (ESLint fix em staged files) | ✅ configurado | `lint-staged.config.js` |
| commitlint (Conventional Commits) | ✅ configurado | `.commitlintrc.json` |
| jest-expo + @testing-library/react-native | ✅ instalado | `package.json#devDependencies` |
| jest.config.js (coverage ≥ 85%) | ✅ criado | `jest.config.js` |
| jest.setup.ts + mocks | ✅ criado | `jest.setup.ts`, `__mocks__/` |
| CODING_STANDARDS.md | ✅ criado | `CODING_STANDARDS.md` |
| SonarCloud config | ✅ criado | `sonar-project.properties` |
| Gitleaks secret scan | ✅ ativo | CI job `secret-scan-gitleaks` |
| TruffleHog secret scan | ✅ ativo | CI job `secret-scan-trufflehog` |
| Dependency Review (CVE block) | ✅ ativo | `.github/workflows/dependency-review.yml` |
| Dependabot (auto-update + auto-merge) | ✅ ativo | `.github/dependabot.yml` |
| Bundle size analysis (Metro) | ✅ ativo | CI job `bundle-analysis` (Android/iOS ≤ 6 MB) |
| Detox scaffold (E2E mobile) | ✅ scaffold | `.detoxrc.js`, `e2e/` |
| GitHub Actions CI (10 jobs) | ✅ atualizado | `.github/workflows/ci.yml` |

### auraxis-web ✅

| Item | Estado | Arquivo |
|:-----|:-------|:--------|
| Projeto Nuxt 4 inicializado | ✅ ativo | `nuxt.config.ts`, `app/app.vue` |
| @nuxt/eslint + Prettier | ✅ ativo | `package.json`, `eslint.config.mjs` |
| Husky v9 (pre-commit, commit-msg, pre-push) | ✅ configurado | `.husky/` |
| lint-staged | ✅ configurado | `lint-staged.config.js` |
| commitlint | ✅ configurado | `.commitlintrc.json` |
| Vitest + vitest.config.ts (coverage ≥ 85%) | ✅ criado | `vitest.config.ts` |
| Playwright (E2E) | ✅ configurado | `playwright.config.ts`, `e2e/` |
| SonarCloud config | ✅ criado | `sonar-project.properties` |
| Lighthouse CI | ✅ configurado | `.lighthouserc.yml` (perf ≥ 80, a11y ≥ 90, SEO ≥ 90) |
| Gitleaks secret scan | ✅ ativo | CI job `secret-scan-gitleaks` |
| TruffleHog secret scan | ✅ ativo | CI job `secret-scan-trufflehog` |
| Dependency Review (CVE block) | ✅ ativo | `.github/workflows/dependency-review.yml` |
| Dependabot (auto-update + auto-merge) | ✅ ativo | `.github/dependabot.yml` |
| Bundle size analysis (Nuxt) | ✅ ativo | CI job `bundle-analysis` (public ≤ 3 MB hard) |
| CODING_STANDARDS.md | ✅ atualizado | `CODING_STANDARDS.md` |
| GitHub Actions CI (12 jobs) | ✅ atualizado | `.github/workflows/ci.yml` |

---

## Gaps restantes

### 🟡 Média prioridade

| Gap | Descrição | Task | Quando |
|:----|:----------|:-----|:-------|
| **SonarCloud ativação** | Arquivo `.properties` criado, mas conta + token precisam ser configurados | Manual (usuário) | Antes do primeiro PR público |
| **Lighthouse CI GitHub App** | Token `LHCI_GITHUB_APP_TOKEN` opcional — sem ele usa `temporaryPublicStorage` | Manual (usuário) | Opcional |
| **Stryker** (mutation testing) | Mutation testing para verificar qualidade dos testes | APP5/WEB5 | Maturidade de testes |
| **Detox real** (E2E mobile) | Scaffold criado — precisa de self-hosted macOS runner + Xcode | Manual (infra) | Beta |
| **expo-secure-store** | Não está nas deps — necessário para auth segura | `npx expo install expo-secure-store` | Antes de auth screen |
| **Sentry** (error tracking) | Monitoramento de erros em produção | APP3/WEB3 | Pré-launch |

### 🟢 Baixa prioridade (fase Beta+)

| Gap | Descrição |
|:----|:----------|
| **EAS Build CI** | Build nativo iOS/Android no CI (requer EAS paid plan) |
| **EAS Update (OTA)** | Deploy over-the-air sem nova build |
| **Certificate pinning** | Pinning de certificado SSL em produção |
| **OWASP Mobile Top 10** | Checklist mobile (equivalente ao backend OWASP S3) |
| **React Native Hermes profiling** | Gate de startup time < 2s |

---

## Comparativo backend vs frontend (estado atual)

| Capacidade | auraxis-api | auraxis-web | auraxis-app |
|:-----------|:-----------:|:-----------:|:-----------:|
| Lint | ✅ Flake8 | ✅ @nuxt/eslint | ✅ ESLint |
| Format | ✅ Black | ✅ Prettier | ✅ Prettier |
| Type check | ✅ Mypy strict | ✅ nuxi typecheck | ✅ tsc --noEmit |
| Pre-commit hooks | ✅ 7 hooks | ✅ 3 hooks | ✅ 3 hooks |
| Commit lint | ✅ commitlint | ✅ commitlint | ✅ commitlint |
| Tests | ✅ Pytest | ✅ Vitest (config) | ✅ Jest (jest-expo) |
| Coverage threshold | ✅ 85% enforced | ✅ 85% (vitest.config.ts) | ✅ 85% (jest.config.js) |
| CI pipeline | ✅ 11 jobs | ✅ 12 jobs | ✅ 10 jobs |
| Secret scan | ✅ Gitleaks + detect-private-key | ✅ Gitleaks + TruffleHog | ✅ Gitleaks + TruffleHog |
| Dep audit | ✅ pip-audit | ✅ pnpm audit + dep-review | ✅ npm audit + dep-review |
| SAST (análise estática) | ✅ Bandit | ✅ SonarCloud (config) | ✅ SonarCloud (config) |
| E2E tests | ✅ Schemathesis | ✅ Playwright (scaffold) | ✅ Detox (scaffold) |
| Performance | N/A | ✅ Lighthouse CI | ⚠️ Metro bundle analysis |
| Bundle analysis | N/A | ✅ Nuxt bundle (≤ 3 MB) | ✅ Metro bundle (≤ 6 MB) |
| Dependabot | ❌ gap | ✅ auto-merge patch/minor | ✅ auto-merge (exceto RN major) |
| Dep Review (CVE) | ❌ gap | ✅ bloqueia CVE high | ✅ bloqueia CVE high |
| Mutation testing | ✅ Cosmic Ray | ❌ Stryker (pendente) | ❌ Stryker (pendente) |
| Container scan | ✅ Trivy | N/A | N/A |
| OWASP checks | ✅ 17 evidências | ❌ gap | ❌ gap |

**Legenda:** ✅ Implementado | ⚠️ Scaffold/Parcial | ❌ Gap

---

## Setup manual necessário (ação do usuário)

### SonarCloud (ambos os repos)
1. Acesse [sonarcloud.io](https://sonarcloud.io) → "+" → "Analyze new project"
2. Selecione `auraxis-web` e `auraxis-app`
3. Gere um token: My Account → Security → Generate Token
4. Adicione os secrets por repo: Settings → Secrets and variables → Actions
   - `auraxis-web` → `SONAR_AURAXIS_WEB_TOKEN`
   - `auraxis-app` → `SONAR_AURAXIS_APP_TOKEN`

### Dependabot auto-merge (ambos os repos)
1. Habilite auto-merge: Settings → General → "Allow auto-merge" = ✅
2. Configure branch protection em `master`:
   - Require status checks: `ci-passed`
   - Require branches to be up to date: ✅

### Lighthouse CI GitHub App (auraxis-web, opcional)
1. Instale: [github.com/apps/lighthouse-ci](https://github.com/apps/lighthouse-ci)
2. Copie o token gerado → adicione como `LHCI_GITHUB_APP_TOKEN` nos secrets

---

*Relacionado: `23_definition_of_done.md`, `02_backlog_next.md`, `repos/*/CODING_STANDARDS.md`*
