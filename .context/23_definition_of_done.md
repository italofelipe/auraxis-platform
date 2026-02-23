# Definition of Done (DoD) — Canônico

Este é o **único documento autoritativo** de DoD para o ecossistema Auraxis.
Todos os outros arquivos que mencionam "definição de pronto" referenciam este.

---

## DoD universal (aplica-se a qualquer tarefa, qualquer repo)

Uma tarefa está **pronta** quando todos os itens abaixo são verdadeiros:

### Implementação
- [ ] Funcionalidade implementada e operando conforme critério de aceitação definido no `tasks.md`.
- [ ] Nenhum `TODO` ou `FIXME` deixado sem issue rastreável.
- [ ] Sem código comentado sem justificativa explícita.

### Qualidade de código
- [ ] Lint sem erros (ferramenta definida por repo: Ruff/flake8/ESLint/Biome).
- [ ] Type-check sem erros (mypy em Python, tsc em TypeScript).
- [ ] Nenhuma violação de segurança nova introduzida (bandit/gitleaks/npm audit conforme stack).

### Testes
- [ ] Caminho principal coberto por teste automatizado.
- [ ] Regressões críticas cobertas (qualquer cenário que falhou historicamente).
- [ ] Todos os testes existentes passando sem skip injustificado.

### Documentação e rastreabilidade
- [ ] `tasks.md` do repo atualizado: status `Done`, commit(s) referenciado(s), data.
- [ ] Se decisão arquitetural foi tomada: entrada criada em `.context/20_decision_log.md`.
- [ ] Se contrato de API mudou: `.context/16_contract_compatibility_policy.md` consultado e seguido.
- [ ] Handoff atualizado em `.context/05_handoff.md` com o que foi feito e próximo passo.

### Revisão e merge
- [ ] Branch criada no formato `type/scope-descricao` (nunca commit direto em `master`/`main`).
- [ ] PR com descrição: objetivo, impacto, evidência de validação, risco residual.
- [ ] Pre-commit hooks passando localmente antes do push.

---

## Critérios adicionais por tipo de tarefa

### Feature de produto
- [ ] Cenário de erro tratado (o que acontece quando a operação falha).
- [ ] Contrato de API (REST/GraphQL) documentado ou atualizado no OpenAPI/schema.
- [ ] Smoke test manual ou automatizado validado em DEV.

### Débito técnico
- [ ] Comportamento externo preservado (nenhuma regressão de contrato).
- [ ] Benchmarks ou métricas antes/depois registradas (se aplicável).

### Governança / plataforma
- [ ] `.context/` atualizado refletindo o novo estado.
- [ ] `scripts/check-health.sh` passa sem falhas após a mudança.

### Hotfix / incidente
- [ ] Causa raiz documentada.
- [ ] Ação preventiva registrada no backlog (`tasks.md` ou `.context/02_backlog_next.md`).

---

## O que NÃO é parte do DoD

- Aprovação de negócio ou usuário final (é gate de release, não de DoD).
- Deploy em produção (é etapa pós-DoD, governada por `13_release_governance.md`).
- 100% de cobertura de testes (meta de evolução gradual, não gate bloqueante por padrão).

---

## Referências

- `07_steering_global.md` — princípios que motivam este DoD.
- `13_release_governance.md` — o que acontece após o DoD ser atingido.
- `15_workflow_conventions.md` — formato de branch, commit e PR.
- `12_quality_security_baseline.md` — ferramentas de qualidade por stack.
