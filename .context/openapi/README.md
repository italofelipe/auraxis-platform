# OpenAPI Snapshot

Diretório canônico com snapshot de contrato OpenAPI do backend (`auraxis-api`),
usado para geração tipada de clientes em frontend (`auraxis-web` e `auraxis-app`).

## Arquivos

- `openapi.snapshot.json`: snapshot versionado do endpoint `/docs/swagger/`.

## Como atualizar

Na raiz da platform:

```bash
bash scripts/export-openapi-snapshot.sh
```

Depois de atualizar o snapshot:

1. sincronizar web: `pnpm contracts:sync` em `repos/auraxis-web`;
2. sincronizar app: `npm run contracts:sync` em `repos/auraxis-app`;
3. validar CI local/quality-check dos dois frontends.

## Observação

Este snapshot complementa os `Feature Contract Packs` em
`.context/feature_contracts/`: packs indicam o que mudou por task, enquanto
o OpenAPI snapshot fornece a base completa para geração de tipos.
