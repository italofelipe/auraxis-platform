# Architecture Principles

## Objetivo arquitetural
Manter o produto extensível, desacoplado, testável e seguro, reduzindo custo de manutenção no crescimento multi-repo.

## Princípios
- Arquitetura orientada a domínio.
- Adapters (REST/GraphQL/UI) finos.
- Regras de negócio centralizadas em serviços/casos de uso.
- Dependências invertidas para facilitar testes.
- Contratos explícitos e versionáveis entre camadas/repos.

## Regras de desenho
- Evitar lógica de negócio em controllers/resolvers/components de borda.
- Garantir idempotência em fluxos sensíveis.
- Implementar trilha de auditoria para ações críticas.
- Tratar erros com catálogo público e sem vazamento interno.
- Preferir composição sobre herança para extensibilidade.

## Contratos e integração
- APIs públicas devem ter contrato formal (OpenAPI/GraphQL schema).
- Breaking change exige:
  - aviso no backlog
  - plano de migração
  - janela de compatibilidade quando aplicável

## Testabilidade
- Cobrir no mínimo:
  - caso feliz
  - validações
  - autorização/autenticação
  - cenários de erro esperados
- Preferir testes de contrato em fronteiras públicas.

## Estratégia de evolução
- Refatorar continuamente para manter adapters finos.
- Registrar débitos técnicos com urgência e impacto.
- Priorizar correções que reduzem risco sistêmico.
