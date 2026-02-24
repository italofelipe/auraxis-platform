# Workflow: Agent Session

**Gatilho:** Início de qualquer sessão de agente (Claude, Gemini, GPT, CrewAI).
**Escopo:** Platform-level e por repo.

---

## Pré-condições

- `auraxis-platform` clonado e atualizado
- Acesso de leitura/escrita ao repo alvo
- API keys configuradas (se agente usa LLM externo)

---

## Passo 1 — Verificar prereqs da sessão

```bash
cd /path/to/auraxis-platform
./scripts/verify-agent-session.sh
```

Se houver `❌ Failures`, resolver antes de continuar.

Se o script ainda não existir (bootstrap inicial), verificar manualmente:
- `git` instalado e configurado com nome/email
- SSH agent rodando (`ssh-add -l` retorna chave)
- Python 3 disponível (`python3 --version`)
- Submodules inicializados (`git submodule status` sem `-SHA`)

---

## Passo 2 — Health check

```bash
./scripts/check-health.sh
```

Se houver `❌ Failures`, resolver antes de continuar.
Warnings (`⚠️`) podem ser aceitos com consciência documentada.

---

## Passo 3 — Verificar agent lock

```bash
./scripts/agent-lock.sh status
```

- Se **livre**: prosseguir para o passo 4.
- Se **ocupado**: aguardar liberação ou coordenar via `.context/05_handoff.md`.

### Política de lock — quando é OBRIGATÓRIO

| Cenário | Lock obrigatório? |
|:--------|:------------------|
| Sessão autônoma (agente executa task completa sem supervisão humana) | **SIM — sempre** |
| Sessão de implementação com commits (qualquer agente escrevendo código) | **SIM — sempre** |
| Sessão multi-step com duração > 15 minutos | **SIM — sempre** |
| Sessão de leitura/pesquisa apenas (sem commits) | Não obrigatório |
| Sessão interativa curta com humano supervisionando em tempo real | Não obrigatório |

> **Regra prática:** Se você vai commitar, adquira o lock. Sem exceção.

---

## Passo 4 — Adquirir lock

```bash
./scripts/agent-lock.sh acquire <agente> <repo> "<descrição da tarefa>"
```

Exemplos:
```bash
./scripts/agent-lock.sh acquire claude auraxis-api "Implement B10 investor profile quiz"
./scripts/agent-lock.sh acquire gpt auraxis-web "Implement WEB1 Nuxt project init"
./scripts/agent-lock.sh acquire gemini auraxis-platform "Architecture review X3 strategy"
```

Agentes válidos: `claude`, `gemini`, `gpt`, `crewai`

> O lock expira automaticamente após 4 horas (TTL padrão no script). Se a sessão ultrapassar esse tempo, renovar com `acquire` novamente antes de expirar.

---

## Passo 5 — Bootstrap de contexto

Ler em ordem (versão mínima):

1. `.context/06_context_index.md` — índice e ordem de leitura
2. `.context/07_steering_global.md` — governança imutável
3. `.context/08_agent_contract.md` — contrato de comportamento do agente
4. `.context/01_status_atual.md` — onde estamos e **qual a próxima task**
5. `.context/02_backlog_next.md` — prioridades globais
6. `repos/<repo-alvo>/tasks.md` — status local do repo
7. `repos/<repo-alvo>/.context/README.md` — contexto local do repo (se existir)

Para sessões longas ou início de ciclo, ler a sequência completa em `CLAUDE.md` (raiz da platform).

---

## Passo 6 — Criar branch de trabalho

```bash
cd repos/<repo-alvo>
git checkout master && git pull   # ou main, conforme o repo
git checkout -b <tipo>/<escopo-curto>
```

Tipos válidos: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `security`

Exemplos:
```
feat/b10-investor-quiz
fix/auth-token-refresh
docs/context-update-plt14
```

---

## Passo 7 — Implementar

- Commits pequenos, **um por responsabilidade**
- Formato: `tipo(escopo): descrição imperativa curta`
- Nunca `git add .` — sempre staging seletivo
- Rodar quality gates do repo antes de cada commit:

### Gates por repo (antes de commitar)

**auraxis-api (Python/Flask):**
```bash
black . && isort app tests config && flake8 app tests && mypy app && pytest -m "not schemathesis" --cov=app --cov-fail-under=85
```

**auraxis-web (Nuxt/@nuxt/eslint):**
```bash
pnpm lint && pnpm typecheck && pnpm test:coverage
```

**auraxis-app (React Native/ESLint):**
```bash
npm run lint && npm run typecheck && npm run test:coverage
```

> Referência completa: `repos/<repo-alvo>/.context/quality_gates.md`

```bash
git add <arquivos específicos>
git commit -m "tipo(escopo): descrição"
```

---

## Passo 8 — Encerramento de sessão

### 8.1 Atualizar tasks.md do repo
Marcar tasks concluídas, atualizar progresso, registrar commit hashes.

### 8.2 Registrar handoff
Editar `.context/05_handoff.md` com:
- O que foi feito
- O que foi validado (quais gates passaram)
- Riscos pendentes
- Próximo passo sugerido (task ID + repo)
- Branch(es) abertas e commits

### 8.2.1 Sincronizar branch antes do push (obrigatório)

Antes de qualquer push, atualizar a branch atual com a branch alvo do PR:

```bash
# Exemplo para repos com main
git pull --no-rebase origin main

# Exemplo para repos com master
git pull --no-rebase origin master
```

Se houver conflito:
- Resolver localmente.
- Reexecutar quality gates.
- Só então executar `git push`.

### 8.3 Liberar lock

```bash
cd /path/to/auraxis-platform
./scripts/agent-lock.sh release <agente>
```

> **Nunca encerrar sessão sem liberar o lock.** O TTL evita lock eterno, mas liberar explicitamente mantém coordenação previsível.

### 8.4 Atualizar status global (se houve decisão relevante)

```bash
# Editar .context/01_status_atual.md com o novo estado
git add .context/01_status_atual.md
git commit -m "docs(context): update platform status after <descrição>"
```

---

## Critério de saída

- [ ] Prereqs verificados (verify-agent-session.sh passou)
- [ ] Health check passou (ou warnings documentados)
- [ ] Quality gates do repo passaram antes de cada commit
- [ ] Lock liberado
- [ ] Handoff atualizado em `.context/05_handoff.md`
- [ ] tasks.md do repo alvo sincronizado
- [ ] Branch aberta com commits granulares
