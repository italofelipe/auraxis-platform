# Steering Global

## Missão
Entregar o produto Auraxis com previsibilidade, segurança e qualidade, usando fluxo orientado a contexto compartilhado entre humanos e agentes.

## Princípios imutáveis
- Não commitar diretamente em `master`/`main`.
- Branches e commits seguem `conventional branching` e `conventional commits`.
- Commits pequenos, reversíveis e com escopo claro.
- Toda mudança relevante deve atualizar documentação de contexto.
- Toda feature com impacto de contrato deve ter teste de regressão.

## Padrões de entrega
- Ciclo preferencial: estabilização > features > débitos > refinamento > features.
- Cada bloco de trabalho precisa de:
  - objetivo
  - critérios de conclusão
  - evidência de teste
  - risco residual

## Definição de pronto (DoD)
- Implementação funcional concluída.
- Testes automatizados cobrindo cenário principal e regressões críticas.
- Lint/type-check/security gates aplicáveis sem falha.
- `tasks.md` atualizado com status e rastreabilidade.
- Handoff registrado para continuidade.

## Política de rollback
- Toda entrega deve permitir rollback por commit.
- Evitar “mega commits” com múltiplas responsabilidades.

## Proibições
- Reescrever histórico compartilhado sem alinhamento explícito.
- Alterar contratos públicos sem versionamento/migração.
- Introduzir acoplamento oculto entre domínios.
