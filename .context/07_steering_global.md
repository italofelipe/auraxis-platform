# Steering Global — Auraxis Platform

> Governança técnica global. Vinculante para todos os agentes, desenvolvedores e repositórios.
> Atualizado: 2026-02-27

---

## Missão

Entregar o produto Auraxis com previsibilidade, segurança e qualidade, usando fluxo orientado a contexto compartilhado entre humanos e agentes.

---

## Princípios imutáveis

### Entrega
- Não commitar diretamente em `master`/`main`.
- Branches e commits seguem `conventional branching` e `conventional commits`.
- Prefixo `codex/` é proibido em qualquer branch local/remota publicada.
- Em execução autônoma, cada branch deve conter o `task_id` ativo no nome (anti-drift).
- Commits pequenos, reversíveis e com escopo claro.
- Toda mudança relevante deve atualizar documentação de contexto.
- Toda feature com impacto de contrato deve ter teste de regressão.
- Toda feature backend com impacto de contrato deve publicar `Feature Contract Pack` em `.context/feature_contracts/` para consumo dos frontends.
- Bootstrap de feature flags por ambiente deve usar o script central `scripts/bootstrap-feature-flag-provider.sh` (PLT4.3), evitando configuração ad-hoc por repo.
- Execução autônoma só inicia com `task_id` resolvido (nunca `UNSPECIFIED`) e worktree limpo.
- Se houver drift de contexto (fingerprint de política), execução deve falhar em preflight.
- Execução autônoma multi-repo deve usar worktree efêmero por child (baseado em `origin/<default>`) para impedir escrita direta no clone base.
- Preparação de repositório antes do run deve normalizar para branch default (`main`/`master`) e sincronizar com `origin` antes de qualquer dispatch.

### Qualidade — não negociável em nenhum repo
- **Testes não são opcionais.** Toda lógica nova tem teste antes de merge.
- **Quality gates devem passar antes de commitar.** Falha = não commitar.
- **Coverage não regride.** Nenhum PR pode baixar o threshold estabelecido.
- **Zero `any` implícito.** TypeScript strict é obrigatório em todos os projetos TS.
- **TypeScript-only em frontend.** Código de produto em web/app deve usar `.ts`/`.tsx` (sem `.js`/`.jsx` para features).
- **Funções explícitas e documentadas.** Toda função de frontend deve ter retorno explícito e JSDoc.
- **Composables/hook modulares.** Lógica de negócio em frontend deve usar estrutura por módulo (`index.ts` + `types.ts` + arquivos por responsabilidade), evitando arquivos monolíticos.
- **Zero erros de lint.** ESLint com `--max-warnings 0` em todos os repos frontend.
- **Stack de UI padronizada.** Web usa Chakra UI customizado e app usa React Native Paper (ou ADR substituta); Tailwind é proibido em ambos.
- **Design system único.** Paleta oficial (`#262121`, `#ffbe4d`, `#413939`, `#0b0909`, `#ffd180`, `#ffab1a`), tipografia (`Playfair Display` + `Raleway`) e grid base de 8px.
- **Shared-first para reutilização.** Código frontend reutilizado deve viver em diretórios shared canônicos:
  - web: `app/shared/{components,types,validators,utils}`
  - app: `shared/{components,types,validators,utils}`
- **Guideline frontend unificado.** Web e app devem seguir os mesmos conceitos arquiteturais, gates e convenções descritos em `.context/32_frontend_unified_guideline.md`, com variação apenas de camada/plataforma.
- **Contrato tipado obrigatório.** Frontend deve manter tipos OpenAPI gerados e baseline de `Feature Contract Pack` em CI (`contracts:check` bloqueante).
- **PR checklist obrigatório.** Todo repo de produto deve manter template de PR com checklist de validação, contratos e riscos.

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
| auraxis-app (RN + jest-expo) | lint + typecheck + test (≥85%) + expo-bundle + secret scan | `repos/auraxis-app/.context/quality_gates.md` |
| auraxis-api (Python + pytest) | ruff + mypy + pytest (≥85%) | `repos/auraxis-api/.context/quality_gates.md` |

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
