# Workflow: Multi-Front Agent Orchestration

**Objetivo:** coordenar execucao paralela em `auraxis-api`, `auraxis-web` e `auraxis-app` com CrewAI + Claude + Gemini + GPT sem colisao de contexto ou de codigo.

## 1. Modelo de lanes

- **Lane API:** backend contracts, regras de negocio, migrations.
- **Lane Web:** consumo de contrato, SSR/UI, testes web.
- **Lane App:** consumo de contrato, UX mobile, testes RN.

Cada lane deve ter branch propria e lock ativo no repo alvo.

## 2. Matriz de papeis

| Agente | Papel primario | Saida obrigatoria |
|:-------|:---------------|:------------------|
| CrewAI | Orquestracao e execucao de backlog estruturado | plano de execucao + handoff por bloco |
| GPT/Codex | Implementacao e hardening tecnico | commits granulares + delivery report |
| Claude | Revisao arquitetural e contratos | review de riscos + decisao tecnica |
| Gemini | Revisao independente (adversarial) | validacao de risco/regressao |

## 3. Contrato de handoff por bloco

Arquivo: `.context/handoffs/YYYY-MM-DD_<agent>_<repo>_<task>.md`

Campos minimos:
- o que foi feito
- o que foi validado
- riscos pendentes
- proximo passo claro
- links de branch/commit/PR

## 4. Regras de concorrencia

1. Nao trabalhar em dois agentes na mesma branch.
2. Nao abrir duas tasks com impacto no mesmo contrato sem ordem explicita.
3. Toda mudanca de contrato no API deve gerar sinalizacao para lanes web/app no mesmo dia.
4. Se houver conflito de prioridade, prevalece estabilidade de pipeline e seguranca.

## 5. Gate de inicio de sprint autonoma

- `./scripts/check-health.sh` sem falhas criticas.
- Branch protections aplicadas a partir de `governance/github/branch-protection-config.json`.
- Sonar em modo CI scanner e Automatic Analysis desligado.
- Dependency review sem fallback permissivo.
- Templates SDD existentes em cada repo de produto.

## 6. Critério de saída do bloco paralelo

- cada lane com delivery report publicado;
- contexto global atualizado (`01_status_atual.md`, `02_backlog_next.md`, `05_handoff.md`);
- locks liberados em todos os agentes;
- status check `CI Passed` verde nas 3 frentes.
