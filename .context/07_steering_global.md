# Steering Global — Auraxis Platform

> Governança técnica global. Vinculante para todos os agentes, desenvolvedores e repositórios.
> Atualizado: 2026-02-23

---

## Missão

Entregar o produto Auraxis com previsibilidade, segurança e qualidade, usando fluxo orientado a contexto compartilhado entre humanos e agentes.

---

## Princípios imutáveis

### Entrega
- Não commitar diretamente em `master`/`main`.
- Branches e commits seguem `conventional branching` e `conventional commits`.
- Prefixo `codex/` é proibido em qualquer branch local/remota publicada.
- Commits pequenos, reversíveis e com escopo claro.
- Toda mudança relevante deve atualizar documentação de contexto.
- Toda feature com impacto de contrato deve ter teste de regressão.

### Qualidade — não negociável em nenhum repo
- **Testes não são opcionais.** Toda lógica nova tem teste antes de merge.
- **Quality gates devem passar antes de commitar.** Falha = não commitar.
- **Coverage não regride.** Nenhum PR pode baixar o threshold estabelecido.
- **Zero `any` implícito.** TypeScript strict é obrigatório em todos os projetos TS.
- **Zero erros de lint.** ESLint com `--max-warnings 0` em todos os repos frontend.

### Segurança — não negociável em nenhum repo
- **Zero secrets em código.** Nenhum token, API key ou credential hardcoded.
- **Zero secrets em logs.** `console.log` com dados de usuário é proibido em produção.
- **Armazenamento seguro obrigatório.** JWT em `expo-secure-store` (mobile) ou `httpOnly cookies` (web). Nunca `AsyncStorage` ou `localStorage`.
- **Variáveis de ambiente respeitam o escopo.** Segredos nunca em variáveis públicas (`NUXT_PUBLIC_*`, `EXPO_PUBLIC_*`).
- **Secret scan automático no CI.** Gitleaks + TruffleHog bloqueiam qualquer PR com secrets detectados.
- **CVEs bloqueados no CI.** `npm audit` / `pnpm audit` + Dependency Review Action bloqueiam high/critical.

---

## Padrões de entrega

- Ciclo preferencial: estabilização > features > débitos > refinamento > features.
- Cada bloco de trabalho precisa de:
  - objetivo
  - critérios de conclusão
  - evidência de teste
  - risco residual

---

## Definição de pronto (DoD)

Ver `23_definition_of_done.md` — documento canônico e autoritativo.
Ver também `25_quality_security_playbook.md` — referência operacional completa por repo.

---

## Quality gates por stack

| Stack | Quality gates | Arquivo de referência |
|:------|:-------------|:----------------------|
| auraxis-web (Nuxt 4 + Vitest) | lint + typecheck + test (≥85%) + build + lighthouse + e2e | `repos/auraxis-web/.context/quality_gates.md` |
| auraxis-app (RN + jest-expo) | lint + typecheck + test (≥80%) + expo-bundle + secret scan | `repos/auraxis-app/.context/quality_gates.md` |
| auraxis-api (Python + pytest) | ruff + mypy + pytest (≥80%) | `repos/auraxis-api/.context/quality_gates.md` |

Detalhe completo: `25_quality_security_playbook.md`

---

## Política de rollback

- Toda entrega deve permitir rollback por commit.
- Evitar "mega commits" com múltiplas responsabilidades.

---

## Proibições

- Reescrever histórico compartilhado sem alinhamento explícito.
- Alterar contratos públicos sem versionamento/migração.
- Introduzir acoplamento oculto entre domínios.
- Commitar código sem que os quality gates tenham passado.
- Hardcodar qualquer secret, token ou credential.
- Desabilitar ou contornar gates de qualidade (ex.: `--no-verify`, `@ts-ignore` em produção sem justificativa).
