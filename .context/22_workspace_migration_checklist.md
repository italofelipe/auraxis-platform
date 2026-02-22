# Workspace Migration Checklist (backend -> platform)

Data base: 2026-02-22

## Objetivo
Migrar o backend atual para `auraxis-platform/repos/auraxis-api` sem perder contexto, rastreabilidade ou operacionalidade local/CI.

## Pré-migração (obrigatório)
- [ ] Garantir `git status` limpo no backend.
- [ ] Garantir `git status` limpo no `auraxis-platform`.
- [ ] Confirmar handoff atualizado no backend (`.context/handoffs/`).
- [ ] Confirmar `TASKS.md` do backend sincronizado.
- [ ] Confirmar `.context/01_status_atual.md` e `.context/05_handoff.md` no `auraxis-platform`.

## Migração física da pasta
Exemplo:

```bash
cd /Users/italochagas/Desktop/projetos/auraxis-platform/repos
mv /Users/italochagas/Desktop/projetos/flask-expenses-manager ./auraxis-api
```

## Pós-migração imediata (obrigatório)
- [ ] Validar branch atual e remotes em `repos/auraxis-api`.
- [ ] Executar leitura de bootstrap do contexto (`.context/README.md`, `TASKS.md`, `steering.md`).
- [ ] Validar scripts com path absoluto conhecido (deploy, CI-like, quality gates).
- [ ] Validar que hooks/pre-commit continuam operando no novo caminho.
- [ ] Validar que automações/agentes apontam para o novo diretório de trabalho.

## Sanidade mínima recomendada (após mover)
- [ ] `python --version` no ambiente local esperado.
- [ ] `pre-commit run --all-files`.
- [ ] `pytest -q` (ou suíte curta equivalente acordada).
- [ ] Script CI-like local do backend (se aplicável).

## Riscos principais
- Quebra de scripts hardcoded com path antigo.
- Drift entre contexto local e contexto plataforma.
- Perda de referência operacional entre branches abertas.

## Mitigações
- Preferir caminhos relativos no repositório sempre que possível.
- Atualizar imediatamente os documentos de handoff/status após a movimentação.
- Executar checklist antes de iniciar novo bloco de feature/refactor.
