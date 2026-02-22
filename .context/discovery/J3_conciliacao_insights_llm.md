# J3 - Conciliacao inteligente e insights com LLM

## Problema
Mesmo com importacao, ainda existe friccao para deduplicar, categorizar e extrair insights de gasto.

## Hipotese de valor
Camada inteligente advisory reduz trabalho manual e aumenta valor percebido do produto.

## Escopo v1
- Motor de conciliacao deterministica (sem LLM) como baseline:
  - match por data/valor/descricao normalizada.
- Camada LLM advisory para:
  - sugerir duplicidades ambiguas
  - sugerir categoria
  - gerar insights de padrao de gasto
- Decisao final sempre humana (no auto-merge/auto-delete).

## Fora de escopo v1
- Acao automatica irreversivel com base em LLM.
- Recomendacao de investimento prescritiva.

## Contrato e arquitetura
- Servico de conciliacao como dominio proprio.
- LLM via adaptador isolado (provider-agnostic).
- Persistir sugestoes com status (`pending`, `accepted`, `rejected`).
- Trilha de explicacao curta por sugestao.

## Regras de negocio
- Regra deterministica tem precedencia sobre LLM.
- LLM so atua em casos ambiguos.
- Todas as sugestoes devem ser auditaveis.

## Seguranca e privacidade
- Dados enviados ao LLM minimizados e pseudonimizados quando possivel.
- Configuracao explicita de consentimento para funcionalidades de IA.
- Politica de retention para payloads e respostas.

## Observabilidade
- metricas: llm_calls_total, llm_cost_estimated, suggestion_accept_rate, false_positive_rate.
- logs de decisao sem dados sensiveis em claro.

## Criterios de aceite
- Conciliacao deterministica cobre casos obvios com acuracia alta.
- Sugestoes LLM aparecem com explicacao e requerem confirmacao manual.
- Usuario consegue aceitar/rejeitar sugestoes e sistema aprende historico de decisoes.
- Politicas de privacidade/consentimento estao aplicadas no fluxo.

## Riscos e mitigacao
- Risco: falso positivo de duplicidade.
  - Mitigacao: advisory-only + confirmacao humana obrigatoria.
- Risco: custo de inferencia.
  - Mitigacao: thresholds + batching + limites por usuario/plano.
- Risco: compliance/LGPD.
  - Mitigacao: minimizacao de dados e consentimento explicito.

## Dependencias
- J2 implementado (dados importados disponiveis).
- Definicao de provider e politica de custo.

## Estimativa
- Complexidade: alta
- Urgencia: media/alta
- Recomendacao: iniciar discovery tecnico detalhado ao concluir J2.
