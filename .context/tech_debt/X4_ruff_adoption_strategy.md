# X4 - Adoção de Ruff como stack principal de qualidade

## Resumo executivo
Ruff deve substituir `flake8`, `black` e `isort` de forma faseada. Tipagem estática deve continuar em `mypy` (ou migração dedicada para `pyright` em outro item), pois Ruff não substitui rigor de type-checking profundo hoje exigido no projeto.

## Estado atual observado
- Qualidade distribuída em múltiplas ferramentas: `black`, `isort`, `flake8`, `mypy`, `bandit`.
- Hooks pre-commit e CI já maduros, porém com custo de manutenção e execução maior.
- Base já possui padrão de lint/format consolidado (bom cenário para convergência).

## Objetivo técnico
- Reduzir complexidade do toolchain sem perder rigor.
- Acelerar feedback local e CI.
- Manter segurança e tipagem no mesmo nível atual.

## Escopo recomendado
### Fase 1 - Introdução sem quebra
- Adicionar Ruff em modo advisory (sem bloquear) para medir drift.
- Configurar regras equivalentes ao baseline atual.

### Fase 2 - Substituição de lint/format/import
- Tornar Ruff bloqueante para lint + format + import sort.
- Remover `flake8`, `black`, `isort` gradualmente do CI e pre-commit.

### Fase 3 - Consolidação
- Atualizar scripts de paridade local para novo fluxo.
- Revisar documentação (`steering.md`, runbooks, onboarding).

## Tipagem estática (decisão explícita)
- Manter `mypy` como gate obrigatório no curto/médio prazo.
- Avaliar `pyright` em item separado (benchmark de cobertura e falsos positivos).
- Não reduzir rigor de tipagem durante a migração de lint/format.

## Riscos principais
- Mudança simultânea de muitas regras gerando ruído de diff.
- Queda de confiança no gate se configuração inicial estiver desalinhada.

## Mitigações
- Fase advisory inicial.
- Substituição em etapas pequenas.
- Congelar mudanças de estilo durante janela de migração.

## Critérios de saída do X4 (análise)
- Matriz de equivalência de regras aprovada.
- Plano de rollout e rollback definido.
- Decisão formal: `mypy` mantido como gate de tipos.

## Recomendação final
Adotar Ruff para lint/format/import em fases e manter `mypy` como type gate obrigatório.
