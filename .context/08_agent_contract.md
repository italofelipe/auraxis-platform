# Agent Contract — Auraxis Platform

> Contrato de comportamento obrigatório para todos os agentes que operam no ecossistema Auraxis.
> Vinculante para Claude, GPT, Gemini, CrewAI e qualquer agente futuro.
> Atualizado: 2026-02-24

---

## Objetivo

Padronizar como agentes atuam no ecossistema Auraxis — garantindo que entreguem código com qualidade, segurança e contexto adequados, não apenas funcionalidade.

---

## Input mínimo obrigatório antes de executar

Todo agente DEVE ler na ordem antes de qualquer ação:

1. `06_context_index.md` — índice de todos os arquivos de contexto
2. `07_steering_global.md` — princípios imutáveis de governança
3. `01_status_atual.md` — estado atual do projeto
4. `02_backlog_next.md` — próximas prioridades
5. `tasks.md` do repositório alvo
6. `steering.md` do repositório alvo (se existir)

Para trabalho em produto (web, app, api), também ler:
- `.context/quality_gates.md` do repo — gates obrigatórios
- `CODING_STANDARDS.md` do repo — padrões de código
- `.context/30_design_reference.md` — obrigatorio para qualquer tarefa de UI/layout em `web`/`app`

---

## Comportamento esperado

### Antes de escrever código
- Explicitar objetivo do bloco de trabalho
- Listar critérios de conclusão
- Identificar riscos antes de mudanças estruturais
- Verificar se existe teste para a lógica que será implementada
- Em tarefas frontend, abrir os assets de `designs/` e confirmar aderencia ao blueprint visual canonico

### Ao escrever código
- Seguir os padrões definidos em `CODING_STANDARDS.md` do repo
- TypeScript strict em todo código TS — zero `any` implícito
- Toda lógica nova vem acompanhada de teste
- Comentários explicam o "por quê", não o "o quê"

### Antes de commitar
- Executar `npm run quality-check` (app) ou `pnpm quality-check` (web) obrigatoriamente
- Se qualquer gate falhar: **corrigir antes de commitar**
- Verificar checklist de segurança:
  - [ ] Nenhum secret ou token hardcoded
  - [ ] Nenhum `console.log` com dados de usuário
  - [ ] Armazenamento seguro correto (secure-store / httpOnly cookies)
  - [ ] `.env*` não staged

### Ao finalizar um bloco
- Atualizar `01_status_atual.md` com o que foi feito
- Registrar decisões em `20_decision_log.md`
- Atualizar `tasks.md` do repo com próximos passos
- Registrar handoff em `05_handoff.md` se a sessão encerra
- Reportar no terminal: status final, o que foi implementado, tasks concluídas e próxima tarefa sugerida
- Em erro/bloqueio: notificar gestor e agentes paralelos no terminal, e registrar detalhe técnico em `tasks_status/<TASK_ID>.md` na platform
- `tasks_status/` é log operacional local (não versionado); o status oficial continua em `tasks.md`/`TASKS.md`

---

## Qualidade não é opcional — regras de enforcement

| Regra | Consequência de violação |
|:------|:------------------------|
| Código sem teste para lógica nova | Bloqueio de merge via CI |
| Coverage abaixo do threshold | CI falha — `ci-passed` não passa |
| Lint com erros | CI falha — `lint` job bloqueante |
| TypeScript com erros | CI falha — `typecheck` job bloqueante |
| Secret detectado | CI falha — `gitleaks` + `trufflehog` bloqueiam PR |
| CVE high/critical em nova dep | CI falha — `dependency-review` bloqueia PR |
| Bundle acima do limite | CI falha em PR (`bundle-analysis` job) |

**Agentes não devem tentar contornar gates.** Se um gate falha, o problema deve ser corrigido, não ignorado.

---

## Estrutura de saída por bloco

1. **O que foi feito** — lista concisa das mudanças
2. **O que foi validado** — gates que passaram, testes executados
3. **Riscos pendentes** — o que não foi coberto
4. **Próximo passo sugerido** — baseado no backlog e tasks.md
5. **Commits/PRs** — referências com hash

---

## Quality gates por repositório

### auraxis-web (Nuxt 4 · pnpm)

```bash
# Antes de todo commit — obrigatório:
pnpm quality-check  # = pnpm lint && pnpm typecheck && pnpm test:coverage

# Thresholds:
# Vitest: lines ≥ 85%, functions ≥ 85%, statements ≥ 85%, branches ≥ 85%
# ESLint: 0 erros (@nuxt/eslint)
# TypeScript: 0 erros (strict: true)
```

Referência completa: `repos/auraxis-web/.context/quality_gates.md`

### auraxis-app (React Native · npm · jest-expo)

```bash
# Antes de todo commit — obrigatório:
npm run quality-check  # = npm run lint && npm run typecheck && npm run test:coverage

# Thresholds:
# jest-expo: lines ≥ 85%, functions ≥ 85%, statements ≥ 85%, branches ≥ 85%
# ESLint: 0 erros (eslint-config-expo, --max-warnings 0)
# TypeScript: 0 erros (strict: true)

# ATENÇÃO: Vitest NÃO é compatível com React Native.
# O jest-expo é obrigatório — não substituir por Vitest.
```

Referência completa: `repos/auraxis-app/.context/quality_gates.md`

### auraxis-api (Python · Flask)

Ver `repos/auraxis-api/` para gates específicos.

---

## Regras de segurança operacional

- **Nunca** expor secrets em código, log ou documentação
- **Nunca** hardcodar tokens, API keys ou credentials
- Tratar arquivos temporários/sufixos acidentais (ex.: `* 2`) como artefatos descartáveis
- Não executar ações destrutivas sem instrução explícita
- Não usar `git add .` — sempre staged seletivo

---

## Governança de contexto

Ao tomar qualquer decisão relevante:
- Mudança em regra global → atualizar `07_steering_global.md`
- Mudança de arquitetura → atualizar `09_architecture_principles.md` + ADR em `20_decision_log.md`
- Mudança de prioridade → atualizar `02_backlog_next.md` e `tasks.md` do repo
- Mudança em quality gates → atualizar `quality_gates.md` do repo + este arquivo

---

## Referências operacionais

| Documento | O que contém |
|:----------|:------------|
| `25_quality_security_playbook.md` | Manual completo: como rodar gates, o que testar, setup de ferramentas |
| `23_definition_of_done.md` | Critérios de conclusão canônicos |
| `repos/auraxis-web/.context/quality_gates.md` | Gates completos do projeto web |
| `repos/auraxis-app/.context/quality_gates.md` | Gates completos do app mobile |
| `repos/auraxis-web/steering.md` | Governança técnica do projeto web |
| `repos/auraxis-app/steering.md` | Governança técnica do app mobile |
| `repos/auraxis-web/CODING_STANDARDS.md` | Padrões de código do projeto web |
| `repos/auraxis-app/CODING_STANDARDS.md` | Padrões de código do app mobile |
