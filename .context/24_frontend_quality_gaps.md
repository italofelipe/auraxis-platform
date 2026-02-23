# Frontend Quality Gaps & Roadmap

**Data:** 2026-02-23
**Escopo:** auraxis-web (Nuxt 3) + auraxis-app (React Native/Expo)
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

### auraxis-web ✅ (scaffold — aguarda WEB1)

| Item | Estado | Arquivo |
|:-----|:-------|:--------|
| package.json scaffold | ✅ criado | `package.json` |
| Husky v9 (pre-commit, commit-msg, pre-push) | ✅ scaffold | `.husky/` |
| lint-staged (Biome em staged files) | ✅ scaffold | `package.json#lint-staged` |
| commitlint | ✅ scaffold | `.commitlintrc.json` |
| GitHub Actions CI (7 jobs) | ✅ criado | `.github/workflows/ci.yml` |
| CODING_STANDARDS.md | ✅ criado | `CODING_STANDARDS.md` |
| FRONTEND_GUIDE.md | ✅ criado | `FRONTEND_GUIDE.md` |
| Biome | ⚠️ pendente instalação real | Aguarda `npx nuxi init` (WEB1) |
| Vitest + coverage | ⚠️ pendente instalação real | Aguarda WEB1 |

---

## Gaps identificados — não implementáveis agora

### 🔴 Alta prioridade (implementar em APP3/WEB3)

| Gap | Descrição | Bloqueador | Task sugerida |
|:----|:----------|:-----------|:--------------|
| **Jest setup real** (app) | `jest-expo` não está instalado + `jest.config.js` não existe | Precisa inicializar suite de testes | APP2 |
| **Vitest setup real** (web) | Vitest não instalado até WEB1 | Aguarda `npx nuxi init` | WEB1 |
| **Coverage thresholds enforcement** | Sem configuração de threshold real no Jest/Vitest ainda | Depende de Jest/Vitest setup | APP2/WEB2 |
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
| Lint | ✅ Flake8 | ✅ Biome (scaffold) | ✅ ESLint |
| Format | ✅ Black | ✅ Biome (scaffold) | ⚠️ Prettier (instalado) |
| Type check | ✅ Mypy strict | ⚠️ nuxi typecheck (scaffold) | ✅ tsc --noEmit |
| Pre-commit hooks | ✅ 7 hooks | ✅ 3 hooks (scaffold) | ✅ 3 hooks |
| Commit lint | ✅ commitlint | ✅ commitlint (scaffold) | ✅ commitlint |
| Tests | ✅ Pytest | ⚠️ Vitest (scaffold) | ⚠️ Jest (não configurado) |
| Coverage | ✅ 85% enforced | ⚠️ 85% (scaffold) | ⚠️ 80% (configuração pendente) |
| CI pipeline | ✅ 11 jobs | ✅ 7 jobs | ✅ 7 jobs |
| Secret scan | ✅ Gitleaks + detect-private-key | ✅ Gitleaks | ✅ Gitleaks |
| Dep audit | ✅ pip-audit | ✅ npm audit | ✅ npm audit |
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

### WEB1 (inicialização do projeto Nuxt)
```bash
# 1. Inicializar projeto Nuxt
npx nuxi init . --force

# 2. Instalar devDeps do package.json scaffold
npm install

# 3. Configurar Biome
npx biome init

# 4. Verificar que hooks já funcionam (estão em .husky/)
npm run prepare

# 5. Rodar quality-check completo
npm run quality-check
```

---

*Relacionado: `23_definition_of_done.md`, `02_backlog_next.md`, `repos/*/CODING_STANDARDS.md`*
