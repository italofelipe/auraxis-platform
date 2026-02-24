# Workflow Conventions

## Objetivo
Padronizar fluxo de trabalho entre equipes humanas e agentes, mantendo previsibilidade e rastreabilidade.

## Convenções de branch
Formato recomendado:
- `feat/<escopo-curto>`
- `fix/<escopo-curto>`
- `refactor/<escopo-curto>`
- `chore/<escopo-curto>`
- `docs/<escopo-curto>`
- `test/<escopo-curto>`

Restrições obrigatórias:
- Não usar prefixo `codex/` em branches.
- Não usar branches genéricas sem tipo (ex.: `italo-test`).
- Antes de qualquer `git push`, atualizar a branch de trabalho com a branch alvo (`main`/`master`) e resolver conflitos localmente.

Exemplos:
- `feat/profile-investor-quiz`
- `fix/auth-password-reset-token-expiry`
- `docs/platform-context-bootstrap`

## Convenções de commit
Padrão: Conventional Commits
- `feat:` nova funcionalidade
- `fix:` correção de defeito
- `refactor:` melhoria interna sem alterar comportamento esperado
- `docs:` documentação
- `test:` testes
- `chore:` manutenção/infra/tooling
- `perf:` melhoria de performance
- `security:` correções de segurança

## Sequência operacional por tarefa/bloco
1. Atualizar base local da branch principal.
2. Criar branch de trabalho.
3. Implementar incrementalmente.
4. Executar testes/checks aplicáveis.
5. Fazer `pull` da branch alvo na branch de trabalho (ex.: `git pull --no-rebase origin main`).
6. Resolver conflitos localmente e revalidar checks.
7. Atualizar documentação de status.
8. Commits granulares e reversíveis.
9. Abrir PR com contexto claro.

## Política de PR
Todo PR deve incluir:
- objetivo e escopo
- impacto em contrato
- evidência de validação
- riscos residuais
- plano de rollback

## Política de merge
- Evitar squash de blocos heterogêneos.
- Preservar granularidade útil para rollback.
- Não mergear com checks críticos falhando.
