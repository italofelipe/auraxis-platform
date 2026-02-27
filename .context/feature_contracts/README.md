# Feature Contracts (Backend -> Frontend)

Esta pasta contém pacotes de contrato gerados automaticamente pelo fluxo do backend (`ai_squad`).

## Objetivo

Dar aos agentes de frontend um artefato claro e acionável logo após a entrega backend,
reduzindo ambiguidade de integração e drift de contrato.

## Formato

Para cada task backend (ex.: `B11`) são gerados dois arquivos:

- `<TASK_ID>.json` — contrato estruturado para consumo por ferramenta/agente.
- `<TASK_ID>.md` — resumo humano para execução frontend.

## Fonte de verdade

- Contrato runtime da API: OpenAPI/GraphQL do repositório backend.
- Este diretório: handoff operacional para acelerar implementação frontend.

## Regras

- Sempre publicar pack ao fim da task backend (mesmo sem mudanças de endpoint,
  com nota explícita de "no contract change").
- Não editar manualmente packs antigos sem registrar decisão em `.context/20_decision_log.md`.
- Frontend deve ler o pack antes de iniciar integração com endpoint novo/alterado.
