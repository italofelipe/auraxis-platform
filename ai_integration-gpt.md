# Guia de Integração — GPT (OpenAI) @ Auraxis Platform

**Nomes alternativos em uso:** Gepeto, Codex, GPT-4, ChatGPT
**Escopo:** Nível de plataforma (orquestração e governança).

---

## Papel do GPT neste ecossistema

| Nível    | Papel primário                                                 |
|:---------|:---------------------------------------------------------------|
| Platform | Implementação de scripts, automações, geração de código        |
| Repos    | Feature implementation, debugging, code generation             |

O GPT é o agente de implementação de alta velocidade. Use-o quando o
objetivo é gerar código funcional rapidamente, com Claude ou Gemini
fazendo revisão posterior.

---

## Bootstrap obrigatório

Antes de qualquer trabalho de implementação, ler:

1. `.context/06_context_index.md` — índice de contexto
2. `.context/07_steering_global.md` — governança global
3. `.context/08_agent_contract.md` — contrato de agentes
4. `.context/01_status_atual.md` — status atual
5. `.context/02_backlog_next.md` — próximas prioridades
6. `tasks.md` do repo alvo — backlog e status local

---

## Protocolo de sessão

### Início
```
1. Ler os arquivos de bootstrap acima
2. Verificar .context/agent_lock.json — há outro agente ativo?
3. Identificar a task alvo em tasks.md
4. Criar branch seguindo conventional branching
```

### Trabalho
- Implementar em branches de feature/fix
- Commits granulares com Conventional Commits
- Executar quality gates antes de qualquer commit
- Registrar suposições e riscos em comentários ou no handoff

### Encerramento
```
1. Garantir que todos os quality gates passam
2. Atualizar tasks.md com status e commit hashes
3. Registrar handoff em .context/05_handoff.md
```

---

## Fronteiras operacionais

### GPT faz autonomamente
- Implementar features e correções em branches de trabalho
- Criar testes automatizados
- Gerar documentação técnica
- Executar scripts de qualidade

### GPT pede aprovação antes
- Mudanças de arquitetura com impacto cross-repo
- Alterações em contratos públicos (OpenAPI, GraphQL schema)
- Deploy em qualquer ambiente
- Deleção de código ou testes existentes

### GPT nunca faz
- Commitar diretamente em `master`
- Escrever secrets em qualquer arquivo
- `git add .` (staging seletivo obrigatório)
- Alterar arquivos de governança sem alinhamento explícito

---

## Quality gates obrigatórios (auraxis-api)

```bash
black .
isort app tests config run.py run_without_db.py
flake8 app tests config run.py run_without_db.py
mypy app
pytest -m "not schemathesis" --cov=app --cov-fail-under=85
```

Para outros repos, verificar o `steering.md` local.

---

## Colaboração com Claude e Gemini

| Situação                              | Fluxo recomendado                        |
|:--------------------------------------|:-----------------------------------------|
| Feature nova                          | GPT implementa → Claude revisa           |
| Decisão arquitetural                  | Gemini analisa → Claude decide → GPT implementa |
| Bug crítico                           | GPT debugga → Claude valida              |
| Review de segurança                   | Claude ou Gemini revisam output do GPT   |

Handoffs em `.context/handoffs/` garantem continuidade entre agentes.

---

## Contexto do CrewAI

O GPT pode ser configurado como LLM base do `ai_squad/` (CrewAI) no backend.
Ver `repos/auraxis-api/ai_squad/README.md` para configuração de `OPENAI_API_KEY`.
