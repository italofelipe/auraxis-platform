# Autonomous Delivery Readiness (API + App + Web)

Data: 2026-02-24

Objetivo: garantir base estável de governança, segurança e instrumentação antes de iniciar blocos de feature com agentes autônomos.

---

## 1) Governança de merge

Status:
- ✅ Branch protection ativo em `main` para `auraxis-api`, `auraxis-app`, `auraxis-web`
- ✅ Required checks padronizados com `CI Passed` + dependency check por repo
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
- [ ] Confirmar Dependency Graph habilitado nos 3 repositórios (app/web agora sem fallback permissivo no workflow).

---

## 4) Hygiene operacional

Status:
- ✅ Removido artefato local indevido no web (`.nuxtrc 2`)
- ✅ `.gitignore` do web ajustado para evitar recorrência (`.nuxtrc*`)
- ✅ Política de branch `codex/*` proibida documentada na plataforma
- ✅ `WEB9` concluído: Dockerfile + docker-compose + runbook + gate de Docker build no CI
- ✅ `APP2` e `WEB2` concluídos: clientes HTTP com healthcheck e testes
- ✅ Templates SDD locais adicionados em `auraxis-app` e `auraxis-web`

Pendência recomendada:
- [ ] Eliminar branches remotos legados `codex/*` ainda existentes após migração de PRs ativos.

---

## 5) Próximo bloco (pré-feature)

1. Confirmar pipelines verdes em `main` nos 3 repos após hardening final.
2. Aplicar branch protection as-code atualizado (`solo maintainer`) com `scripts/apply-branch-protection.sh`.
3. Iniciar backlog de negócio: `B10` e `B11` (API), seguido de fluxos consumidores em web/app.
4. Ativar progressivamente E2E/Lighthouse no web via flags de repo após estabilização do SSR.
