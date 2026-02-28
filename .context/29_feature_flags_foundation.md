# Feature Flags Foundation (PLT4)

Atualizado: 2026-02-28

## Objetivo

Padronizar governança de feature toggles para permitir rollout seguro e previsível em web/app/api.

## Diretriz de stack

- Provider OSS alvo: `unleash` (design OpenFeature-compatible).
- Runtime padrão por repo: `provider remoto -> override env -> catálogo local`.
- Antes da integração runtime, todo repo deve manter catálogo versionado de flags.

## Runtime canônico (PLT4.2)

Integração publicada nos três repos:

- API: `repos/auraxis-api/app/utils/feature_flags.py`
- Web: `repos/auraxis-web/app/shared/feature-flags/service.ts`
- App: `repos/auraxis-app/shared/feature-flags/service.ts`

Contrato mínimo de ambiente:

- `<STACK>_FLAG_PROVIDER` = `local` | `unleash`
- `<STACK>_UNLEASH_PROXY_URL`/`AURAXIS_UNLEASH_URL`
- `<STACK>_UNLEASH_*` (app/instance/environment/key/token)
- cache TTL curto para snapshot remoto

## Catálogos canônicos por repositório

- `repos/auraxis-web/config/feature-flags.json`
- `repos/auraxis-app/config/feature-flags.json`
- `repos/auraxis-api/config/feature-flags.json`

## Guardrails mínimos

- Toda flag deve ter owner.
- Toda flag deve ter `createdAt` e `removeBy`.
- Flag expirada sem remoção deve falhar em CI.
- Prefixo por plataforma obrigatório: `web.`, `app.`, `api.`.
