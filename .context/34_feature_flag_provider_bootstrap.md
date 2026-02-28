# Feature Flag Provider Bootstrap (PLT4.3)

Atualizado: 2026-02-28

## Objetivo

Centralizar o bootstrap operacional de provider de feature flags por ambiente (`development`, `staging`, `production`) para `auraxis-api`, `auraxis-web` e `auraxis-app`.

## Script canônico

- `scripts/bootstrap-feature-flag-provider.sh`

Esse script emite variáveis de ambiente já normalizadas para:

1. namespace canônico cross-repo (`AURAXIS_*`);
2. namespace web (`NUXT_PUBLIC_*`);
3. namespace app (`EXPO_PUBLIC_*`).

## Como usar

### Emitir exports (shell)

```bash
./scripts/bootstrap-feature-flag-provider.sh --environment development --format shell
```

### Emitir formato `.env`

```bash
./scripts/bootstrap-feature-flag-provider.sh --environment staging --format env
```

### Forçar provider

```bash
./scripts/bootstrap-feature-flag-provider.sh \
  --environment production \
  --provider unleash \
  --unleash-url https://unleash.company.internal \
  --format shell
```

## Integração automática no fluxo de agentes

`scripts/ai-next-task.sh` executa bootstrap automático quando:

- `AURAXIS_FEATURE_FLAGS_BOOTSTRAP=true` (default);
- `AURAXIS_FEATURE_FLAGS_ENV=<development|staging|production>` (default `development`);
- `AURAXIS_FEATURE_FLAGS_PROVIDER` opcional para override.

## Matriz padrão

| Ambiente | Provider padrão |
|:---------|:----------------|
| `development` | `local` |
| `staging` | `unleash` |
| `production` | `unleash` |

## Contrato de fallback por runtime

- API: usa `AURAXIS_*`.
- Web: usa `NUXT_PUBLIC_*` e fallback para `AURAXIS_*`.
- App: usa `EXPO_PUBLIC_*` e fallback para `AURAXIS_*`.

Isso reduz drift de configuração entre plataformas e simplifica execução paralela de agentes.
