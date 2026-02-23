# CLAUDE.md — [Nome do Repo]

## Identidade

[Uma frase descrevendo o propósito do repo e sua stack principal.]

Este repo é um **submodule** de `auraxis-platform`.
Trabalhe a partir da raiz da platform quando precisar de contexto global.

---

## Session Bootstrap (MANDATORY — execute em ordem)

Antes de qualquer ação:

1. `auraxis-platform/.context/06_context_index.md` — índice de todos os artefatos
2. `auraxis-platform/.context/07_steering_global.md` — princípios imutáveis
3. `auraxis-platform/.context/08_agent_contract.md` — contrato de comportamento
4. `auraxis-platform/.context/23_definition_of_done.md` — DoD canônico
5. `auraxis-platform/.context/01_status_atual.md` — onde o projeto está
6. `auraxis-platform/.context/02_backlog_next.md` — o que fazer a seguir
7. Este arquivo — regras específicas deste repo
8. `tasks.md` deste repo — backlog detalhado

---

## Limites operacionais

### Pode fazer autonomamente
- Ler qualquer arquivo do repo.
- Criar/editar código, testes, documentação local.
- Criar branches de feature seguindo `type/scope-descricao`.
- Commitar com Conventional Commits granulares.
- Atualizar `tasks.md` e `steering.md` locais.

### Deve perguntar antes de prosseguir
- Adicionar dependências que afetam o build ou o runtime.
- Mudanças em configuração de CI/CD.
- Alterações em contratos de API (REST/GraphQL) — consultar `16_contract_compatibility_policy.md`.
- Decisões arquiteturais com impacto em outros repos.
- Qualquer ação irreversível (drop de tabela, remoção de endpoint, etc.).

### Nunca fazer
- Commitar diretamente em `master`/`main`.
- Expor secrets, tokens ou chaves em código, logs ou documentação.
- Modificar `.context/` da platform diretamente — propor mudança via handoff.
- Executar ações destrutivas sem instrução explícita do humano.

---

## Stack e ferramentas

| Componente | Tecnologia |
|:-----------|:-----------|
| Linguagem | [ex: Python 3.13 / TypeScript 5.x] |
| Framework | [ex: Flask / Nuxt 3 / Expo SDK 54] |
| Lint/Format | [ex: Ruff + mypy / Biome / ESLint] |
| Testes | [ex: pytest / Vitest] |
| CI | [ex: GitHub Actions] |

---

## Operação local

```bash
# Instalar dependências
[comando]

# Dev server / testes
[comando]

# Lint
[comando]
```

---

## Convenções

- **Commits**: Conventional Commits — `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.
- **Branch**: `type/scope-descricao` (ex: `feat/auth-login`, `fix/token-expiry`).
- **PR**: incluir objetivo, impacto, evidência de validação e risco residual.

---

## Integração com a platform

- Contexto global: `auraxis-platform/.context/`
- Handoffs e decisões transversais: `auraxis-platform/.context/05_handoff.md`
- Contratos de API: definidos em `auraxis-api` (fonte de verdade)
- Lock de agente: `auraxis-platform/scripts/agent-lock.sh`
