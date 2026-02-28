# Agent Contract — Auraxis Platform

> Contrato de comportamento obrigatório para todos os agentes que operam no ecossistema Auraxis.
> Vinculante para Claude, GPT, Gemini, CrewAI e qualquer agente futuro.
> Atualizado: 2026-02-27

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
- `.context/32_frontend_unified_guideline.md` — obrigatório para qualquer tarefa frontend (web/app)

### Guardrails anti-drift (obrigatórios antes do kickoff)

- `task_id` precisa estar resolvido (`AURAXIS_RESOLVED_TASK_ID` ou parsing válido em `tasks.md`/`TASKS.md`).
- Execução com `task_id=UNSPECIFIED` é bloqueada em preflight.
- Repo alvo deve iniciar com worktree limpo (sem staged/unstaged/untracked) para evitar contaminação de escopo.
- Branch criada pelo agente deve conter o `task_id` ativo no nome (`feat/WEB3-...`, `fix/APP4-...`, etc.).
- Se houver drift entre fingerprint de políticas globais (steering/contract/product) e o snapshot da execução, o run deve bloquear e pedir rerun sincronizado.

---

## Comportamento esperado

### Antes de escrever código
- Explicitar objetivo do bloco de trabalho
- Listar critérios de conclusão
- Identificar riscos antes de mudanças estruturais
- Verificar se existe teste para a lógica que será implementada
- Em tarefas frontend, abrir os assets de `designs/` e confirmar aderencia ao blueprint visual canonico
- Em tarefas frontend com dependência de backend recém-entregue, ler o `Feature Contract Pack` em `.context/feature_contracts/<TASK_ID>.md` antes de codificar integração.
- Confirmar `task_id` em execução e rejeitar qualquer troca implícita de task durante o mesmo bloco.
- Ao executar tarefas com feature flags, aplicar bootstrap de ambiente via `scripts/bootstrap-feature-flag-provider.sh` (ou `scripts/ai-next-task.sh`, que já injeta esse bootstrap automaticamente).

### Ao escrever código
- Seguir os padrões definidos em `CODING_STANDARDS.md` do repo
- TypeScript strict em todo código TS — zero `any` implícito
- Frontend (web/app): arquivos de código devem ser **somente TypeScript** (`.ts`/`.tsx`). `.js`/`.jsx` são proibidos para código de produto.
- Frontend (web/app): toda função deve ter tipo explícito de retorno e JSDoc obrigatório.
- Toda lógica nova vem acompanhada de teste
- Comentários explicam o "por quê", não o "o quê"
- Frontend (web/app): **proibido** usar valores arbitrários de estilo (ex.: `font-size: 1rem`, `fontWeight: 600`, `border: 1px solid #ccc`, `borderRadius: 4`). Usar somente tokens de tema e props dos componentes da UI library.
- Frontend (web/app): composables/hooks com regra de negócio devem ser modulares (`useX/index.ts`, `useX/types.ts` e arquivos por responsabilidade), sem concentrar tipos e implementação em um único arquivo.
- Frontend web: usar componentes Chakra UI (customizados com tokens Auraxis). Evitar tags HTML cruas de formulário/texto (`<input>`, `<label>`, `<button>`, `<textarea>`, `<select>`, `<p>`) em telas/componentes de produto.
- Código compartilhado entre múltiplas features/telas deve obrigatoriamente ir para diretórios shared canônicos:
  - web: `app/shared/{components,types,validators,utils}`
  - app: `shared/{components,types,validators,utils}`
- Para troca de payload estruturado entre agentes (handoff técnico), usar **TOON/1** por padrão.
  JSON é permitido apenas como fallback de compatibilidade quando TOON não for suportado.

### Política de estilo por tokens (frontend)
- Web: usar tokens/vars do tema Chakra UI (ou camada de tokens equivalente) para cores, tipografia, spacing, radius, bordas e motion.
- App: usar tokens do tema React Native Paper + mapa de tokens interno para estilos.
- Valores crus (`px`, `rem`, hex, pesos numéricos de fonte, radius numérico) só são permitidos em arquivos de definição de tema/tokens.

### Antes de commitar
- Executar `npm run quality-check` (app) ou `pnpm quality-check` (web) obrigatoriamente
- Executar `contracts:check` (diretamente ou via `quality-check`) para validar drift de OpenAPI + packs
- Se qualquer gate falhar: **corrigir antes de commitar**
- Em fluxos autônomos: não marcar `Done` sem `update_task_status` válido para o mesmo `task_id` do preflight.
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
- Em task backend com impacto de contrato (REST/GraphQL), publicar `Feature Contract Pack` (`.json` + `.md`) em `.context/feature_contracts/`.
- Em tasks frontend com integração backend, atualizar baseline/geração tipada via `contracts:sync` antes de subir PR.

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
