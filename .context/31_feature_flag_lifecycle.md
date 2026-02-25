# Feature Flag Lifecycle (PLT4.1)

Atualizado: 2026-02-25

## Estados

1. `draft`
2. `enabled-dev`
3. `enabled-staging`
4. `enabled-prod`
5. `cleanup-pending`
6. `removed`

## Metadados obrigatórios

- `key`
- `owner`
- `createdAt` (`YYYY-MM-DD`)
- `removeBy` (`YYYY-MM-DD`)
- `type` (`release`, `experiment`, `kill-switch`)
- `status`

## Enforcement implementado

- Web: `scripts/check-feature-flags.cjs` + job `Feature Flags Hygiene` no CI.
- App: `scripts/check-feature-flags.cjs` + job `Feature Flags Hygiene` no CI.
- API: `scripts/check_feature_flags.py` + step `Feature Flags Hygiene` no job `quality`.

## Critérios de falha

- owner ausente;
- removeBy ausente/inválido;
- removeBy anterior a createdAt;
- flag expirada com status diferente de `removed`;
- chave duplicada;
- prefixo de chave incompatível com a plataforma.
