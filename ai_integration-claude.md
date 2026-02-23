# Guia de Integração — Claude (Anthropic) @ Auraxis Platform

**Escopo:** Nível de plataforma (orquestração e governança). Para trabalho no backend,
leia também `repos/auraxis-api/ai_integration-claude.md`.

---

## Papel do Claude neste ecossistema

| Nível        | Papel primário                                      |
|:-------------|:----------------------------------------------------|
| Platform     | Governança, contexto, templates, orquestração       |
| auraxis-api  | Implementação backend, review, análise, documentação |
| auraxis-web  | (futuro) Implementação frontend Nuxt.js              |
| auraxis-app    | Implementação React Native + Expo                 |

---

## Bootstrap obrigatório (plataforma)

Antes de qualquer ação, ler em ordem:

1. `CLAUDE.md` — directive operacional
2. `.context/06_context_index.md` — índice de contexto
3. `.context/07_steering_global.md` — governança global
4. `.context/08_agent_contract.md` — contrato de agentes
5. `.context/01_status_atual.md` — status atual
6. `.context/02_backlog_next.md` — próximas prioridades

---

## Protocolo de sessão

### Início
```bash
# Verificar saúde da platform
./scripts/check-health.sh

# Adquirir lock (se for trabalho autônomo estruturado)
./scripts/agent-lock.sh acquire claude <repo> "<tarefa>"
```

### Trabalho
- Commits pequenos e granulares por responsabilidade
- Atualizar `.context/` após decisões relevantes
- Nunca commitar direto em `master`

### Encerramento
```bash
# Atualizar handoff
# Editar .context/05_handoff.md com o que foi feito, validado, riscos e próximo passo

# Liberar lock
./scripts/agent-lock.sh release claude
```

---

## Fronteiras operacionais

### Claude faz autonomamente
- Ler qualquer arquivo no repositório
- Atualizar `.context/`, `docs/`, templates
- Criar e executar scripts em `scripts/`
- Commits com mensagens convencionais
- Criar feature branches

### Claude pede aprovação antes
- Adicionar/remover submodules
- Alterar arquivos de governança global (`07_steering_global.md`, `08_agent_contract.md`)
- Qualquer ação com impacto em múltiplos repos
- Deleção de arquivos

### Claude nunca faz
- Commitar diretamente em `master`
- Escrever secrets ou tokens em arquivos
- `git add .` (sempre staging seletivo)
- Força push em qualquer branch

---

## Colaboração com outros agentes

Antes de iniciar trabalho substantivo, verificar:
```bash
./scripts/agent-lock.sh status
```

Se outro agente estiver ativo no mesmo repo, aguardar ou coordenar via
`.context/05_handoff.md`.

**Handoff interop:** Claude lê e escreve handoffs em `.context/05_handoff.md`
e `.context/handoffs/` (auraxis-api). Gemini e GPT também consomem esses arquivos.
Use linguagem clara e estruturada — os handoffs precisam ser parseáveis por outros agentes.

---

## Qualidades esperadas do output de Claude nesta platform

- Commits com mensagens Conventional Commits precisas
- Documentação clara, sem ambiguidade de escopo
- Atualização de `.context/` após cada decisão relevante
- Código de scripts robusto (set -euo pipefail, erros explícitos)
- Sem hardcode de paths absolutos nos scripts (usar `$PLATFORM_ROOT`)
