# Frontend Unified Guideline (Web + App)

Atualizado: 2026-02-27

## Objetivo

Garantir que `auraxis-web` (Nuxt) e `auraxis-app` (React Native) evoluam com
arquitetura, governança e padrões praticamente equivalentes, respeitando
peculiaridades de plataforma.

## Regras canônicas compartilhadas

- TypeScript-only em código de produto (`.ts/.tsx` no app, `.ts/.vue` no web).
- Lint zero warnings + typecheck estrito + cobertura mínima 85%.
- JSDoc obrigatório em funções de código de produto.
- Sem valores visuais arbitrários (cores, spacing, radius, font-size/weight/line-height).
  Tudo por tokens/tema.
- Tema/tokens em arquitetura modular obrigatória:
  - arquivos dedicados por domínio (`colors`, `typography`, `spacing`, `radii`, `shadows`, `motion`);
  - `index.ts` apenas como barrel/export aggregator (sem concentrar definições).
- Reuso obrigatório via diretórios shared canônicos:
  - web: `app/shared/{components,types,validators,utils}`
  - app: `shared/{components,types,validators,utils}`
- Fluxo de dados remoto com TanStack Query.
- Form validation tipada (schema-first).
- Segurança de sessão por contrato backend (nunca hardcode de auth behavior no frontend).

## Arquitetura-alvo (isomorfismo conceitual)

| Conceito | Web (Nuxt) | App (React Native) |
|---|---|---|
| Routing | `app/pages` | `app/` (Expo Router) |
| Shared UI | `app/shared/components` | `shared/components` |
| Domain hooks | `app/composables` | `hooks/` |
| HTTP client | `app/services` | `lib/` / `services` |
| Theme tokens | `app/theme` + vars/tokens | `config/design-tokens.ts` + `config/paper-theme.ts` |
| Global state | `pinia` (quando necessário) | `zustand` (ContextAPI vetado para estado global) |

## UI Libraries (obrigatório)

- Web: Chakra UI (ou equivalente aprovado por ADR), com wrappers internos.
- App: React Native Paper, com wrappers internos.
- Em ambos: preferir componentes da library antes de elementos base.

## Backend handoff obrigatório

Toda task backend concluída deve publicar `Feature Contract Pack` em:

- `.context/feature_contracts/<TASK_ID>.json`
- `.context/feature_contracts/<TASK_ID>.md`

Antes de implementar integração, agentes frontend devem:

1. listar packs disponíveis;
2. ler pack relacionado;
3. implementar integração conforme contrato (auth, erros, exemplos, rollout notes).

## Gates de contrato (obrigatórios em web/app)

- `contracts:sync`: atualiza snapshot OpenAPI, tipos gerados e baseline de packs.
- `contracts:check`: bloqueia drift de contrato no CI/local parity.
- `Contract Smoke` em CI deve ser check obrigatório para merge.
- Template de PR deve conter checklist explícito de contrato e validação.

### Payload mínimo esperado no pack

- `rest_endpoints`: lista de rotas REST alteradas/criadas.
- `graphql_endpoints`: lista de operações GraphQL alteradas/criadas.
- `auth`: regra de autenticação/sessão.
- `error_contract`: semântica de erro para UX e retries.
- `examples`: exemplos curtos request/response.
- `notes`: observações de rollout, retrocompatibilidade e flags.

## Exceções

Exceções só por ADR/decision log. Sem ADR, a regra padrão é bloqueante.
