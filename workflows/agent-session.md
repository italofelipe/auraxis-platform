# Workflow: Agent Session

**Gatilho:** Início de qualquer sessão de agente (Claude, Gemini, GPT, CrewAI).
**Escopo:** Platform-level e por repo.

---

## Pré-condições

- `auraxis-platform` clonado e atualizado
- Acesso de leitura/escrita ao repo alvo
- API keys configuradas (se agente usa LLM externo)

---

## Passo 1 — Health check

```bash
cd /path/to/auraxis-platform
./scripts/check-health.sh
```

Se houver `❌ Failures`, resolver antes de continuar.
Warnings (`⚠️`) podem ser aceitos com consciência.

---

## Passo 2 — Verificar agent lock

```bash
./scripts/agent-lock.sh status
```

- Se **livre**: prosseguir para o passo 3.
- Se **ocupado**: aguardar liberação ou coordenar via `.context/05_handoff.md`.

---

## Passo 3 — Bootstrap de contexto

Ler em ordem (versão resumida para sessões curtas):

1. `.context/01_status_atual.md` — onde estamos
2. `.context/02_backlog_next.md` — o que fazer
3. `repos/<repo-alvo>/tasks.md` — status local do repo

Para sessões longas ou início de ciclo, ler a sequência completa em `CLAUDE.md`.

---

## Passo 4 — Adquirir lock (sessões autônomas)

> Somente para execução autônoma estruturada. Sessões interativas curtas podem pular.

```bash
./scripts/agent-lock.sh acquire <agente> <repo> "<descrição da tarefa>"
```

Exemplo:
```bash
./scripts/agent-lock.sh acquire claude auraxis-api "Implement B10 investor profile quiz"
```

---

## Passo 5 — Criar branch de trabalho

```bash
cd repos/<repo-alvo>
git checkout master && git pull
git checkout -b <tipo>/<escopo-curto>
```

Tipos válidos: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `security`

---

## Passo 6 — Implementar e commitar

- Commits pequenos, um por responsabilidade
- Formato: `tipo(escopo): descrição imperativa curta`
- Nunca `git add .` — sempre staging seletivo

```bash
git add <arquivos específicos>
git commit -m "tipo(escopo): descrição"
```

---

## Passo 7 — Encerramento de sessão

### 7.1 Atualizar tasks.md do repo
Marcar tasks concluídas, atualizar progresso, registrar commit hashes.

### 7.2 Registrar handoff
Editar `.context/05_handoff.md` com:
- O que foi feito
- O que foi validado
- Riscos pendentes
- Próximo passo sugerido
- Branch(es) abertas

### 7.3 Liberar lock

```bash
cd /path/to/auraxis-platform
./scripts/agent-lock.sh release <agente>
```

### 7.4 Atualizar status global (se houve decisão relevante)

```bash
# Editar .context/01_status_atual.md com o novo estado
git add .context/01_status_atual.md
git commit -m "docs(context): update platform status after <descrição>"
```

---

## Critério de saída

- [ ] Health check passou (ou warnings documentados)
- [ ] Lock liberado
- [ ] Handoff atualizado
- [ ] tasks.md do repo alvo sincronizado
- [ ] Branch aberta com commits granulares
