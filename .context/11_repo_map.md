# Repo Map

Última atualização: 2026-02-23

## Submodules registrados

| Repo | Path | Remote | Stack | Status |
|:-----|:-----|:-------|:------|:-------|
| auraxis-api | `repos/auraxis-api` | `git@github.com:italofelipe/auraxis-api.git` | Python + Flask | ativo |
| auraxis-app | `repos/auraxis-app` | `git@github.com:italofelipe/auraxis-app.git` | React Native + Expo SDK 54 | bootstrap |
| auraxis-web | `repos/auraxis-web` | `git@github.com:italofelipe/auraxis-web.git` | Nuxt 4.3.1 + TypeScript + @nuxt/eslint | ativo |

## Como clonar a platform completa

```bash
# Clone da platform com todos os submodules
git clone --recurse-submodules git@github.com:italofelipe/auraxis-platform.git

# Se já clonou sem submodules
git submodule update --init --recursive
```

## Estrutura alvo

```
auraxis-platform/
  repos/
    auraxis-api/   # Backend: regras de negócio, API REST/GraphQL, segurança
    auraxis-app/   # Mobile: React Native + Expo (iOS + Android)
    auraxis-web/   # Web: Nuxt 4 (SPA/SSR)
  .context/        # Governança compartilhada entre todos os repos
  scripts/         # Automação de plataforma
  workflows/       # Protocolos de agentes e entrega
```

## Responsabilidades por repositório

### auraxis-api
- Regras de negócio e dados.
- Contratos REST/GraphQL.
- Segurança, auditoria e integrações backend.
- Stack: Python 3.13, Flask, SQLAlchemy, Alembic, Celery.

### auraxis-app
- UX mobile (iOS e Android).
- Navegação com Expo Router (file-based).
- Consumo dos contratos oficiais da API.
- Stack: React Native 0.81, Expo SDK 54, TypeScript.

### auraxis-web
- UX web, navegação, estado de UI.
- Consumo dos contratos oficiais da API.
- Stack: Nuxt 4.3.1, TypeScript, @nuxt/eslint, Vitest, Playwright.

## Contratos compartilhados

- Versionamento explícito de OpenAPI / GraphQL schema (definidos em `auraxis-api`).
- Tipos compartilhados quando aplicável — sem acoplamento indevido entre repos.
- Validação de compatibilidade de contrato em CI (planejado).

## Regra de ownership

Cada repo mantém seu próprio `tasks.md` e `CLAUDE.md`.
Sincronização de prioridades globais ocorre em `.context/02_backlog_next.md`.
Decisões de arquitetura transversais ficam em `.context/03_decisoes_arquitetura.md`.
