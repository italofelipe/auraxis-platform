# Contract Compatibility Policy

## Objetivo
Garantir evolução segura entre repositórios consumidores e produtores de contrato.

## Escopo
- REST/OpenAPI
- GraphQL schema
- eventos/filas (quando existirem)

## Regras
- Mudanças breaking exigem versionamento explícito e plano de migração.
- Mudanças não breaking devem manter retrocompatibilidade com clientes ativos.
- Contratos devem ser rastreáveis por versão e changelog.

## Breaking changes (exemplos)
- remover campo público
- alterar tipo de campo público
- alterar semântica sem versionar
- endurecer validação de forma incompatível sem período de transição

## Não breaking changes (exemplos)
- adicionar campo opcional
- adicionar endpoint/operação nova
- ampliar enum de forma compatível

## Checklist de PR com impacto de contrato
- [ ] Contrato atualizado (OpenAPI/schema)
- [ ] Teste de contrato ajustado
- [ ] Impacto documentado para consumidores
- [ ] Migração/rollout descritos quando necessário

## Recomendação multi-repo
- Pipeline do repo produtor deve validar consumidores críticos (quando possível).
- Publicar snapshot de contrato versionado para consumo de web/mobile.
