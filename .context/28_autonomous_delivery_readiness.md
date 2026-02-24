# Autonomous Delivery Readiness (API + App + Web)

Data: 2026-02-24

Objetivo: garantir base estável de governança, segurança e instrumentação antes de iniciar blocos de feature com agentes autônomos.

---

## 1) Governança de merge

Status:
- ✅ Branch protection ativo em `main` para `auraxis-api`, `auraxis-app`, `auraxis-web`
- ✅ Required checks padronizados com `CI Passed` + dependency check por repo
- ✅ Force-push/delete bloqueados
- ✅ PR obrigatório com aprovação e conversation resolution

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

Pendência manual (painel SonarCloud):
- [ ] Desabilitar Automatic Analysis em:
  - `italofelipe_auraxis-api`
  - `italofelipe_auraxis-app`
  - `italofelipe_auraxis-web`

---

## 3) Security gates mínimos para autonomia

Status:
- ✅ Secret scan (Gitleaks/TruffleHog) em app/web
- ✅ Secret scan + SAST + container scan no api
- ✅ Dependency review em app/web/api
- ✅ Sonar scanner pinado por SHA nos workflows

Pendência recomendada:
- [ ] Garantir Dependency Graph habilitado nos 3 repositórios para enforcement total do Dependency Review (app/web em modo compatibilidade temporário).

---

## 4) Hygiene operacional

Status:
- ✅ Removido artefato local indevido no web (`.nuxtrc 2`)
- ✅ `.gitignore` do web ajustado para evitar recorrência (`.nuxtrc*`)
- ✅ Política de branch `codex/*` proibida documentada na plataforma

Pendência recomendada:
- [ ] Eliminar branches remotos legados `codex/*` ainda existentes após migração de PRs ativos.

---

## 5) Próximo bloco (pré-feature)

1. Fechar pendências manuais do SonarCloud (Automatic Analysis OFF nos 3 projetos).
2. Confirmar pipelines verdes em `main` nos 3 repos após hardening.
3. Executar `WEB9` (dockerização do Nuxt) para completar baseline de execução padronizada.
4. Executar `APP9` e `WEB10` para remover `--passWithNoTests` e tornar os gates de teste estritamente bloqueantes.
5. Iniciar `APP2` e `WEB2` (clientes HTTP) com contratos versionados e testes.
