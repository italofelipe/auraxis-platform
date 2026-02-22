# Decisões de Arquitetura (corrente)

## Multi-repo + contexto central
- Criar repo orquestrador: auraxis-platform
- Backend, web e mobile em repos separados
- Contexto compartilhado em auraxis-platform/.context

## Recomendação de stack (discussão atual)
- Web: Nuxt 4
- Mobile: React Native + Expo
- Motivo: DX, velocidade de entrega, comunidade, deploy, manutenção

## Pendente de formalização
- ADR oficial de stack web/mobile
- Estratégia de contratos compartilhados (OpenAPI/GraphQL/types)
