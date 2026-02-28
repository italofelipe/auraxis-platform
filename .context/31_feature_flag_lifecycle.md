# Feature Flag Lifecycle (PLT4.1)

Atualizado: 2026-02-28

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
- Runtime OSS (PLT4.2): `unleash` integrado com fallback local em web/app/api.
- Bootstrap por ambiente (PLT4.3): `scripts/bootstrap-feature-flag-provider.sh` + injeção automática no `scripts/ai-next-task.sh`.

## Regra de resolução em runtime

1. decisão explícita do provider remoto (`unleash`) quando disponível;
2. override de ambiente (flags por variável);
3. fallback para catálogo local versionado.

## Critérios de falha

- owner ausente;
- removeBy ausente/inválido;
- removeBy anterior a createdAt;
- flag expirada com status diferente de `removed`;
- chave duplicada;
- prefixo de chave incompatível com a plataforma.
