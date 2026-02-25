# Feature Flags Foundation (PLT4)

Atualizado: 2026-02-25

## Objetivo

Padronizar governança de feature toggles para permitir rollout seguro e previsível em web/app/api.

## Diretriz de stack

- Provider OSS alvo: Unleash (design OpenFeature-compatible).
- Antes da integração runtime, todo repo deve manter catálogo versionado de flags.

## Catálogos canônicos por repositório

- `repos/auraxis-web/config/feature-flags.json`
- `repos/auraxis-app/config/feature-flags.json`
- `repos/auraxis-api/config/feature-flags.json`

## Guardrails mínimos

- Toda flag deve ter owner.
- Toda flag deve ter `createdAt` e `removeBy`.
- Flag expirada sem remoção deve falhar em CI.
- Prefixo por plataforma obrigatório: `web.`, `app.`, `api.`.
