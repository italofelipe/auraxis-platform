# Quality & Security Playbook — Auraxis Platform

> Manual operacional unificado para agentes e desenvolvedores.
> Cobre toda a stack de qualidade e segurança dos repositórios frontend do Auraxis.
> Atualizado: 2026-02-23

---

## TL;DR — regras que nunca mudam

1. **Quality gates passam antes de commitar** — sem exceção.
2. **Toda lógica nova tem teste** — antes do merge.
3. **Nenhum secret no código** — Gitleaks + TruffleHog auditam automaticamente.
4. **CVEs high/critical bloqueiam PRs** — Dependency Review Action.
5. **Coverage não regride** — web ≥ 85%, app ≥ 80%.
6. **Vitest é para web, jest-expo é para mobile** — não trocar.

---

## 1. Stack de qualidade por repositório

### auraxis-web

| Camada | Ferramenta | Versão |
|:-------|:-----------|:-------|
| Framework | Nuxt 4 (SSR) | ^4.3.1 |
| Linguagem | TypeScript strict | ^5.8 |
| Gerenciador | pnpm | 10.30.1 |
| Lint | @nuxt/eslint | 1.15.1 |
| Formatação | Prettier | ^3.8 |
| Testes unitários | Vitest + @nuxt/test-utils | ^4.0 |
| Testes E2E | Playwright | ^1.58 |
| Performance/A11y | Lighthouse CI | — |
| Análise estática | SonarCloud | — |
| Secret scan | Gitleaks + TruffleHog | — |
| Dep CVE scan | Dependency Review Action | v4 |
| Dep atualização | Dependabot | auto-merge patch/minor |

### auraxis-app

| Camada | Ferramenta | Versão |
|:-------|:-----------|:-------|
| Plataforma | React Native | 0.81.5 |
| SDK | Expo SDK | ~54.0 |
| Linguagem | TypeScript strict | ~5.9 |
| Gerenciador | npm | — |
| Lint | ESLint + eslint-config-expo | ^9.25 |
| Formatação | Prettier | ^3.8 |
| Testes unitários | **jest-expo** + @testing-library/react-native | ^54.0 / ^13.0 |
| Testes E2E | Detox (scaffold — requer macOS runner) | — |
| Análise estática | SonarCloud | — |
| Secret scan | Gitleaks + TruffleHog | — |
| Dep CVE scan | Dependency Review Action | v4 |
| Dep atualização | Dependabot | auto-merge patch; manual para RN/React minor |

> **Por que jest-expo e não Vitest no mobile?**
> Vitest não tem suporte oficial a React Native. Não existe `@vitest/react-native`.
> `vitest-react-native` (não-oficial) está abandonado — 2 anos sem manutenção, 0 dependentes.
> O ecossistema RN depende do jest-expo para: resolução de módulos `.ios.tsx`/`.android.tsx`,
> mocks do Expo SDK, e transformações específicas de plataforma. Esta decisão é irreversível
> enquanto o ecossistema React Native não oferecer suporte oficial ao Vitest.

---

## 2. Como executar os quality gates

### auraxis-web

```bash
cd repos/auraxis-web

# Comando obrigatório antes de qualquer commit:
pnpm quality-check
# Equivale a: pnpm lint && pnpm typecheck && pnpm test:coverage

# Individualmente:
pnpm lint              # ESLint (@nuxt/eslint) — 0 erros
pnpm typecheck         # nuxt typecheck — 0 erros TypeScript
pnpm test              # Vitest — todos os testes
pnpm test:coverage     # Vitest + coverage report
pnpm test:watch        # Modo watch (desenvolvimento)

# E2E (requer build):
pnpm build && pnpm test:e2e
pnpm test:e2e:ui       # Modo visual interativo
pnpm test:e2e:debug    # Debug step-by-step

# Lighthouse (requer servidor rodando):
pnpm preview &
pnpm dlx @lhci/cli autorun
```

### auraxis-app

```bash
cd repos/auraxis-app

# Comando obrigatório antes de qualquer commit:
npm run quality-check
# Equivale a: npm run lint && npm run typecheck && npm run test:coverage

# Individualmente:
npm run lint           # ESLint (eslint-config-expo, --max-warnings 0)
npm run typecheck      # tsc --noEmit — 0 erros TypeScript
npm run test           # jest-expo — todos os testes
npm run test:coverage  # jest-expo + coverage report
npm run test:watch     # Modo watch (desenvolvimento)

# Arquivo específico:
npx jest src/hooks/useBalance.test.ts

# Limpar cache (quando módulos mudam):
npx jest --clearCache

# E2E Detox (requer macOS + Xcode):
npm run detox:build:ios && npm run detox:test:ios
npm run detox:build:android && npm run detox:test:android
```

---

## 3. Thresholds de qualidade

### auraxis-web

| Gate | Threshold | Bloqueia |
|:-----|:----------|:---------|
| ESLint | 0 erros, 0 warnings | commit (lint-staged) + CI |
| TypeScript | 0 erros | commit (pre-push) + CI |
| Vitest — testes | 100% passando | CI |
| Vitest — lines | ≥ 85% | CI |
| Vitest — functions | ≥ 85% | CI |
| Vitest — statements | ≥ 85% | CI |
| Vitest — branches | ≥ 80% | CI |
| Build Nuxt | Sucesso | CI |
| Playwright E2E | 0 falhas | CI |
| Lighthouse — A11y | ≥ 90 | CI |
| Lighthouse — Perf | ≥ 80 | CI (warn) |
| LCP | ≤ 4.000 ms | CI |
| CLS | ≤ 0.1 | CI |
| Bundle public JS/CSS | ≤ 3 MB | CI (PR) |

### auraxis-app

| Gate | Threshold | Bloqueia |
|:-----|:----------|:---------|
| ESLint | 0 erros, 0 warnings | commit (lint-staged) + CI |
| TypeScript | 0 erros | commit (pre-push) + CI |
| jest-expo — testes | 100% passando | CI |
| jest-expo — lines | ≥ 80% | CI |
| jest-expo — functions | ≥ 80% | CI |
| jest-expo — statements | ≥ 80% | CI |
| jest-expo — branches | ≥ 75% | CI |
| JS bundle Android | ≤ 6 MB | CI (PR) |
| JS bundle iOS | ≤ 6 MB | CI (PR) |

---

## 4. O que deve ter teste

### auraxis-web

| O que | Obrigatório | Ferramenta |
|:------|:-----------:|:-----------|
| Composables com lógica | ✅ | Vitest |
| Stores Pinia | ✅ | Vitest |
| Utilitários (`utils/`) | ✅ | Vitest |
| Componentes com lógica condicional | ✅ | Vitest + @nuxt/test-utils |
| Serviços HTTP | ✅ | Vitest (mock de `$fetch`) |
| Fluxos críticos (login, pagamento) | ✅ | Playwright E2E |
| Páginas de apresentação estática | ⚠️ | Opcional |
| Estilos visuais | ❌ | Não testar com Vitest |

### auraxis-app

| O que | Obrigatório | Ferramenta |
|:------|:-----------:|:-----------|
| Hooks customizados (`hooks/`) | ✅ | jest-expo + renderHook |
| Utilitários (`utils/`) | ✅ | jest-expo |
| Serviços HTTP | ✅ | jest-expo (mock de `fetch`) |
| Componentes com lógica condicional | ✅ | jest-expo + @testing-library/react-native |
| Fluxos críticos (login, pagamento) | ✅ | Detox E2E (quando runner macOS disponível) |
| Componentes de apresentação pura | ⚠️ | Opcional |
| Navegação (Expo Router) | ⚠️ | Mock em jest.setup.ts |

---

## 5. Estrutura dos pipelines CI

### auraxis-web — 12 jobs

```
push / PR → master
│
├── lint              (@nuxt/eslint — 0 erros)
├── typecheck         (nuxt typecheck — 0 erros)
├── test              (vitest + coverage ≥ 85%)
│
├── build             (nuxt build — depende de lint + typecheck + test)
│   ├── bundle-analysis   (comenta tamanho no PR; hard limit 3 MB)
│   ├── lighthouse        (Perf ≥ 80, A11y ≥ 90, SEO ≥ 90, LCP ≤ 4s, CLS ≤ 0.1)
│   └── e2e               (Playwright — Chromium + mobile viewport)
│
├── secret-scan-gitleaks    (0 secrets)
├── secret-scan-trufflehog  (0 secrets validados)
├── audit             (pnpm audit --audit-level=high)
├── sonarcloud        (análise estática + coverage)
└── commitlint        (apenas em PR — Conventional Commits)

└── ci-passed         (status gate — bloqueia merge se qualquer job falhar)

Workflows adicionais:
- dependency-review.yml — bloqueia PRs com CVEs ≥ high em novas deps
- auto-merge.yml — squash-merge automático de PRs Dependabot (patch/minor)
```

### auraxis-app — 10 jobs

```
push / PR → master
│
├── lint              (ESLint — 0 erros, --max-warnings 0)
├── typecheck         (tsc --noEmit — 0 erros)
├── test              (jest-expo + coverage ≥ 80%)
│
├── expo-bundle       (export android — valida que bundle JS compila)
│   └── bundle-analysis   (comenta tamanho no PR; hard limit 6 MB)
│
├── secret-scan-gitleaks    (0 secrets)
├── secret-scan-trufflehog  (0 secrets validados)
├── audit             (npm audit --audit-level=high)
├── sonarcloud        (análise estática + coverage)
└── commitlint        (apenas em PR — Conventional Commits)

└── ci-passed         (status gate — bloqueia merge se qualquer job falhar)

# Job detox-e2e está no ci.yml mas COMENTADO.
# Requer self-hosted runner macOS + Xcode.
# Descomentar quando infra disponível.

Workflows adicionais:
- dependency-review.yml — bloqueia PRs com CVEs ≥ high em novas deps
- auto-merge.yml — squash-merge automático (patch; minor não para RN/React)
```

---

## 6. Ferramentas de segurança — visão geral

### Gitleaks
- **O que faz:** Escaneia o código-fonte e histórico Git em busca de padrões conhecidos de secrets (API keys, tokens, passwords, etc.)
- **Quando roda:** Em cada push e PR via CI (`secret-scan-gitleaks` job)
- **Configuração:** `.gitleaks.toml` (se precisar de allowlist para falsos positivos)
- **Em caso de falha:** Verificar se há secret real ou falso positivo. Se falso positivo, adicionar ao allowlist.

### TruffleHog
- **O que faz:** Detecta secrets por análise de entropia e validação ativa (verifica se o secret está realmente ativo)
- **Quando roda:** Em cada push e PR via CI (`secret-scan-trufflehog` job)
- **Complementa Gitleaks:** TruffleHog valida o secret contra APIs externas para confirmar se é real
- **Em caso de falso positivo:** Adicionar ao `.trufflehog.yml` de allowlist

### Dependency Review Action (GitHub)
- **O que faz:** Bloqueia PRs que introduzem dependências com CVEs de severidade high ou critical
- **Quando roda:** Apenas em PRs (`dependency-review.yml`)
- **Configuração:** `fail-on-severity: high` | `comment-summary-in-pr: always`
- **Licenças bloqueadas:** GPL, AGPL

### npm/pnpm audit
- **O que faz:** Verifica CVEs em TODAS as dependências instaladas (incluindo existentes)
- **Quando roda:** Em cada push via CI (`audit` job)
- **Threshold:** `--audit-level=high` — falha em high ou critical

### SonarCloud
- **O que faz:** Análise estática de código-fonte (bugs, code smells, security hotspots, duplicações)
- **Quando roda:** Em cada push e PR via CI (`sonarcloud` job)
- **Requer setup manual:**
  1. Criar organização em sonarcloud.io
  2. Importar repositório
  3. Adicionar `SONAR_TOKEN` como secret no GitHub
- **Arquivos de config:** `sonar-project.properties` em cada repo

### Dependabot
- **O que faz:** Abre PRs automáticos para atualizar dependências desatualizadas
- **Frequência:** Weekly (segunda-feira)
- **Auto-merge:** PRs de patch e minor são mergeados automaticamente SE o CI passar
- **Exceções (app):** `react-native` e `react` minor nunca são auto-mergeados (risco de quebra de native bridge)
- **Exceções gerais:** Major versions nunca são auto-mergeados

### Lighthouse CI
- **O que faz:** Mede performance, acessibilidade, SEO e Core Web Vitals em ambientes CI
- **Apenas em:** auraxis-web (não aplicável em mobile)
- **Requer:** `LHCI_GITHUB_APP_TOKEN` secret (opcional — para comentários no PR)
- **Configuração:** `.lighthouserc.yml`

---

## 7. Mocks disponíveis — auraxis-app (jest.setup.ts)

| Mock | O que faz |
|:-----|:----------|
| `expo-router` | Mock completo: `useRouter`, `useLocalSearchParams`, `Link`, `Stack`, `Tabs` |
| `expo-constants` | Mock com `expoConfig.name` e `expoConfig.slug` |
| `__mocks__/svgMock.ts` | Retorna `<View testID="svg-mock" />` |
| `__mocks__/imageMock.ts` | Retorna string `'image-mock'` |
| `@testing-library/jest-native` | Matchers extras: `toBeVisible`, `toHaveText`, etc. |

Para adicionar mock de módulo nativo:
```typescript
// jest.setup.ts
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}))
```

---

## 8. Checklist de segurança antes de commitar

```
[ ] Nenhum token, API key ou credential hardcoded
[ ] Nenhum console.log com dados de usuário (CPF, email, token, senha)
[ ] Tokens em armazenamento correto:
    - Web: httpOnly cookies (nunca localStorage)
    - App: expo-secure-store (nunca AsyncStorage)
[ ] Variáveis de ambiente no escopo correto:
    - Web: segredos em NUXT_* (não NUXT_PUBLIC_*)
    - App: segredos fora de EXPO_PUBLIC_*
[ ] .env*, .env.local, .env.production não staged (verificar .gitignore)
[ ] app.json não alterado sem aprovação (afeta bundle identifier e stores)
```

---

## 9. Setup inicial das ferramentas (ação manual necessária)

### SonarCloud

1. Acessar [sonarcloud.io](https://sonarcloud.io)
2. Criar organização vinculada ao GitHub (`italofelipe`)
3. Importar `auraxis-web` e `auraxis-app`
4. Em cada repo, copiar o `SONAR_TOKEN` gerado
5. Adicionar o token como secret no GitHub:
   - `auraxis-web` → Settings → Secrets → `SONAR_TOKEN`
   - `auraxis-app` → Settings → Secrets → `SONAR_TOKEN`

Os arquivos `sonar-project.properties` já estão configurados nos repos.

### Lighthouse CI (opcional — melhora UX do CI)

1. Instalar [Lighthouse CI GitHub App](https://github.com/apps/lighthouse-ci)
2. Autorizar nos repos desejados
3. Copiar o token gerado
4. Adicionar como secret: `LHCI_GITHUB_APP_TOKEN`

Sem o token, o CI roda normalmente mas não comenta no PR.

### GitHub — habilitar auto-merge

Para que o `auto-merge.yml` funcione:
1. Acessar Settings → General → Pull Requests
2. Habilitar "Allow auto-merge"
3. Habilitar "Automatically delete head branches"

### Branch protection — status gate obrigatório

Configurar em Settings → Branches → Add rule para `master`:
- Require status checks: adicionar `ci-passed`
- Require branches to be up to date before merging
- Do not allow bypassing the above settings

---

## 10. Troubleshooting

### auraxis-web

| Sintoma | Causa provável | Solução |
|:--------|:--------------|:--------|
| `pnpm lint` passa local, falha no CI | Node.js version diferente | Verificar `.nvmrc` ou campo `engines` |
| Coverage cai abaixo do threshold | Código novo sem teste | Escrever testes antes do merge |
| Vitest falha com erro de importação Nuxt | `.nuxt/` desatualizado | Rodar `pnpm postinstall` |
| Playwright falha no CI | Servidor não subiu a tempo | Aumentar `timeout` em `playwright.config.ts` |
| TruffleHog falsa positiva | String similar a secret | Adicionar ao `.trufflehog.yml` de allowlist |
| SonarCloud quality gate falha | Coverage caiu ou dívida técnica | Ver dashboard em sonarcloud.io |
| Lighthouse falha em A11y | Componente sem atributo aria | Verificar roles e labels nos elementos |

### auraxis-app

| Sintoma | Causa provável | Solução |
|:--------|:--------------|:--------|
| `Cannot find module 'expo-...'` em teste | Mock ausente | Adicionar mock em `jest.setup.ts` |
| `SyntaxError: Unexpected token` | Módulo ESM não transformado | Adicionar ao `transformIgnorePatterns` em `jest.config.js` |
| Coverage cai abaixo do threshold | Código novo sem teste | Escrever testes antes do merge |
| `act()` warnings | Atualização de estado assíncrona | Envolver em `act()` ou usar `waitFor()` |
| TruffleHog falsa positiva | Pattern similar a secret | Adicionar ao allowlist |
| SonarCloud quality gate falha | Coverage caiu ou dívida técnica | Ver dashboard em sonarcloud.io |
| lint-staged falha em arquivo ignorado | `--no-warn-ignored` ausente | Verificar `lint-staged.config.js` |

---

## 11. O que NÃO faz parte do gate de commit local

| Item | Por quê | Onde roda |
|:-----|:--------|:----------|
| EAS Build nativo (app) | Requer EAS cloud | CI/EAS após merge |
| EAS Update / OTA (app) | Requer aprovação | Após aprovação em produção |
| Detox E2E (app) | Requer macOS runner | CI self-hosted (quando disponível) |
| Playwright E2E (web) | Requer build | CI automático |
| Lighthouse completo (web) | Requer servidor | CI automático |
| SonarCloud (ambos) | Requer token CI | CI automático |
| Deploy (ambos) | Executado após merge | CI/CD pipeline |

---

## Referências

- Governança global: `.context/07_steering_global.md`
- Contrato de agente: `.context/08_agent_contract.md`
- Definição de pronto: `.context/23_definition_of_done.md`
- Quality gates web: `repos/auraxis-web/.context/quality_gates.md`
- Quality gates app: `repos/auraxis-app/.context/quality_gates.md`
- Steering web: `repos/auraxis-web/steering.md`
- Steering app: `repos/auraxis-app/steering.md`
