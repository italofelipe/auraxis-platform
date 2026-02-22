# Decision Log

## 2026-02-22
- Decidido criar `auraxis-platform` como repositório orquestrador.
- Decidido manter repositórios de produto separados (`auraxis-api`, `auraxis-web`, `auraxis-mobile`).
- Decidido centralizar governança e contexto em `.context`.
- Decidido priorizar `PLT1` (configuração formal do repositório platform) antes da migração definitiva.
- Preferência atual de stack (a formalizar por ADR):
  - web: Nuxt
  - mobile: React Native + Expo

## Próximas decisões pendentes
- formalização de ADR de stack web/mobile
- política de contratos compartilhados entre repos
- estratégia de CI cross-repo para compatibilidade de contratos
