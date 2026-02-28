# Autonomous Delivery Readiness (API + App + Web)

Data: 2026-02-27

Objetivo: garantir base estável de governança, segurança e instrumentação antes de iniciar blocos de feature com agentes autônomos.

---

## 1) Governança de merge

Status:
- ✅ Branch protection ativo em `main` para `auraxis-api`, `auraxis-app`, `auraxis-web`
- ✅ Required checks padronizados por gates reais de cada repo (sem gate sintético `CI Passed`)
- ✅ Modo solo maintainer aplicado (sem aprovador obrigatório de review)
- ✅ Force-push/delete bloqueados
- ✅ PR obrigatório com conversation resolution

Referência:
- `governance/github/branch-protection-config.json`
- `scripts/apply-branch-protection.sh`

---

## 2) SonarCloud (modo obrigatório)

Decisão:
- Operar **somente** em modo CI scanner nos 3 repos.

Estado atual:
- ✅ `auraxis-api`: scanner CI ativo no workflow
- ✅ `auraxis-app`: scanner CI ativo no workflow
- ✅ `auraxis-web`: scanner CI ativo no workflow

Status operacional:
- ✅ Automatic Analysis desabilitado e modo CI scanner adotado como padrão único

---

## 3) Security gates mínimos para autonomia

Status:
- ✅ Secret scan (Gitleaks/TruffleHog) em app/web
- ✅ Secret scan + SAST + container scan no api
- ✅ Dependency review em app/web/api
- ✅ Sonar scanner pinado por SHA nos workflows

Pendência recomendada:
- [ ] Confirmar Dependency Graph habilitado nos 3 repositórios (app/web agora em modo estrito; sem suporte o job falha por design).

---

## 4) Hygiene operacional

Status:
- ✅ Removido artefato local indevido no web (`.nuxtrc 2`)
- ✅ `.gitignore` do web ajustado para evitar recorrência (`.nuxtrc*`)
- ✅ Política de branch `codex/*` proibida documentada na plataforma
- ✅ `WEB9` concluído: Dockerfile + docker-compose + runbook + gate de Docker build no CI
- ✅ `APP2` e `WEB2` concluídos: clientes HTTP com healthcheck e testes
- ✅ Templates SDD locais adicionados em `auraxis-app` e `auraxis-web`
- ✅ Guardrail anti-drift de execução: bloqueio de `task_id` divergente no fim do run
- ✅ Auto-prepare de repositório antes de run (fetch, saída de detached HEAD, sync de branch base)
- ✅ Commit guardrail pós-gates no orquestrador:
  - frontend só comita após `run_repo_quality_gates()` com status `pass`;
  - backend só comita após `run_backend_tests()` e `run_integration_tests(full_crud)` com status `pass`.
- ✅ `ai-next-task` com preflight de credencial LLM (`OPENAI_API_KEY` ou `OLLAMA_BASE_URL`).
- ✅ `ai-next-task` com fallback automático de credencial em `.env` da plataforma (além de `ai_squad/.env`).
- ✅ Taskboard hygiene aplicada: somente 1 `In Progress` por repo (`B11`/API, `WEB3`/Web, `APP3`/App).

Pendência recomendada:
- [ ] Eliminar branches remotos legados `codex/*` ainda existentes após migração de PRs ativos.
- [ ] Medir estabilidade do bloqueio de commit pós-gates por pelo menos 3 ciclos completos de `make next-task`.

---

## 5) Próximo bloco (pré-feature)

1. Concluir PLT1/PLT3/PLT4 runtime para remover os últimos bloqueios de autonomia ampla.
2. Manter Node local = CI (`25.x`) em app/web para reduzir drift local-vs-pipeline.
3. Rodar bateria de estabilidade (`make next-task`) por múltiplos ciclos e medir taxa de bloqueio.
4. Com estabilidade comprovada, iniciar backlog de negócio: `B10` e `B11` (API), seguido de fluxos consumidores em web/app.
