# Repo Map

## Estrutura alvo
- `repos/auraxis-api`: backend e contratos de API.
- `repos/auraxis-web`: aplicação web.
- `repos/auraxis-mobile`: aplicação mobile.

## Responsabilidades por repositório
### auraxis-api
- Regras de negócio e dados.
- Contratos REST/GraphQL.
- Segurança, auditoria e integrações backend.

### auraxis-web
- UX web, navegação, estado de UI.
- Consumo dos contratos oficiais da API.
- Monitoramento de erros e telemetria de frontend.

### auraxis-mobile
- UX mobile, offline/resiliência local quando necessário.
- Consumo dos contratos oficiais da API.
- Release mobile e observabilidade mobile.

## Contratos compartilhados
- Versionamento explícito de OpenAPI/GraphQL schema.
- Tipos compartilhados quando aplicável (sem acoplamento indevido).
- Validação de compatibilidade entre repos em CI.

## Regra de ownership
Cada repo mantém seu `tasks.md`, com sincronização de prioridades globais em `.context`.
