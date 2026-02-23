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

Ver `23_definition_of_done.md` — documento canônico e autoritativo.
Não duplicar critérios aqui.

## Política de rollback
- Toda entrega deve permitir rollback por commit.
- Evitar “mega commits” com múltiplas responsabilidades.

## Proibições
- Reescrever histórico compartilhado sem alinhamento explícito.
- Alterar contratos públicos sem versionamento/migração.
- Introduzir acoplamento oculto entre domínios.
