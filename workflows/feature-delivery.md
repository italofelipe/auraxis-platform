# Workflow: Feature Delivery

**Gatilho:** Início de implementação de uma feature do backlog.
**Escopo:** Qualquer repo de produto (`auraxis-api`, `auraxis-web`, `auraxis-app`).

Este workflow implementa o ciclo SDD (Spec-Driven Development) para entregas
controladas por agentes.

---

## Pré-condições

- Task identificada em `tasks.md` com status `Todo` ou `In Progress`
- Sessão de agente iniciada (ver `workflows/agent-session.md`)
- Contexto lido (`.context/01_status_atual.md`, `tasks.md`, `product.md`)

---

## Fase 1 — SPEC (Especificação)

**Quem:** PO (humano) + Agente

1. PO descreve a feature em linguagem natural.
2. Agente lê o contexto relevante:
   - `tasks.md` — task ID e descrição
   - `product.md` — visão e escopo do produto
   - `.context/17_discovery_framework.md` — se for feature nova
3. Agente produz **Feature Card** usando template:
   - `repos/<repo>/.context/templates/feature_card_template.md`
4. PO valida e aprova o Feature Card.

---

## Fase 2 — ANÁLISE

**Quem:** Agente

1. Ler codebase relevante (models, services, controllers, tests).
2. Identificar:
   - Impacto em contratos existentes (REST/GraphQL)
   - Migrations de banco necessárias
   - Testes a criar ou atualizar
   - Riscos e débitos técnicos
3. Documentar análise no Feature Card.

---

## Fase 3 — REFINAMENTO

**Quem:** PO + Agente

1. Agente apresenta plano de implementação com tasks breakdown.
2. PO aprova, ajusta ou bloqueia.
3. tasks.md atualizado com status `In Progress`.

---

## Fase 4 — EXECUÇÃO

**Quem:** Agente (autônomo)

```bash
# Branch de feature
git checkout master || git checkout main
git pull
git checkout -b feat/<escopo-curto>

# Implementar em incrementos
# A cada incremento lógico:
git add <arquivos específicos>
git commit -m "feat(<escopo>): <descrição imperativa>"
```

Quality gates antes de cada commit (por repo):

```bash
# auraxis-api
black . && isort app tests config run.py run_without_db.py && flake8 app tests config run.py run_without_db.py && mypy app && pytest -m "not schemathesis" --cov=app --cov-fail-under=85

# auraxis-web
pnpm lint && pnpm typecheck && pnpm test:coverage

# auraxis-app
npm run lint && npm run typecheck && npm run test:coverage
```

Regras:
- Um commit por responsabilidade
- Testes junto com a implementação (nunca depois)
- Sem commits com quality gates falhando

---

## Fase 5 — ENTREGA

**Quem:** Agente → PO

1. Agente produz **Delivery Report** usando template:
   - `repos/<repo>/.context/templates/delivery_report_template.md`
2. Delivery Report inclui:
   - O que foi implementado
   - Testes criados/atualizados
   - Quality gates: todos passando?
   - Contrato: alguma mudança breaking?
   - Débito técnico gerado
   - Riscos residuais
3. tasks.md atualizado: status `Done`, commit hash registrado.

---

## Fase 6 — FECHAMENTO

**Quem:** PO

1. PO revisa o Delivery Report e o código.
2. PO aprova e sinaliza próxima feature.
3. Agente registra handoff em `.context/05_handoff.md`.
4. Lock liberado: `./scripts/agent-lock.sh release <agente>`

---

## Critério de saída

- [ ] Feature Card aprovado pelo PO
- [ ] Implementação funcional concluída
- [ ] Todos quality gates passando
- [ ] Sem regressão de contrato REST/GraphQL
- [ ] tasks.md atualizado com `Done` e commit hash
- [ ] Delivery Report registrado
- [ ] Handoff atualizado
- [ ] Branch aberta aguardando PR/merge
