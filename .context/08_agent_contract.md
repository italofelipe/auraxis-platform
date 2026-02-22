# Agent Contract

## Objetivo
Padronizar como agentes (CrewAI, Codex, etc.) atuam no ecossistema Auraxis.

## Input mínimo antes de executar
- Ler índice (`06_context_index.md`).
- Ler status atual (`01_status_atual.md`).
- Ler backlog atual (`02_backlog_next.md`).
- Ler `tasks.md` do repositório alvo.

## Comportamento esperado
- Trabalhar por blocos e objetivos claros.
- Explicitar suposições e riscos antes de mudanças estruturais.
- Registrar decisões de arquitetura/processo em `.context`.
- Atualizar backlog/status ao final de cada bloco.

## Estrutura de saída por bloco
1. O que foi feito.
2. O que foi validado (testes/checks).
3. Riscos pendentes.
4. Próximo passo sugerido.
5. Commits/PRs.

## Regras de segurança operacional
- Nunca expor secrets em código/log/documentação.
- Tratar arquivos temporários/sufixos acidentais (ex.: `* 2`) como artefatos descartáveis.
- Não executar ações destrutivas sem instrução explícita.

## Governança de contexto
- Mudança em regra global -> atualizar `07_steering_global.md`.
- Mudança de arquitetura -> atualizar `09_architecture_principles.md` + ADR.
- Mudança de prioridade -> atualizar `02_backlog_next.md` e `tasks.md` do repo.
