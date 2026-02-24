# GitHub Governance

## Branch protection as code

Arquivo-fonte:

- `governance/github/branch-protection-config.json`

Aplicador via API:

- `scripts/apply-branch-protection.sh`

### Requisitos

- `curl`
- `jq`
- token com permissao de administracao de repositorio

### Variavel de ambiente

```bash
export GITHUB_ADMIN_TOKEN="<token>"
```

### Dry-run

```bash
DRY_RUN=true ./scripts/apply-branch-protection.sh
```

### Aplicar

```bash
./scripts/apply-branch-protection.sh
```

### Escopo atual

- `italofelipe/auraxis-app` em `main` e `master` (se existir)
- `italofelipe/auraxis-web` em `main` e `master` (se existir)
