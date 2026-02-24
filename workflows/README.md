# Workflows — Auraxis Platform

Automações e pipelines de orquestração entre repositórios.

## Estrutura

```
workflows/
  README.md                    # Este arquivo
  agent-session.md             # Protocolo de sessão para agentes
  feature-delivery.md          # Fluxo completo de entrega de feature
  repo-bootstrap.md            # Processo de bootstrap de novo repo
```

## Princípio

Workflows são **documentos executáveis** — descrevem passo a passo o que
um agente (ou humano) deve fazer em cada contexto operacional.

Cada workflow tem:
- **Gatilho**: quando usar
- **Pré-condições**: o que deve estar verdadeiro antes
- **Passos**: sequência de ações com comandos concretos
- **Critério de saída**: como saber que terminou

## Referências

- `.context/07_steering_global.md` — governança e princípios
- `.context/15_workflow_conventions.md` — convenções de branch e commit
- `scripts/` — utilitários de execução
