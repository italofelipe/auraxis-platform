# Handoff (Atual)

Data: 2026-02-23 (PLT1.4 — agent autonomy baseline)

## O que foi feito (rodada PLT1.4)

### Objetivo da rodada
Configurar o ambiente para que Claude, Gemini e GPT consigam operar completamente autônomos, seguindo padrões, guardrails e entregando código robusto e confiável.

### Itens executados

| Item | Arquivo(s) criados/modificados | Descrição |
|:-----|:-------------------------------|:----------|
| Quality gates web | `repos/auraxis-web/steering.md` | Biome + nuxi typecheck + vitest com thresholds explícitos |
| Quality gates mobile | `repos/auraxis-app/steering.md` | ESLint + tsc --noEmit + jest com thresholds explícitos |
| Contexto local web | `repos/auraxis-web/.context/README.md`, `architecture.md`, `quality_gates.md` | Stack, estrutura, decisões, gates para agentes no repo web |
| Contexto local mobile | `repos/auraxis-app/.context/README.md`, `architecture.md`, `quality_gates.md` | Stack, estrutura, decisões, gates para agentes no repo mobile |
| Lock sem ambiguidade | `workflows/agent-session.md` | Reescrito: tabela de "quando acquire é obrigatório", gates por repo no passo de commit |
| Script de prereqs | `scripts/verify-agent-session.sh` | Novo script: valida git, SSH, Python, scripts, submodules, .context, CLAUDE.md, agent lock |
| Handoffs históricos | `.context/handoffs/README.md` | Diretório criado + protocolo de nomenclatura e campos obrigatórios |
| CrewAI interop | `repos/auraxis-api/ai_squad/CLAUDE.md` | Protocolo de lock, handoff e bootstrap de contexto para o squad automatizado |
| Next Task estruturada | `.context/01_status_atual.md` | Seção "Próxima task para agentes autônomos" com fila estruturada |

## O que foi validado

- `scripts/verify-agent-session.sh` rodado: ✅ 0 failures, 1 warning esperado (SSH agent)
- `scripts/check-health.sh`: todos os repos passando
- Estrutura `.context/` completa em auraxis-web e auraxis-app
- ai_squad/CLAUDE.md criado e integrado com protocolo de lock

## Pendências manuais (ação do usuário)

| Pendência | Status | Detalhe |
|:----------|:-------|:--------|
| AWS IAM trust policy | ⚠️ Pendente | Subject hint: `repo:italofelipe/auraxis-api:environment:*` |
| SonarCloud project key | ⚠️ Pendente | Renomear de `italofelipe_flask-expenses-manager` para `italofelipe_auraxis-api` |
| Push auraxis-app ao GitHub | ✅ Feito pelo usuário | Confirmado na sessão anterior |
| Push auraxis-web ao GitHub | ✅ Feito pelo usuário | Confirmado na sessão anterior |

## Próximo passo recomendado

**Task X4 — Ruff advisory em `auraxis-api`**

```bash
# Início de sessão:
cd /path/to/auraxis-platform
./scripts/verify-agent-session.sh
./scripts/agent-lock.sh acquire claude auraxis-api "X4 — Ruff advisory setup"
cd repos/auraxis-api
git checkout master && git pull
git checkout -b refactor/x4-ruff-advisory
```

O que fazer:
1. Adicionar `ruff` em `requirements-dev.txt`
2. Adicionar `[tool.ruff]` em `pyproject.toml` com regras advisory (sem substituir black/isort/flake8 ainda)
3. Rodar `ruff check .` e registrar resultado (número de issues por categoria)
4. Atualizar TASKS.md com resultado e commit
5. Documentar decisão: substituição faseada ou direta

## Commits desta rodada (platform — branch docs/agent-autonomy-baseline)

A commitar:
- `docs(autonomy): add quality gates and local context to auraxis-web and auraxis-app`
- `docs(autonomy): rewrite agent-session workflow with unambiguous lock protocol`
- `feat(scripts): add verify-agent-session.sh prereq checker`
- `docs(autonomy): create handoffs/ directory with protocol`
- `docs(autonomy): add CLAUDE.md to ai_squad with CrewAI interop protocol`
- `docs(context): sync PLT1.4 status and handoff`
