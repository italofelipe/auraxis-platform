# .context/handoffs/ — Histórico de Handoffs

Diretório de handoffs históricos entre sessões e agentes.

## Convenção de nomenclatura

```
YYYY-MM-DD_<agente>_<repo-ou-scope>_<tarefa-ou-milestone>.md
```

Exemplos:
```
2026-02-23_claude_platform_plt14-agent-autonomy.md
2026-02-22_claude_auraxis-api_pre-migracao-platform.md
2026-02-15_crewai_auraxis-api_b4-b5-b6-password-reset.md
```

## Diferença entre este diretório e 05_handoff.md

| Arquivo | Propósito | Quando atualizar |
|:--------|:----------|:-----------------|
| `05_handoff.md` | Handoff **ativo** — estado atual da sessão em andamento ou mais recente | A cada fim de sessão (sobrescreve) |
| `handoffs/*.md` | **Arquivo histórico** — registro permanente de cada sessão concluída | A cada fim de sessão (cria novo arquivo) |

## Protocolo

Ao final de cada sessão:

1. Atualizar `05_handoff.md` com o estado atual.
2. Copiar o conteúdo para um novo arquivo aqui com a nomenclatura correta.
3. Commitar ambos juntos:

```bash
git add .context/05_handoff.md .context/handoffs/YYYY-MM-DD_agente_scope_tarefa.md
git commit -m "docs(handoff): register session handoff — <descrição breve>"
```

## Campos obrigatórios em cada handoff

Todo arquivo de handoff deve conter:

```markdown
## O que foi feito
## O que foi validado (gates, testes)
## Riscos pendentes
## Próximo passo sugerido (Task ID + repo + branch)
## Commits desta sessão
```

Usar template em `auraxis-platform/.context/templates/HANDOFF_TEMPLATE.md`.
