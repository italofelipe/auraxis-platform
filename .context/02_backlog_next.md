# Próximas Prioridades

## ⚠️ SETUP MANUAL — fazer ANTES das próximas tarefas de produto

> Estes itens requerem ação humana. Sem eles, os agents terão CI quebrado ou ambiguidade de contexto.

### SETUP-1 — SonarCloud (CRÍTICO para CI não ficar vermelho)
- [ ] Acessar sonarcloud.io → criar organização vinculada ao GitHub (`italofelipe`)
- [ ] Importar `auraxis-web` → copiar `SONAR_TOKEN` → adicionar em Settings > Secrets do repo
- [ ] Importar `auraxis-app` → copiar `SONAR_TOKEN` → adicionar em Settings > Secrets do repo
- [ ] Verificar que `auraxis-api` já tem `SONAR_TOKEN` configurado (era do setup antigo)
- Referência: `.context/25_quality_security_playbook.md` seção 9

### SETUP-2 — GitHub: habilitar auto-merge (CRÍTICO para Dependabot funcionar)
- [ ] `auraxis-web` → Settings → General → Pull Requests → habilitar "Allow auto-merge"
- [ ] `auraxis-app` → Settings → General → Pull Requests → habilitar "Allow auto-merge"
- [ ] Habilitar "Automatically delete head branches" em ambos

### SETUP-3 — Branch protection: status gate obrigatório
- [ ] `auraxis-web` → Settings → Branches → Add rule para `master` → Required status: `ci-passed`
- [ ] `auraxis-app` → Settings → Branches → Add rule para `master` → Required status: `ci-passed`
- [ ] Habilitar "Require branches to be up to date before merging"

### SETUP-4 — Lighthouse CI (opcional — melhora visibilidade de performance)
- [ ] Instalar GitHub App: github.com/apps/lighthouse-ci
- [ ] Adicionar `LHCI_GITHUB_APP_TOKEN` como secret em `auraxis-web`

### SETUP-5 — IAM trust policy AWS (legado, ainda pendente)
- [ ] Atualizar subject hints nos roles dev/prod para `auraxis-api` (renomeado antes)
- Referência: `.context/01_status_atual.md` seção PLT1.1

---

## Em aberto — produto (ordem de prioridade)

1. PLT1.1: ✅ CONCLUÍDO
2. PLT1.2: ✅ CONCLUÍDO
3. PLT1.3: ✅ CONCLUÍDO
4. PLT1.4: ✅ CONCLUÍDO
5. PLT1.5: ✅ CONCLUÍDO
6. WEB1: ✅ CONCLUÍDO — Nuxt 4.3.1 + @nuxt/eslint + quality stack
7. APP2 + Security tooling: ✅ CONCLUÍDO — jest-expo + Playwright + Dependabot + SonarCloud + Lighthouse + bundle analysis
8. **X4** — adoção faseada do Ruff em `auraxis-api` (fase advisory → substituição de flake8/black/isort, manter mypy)
9. **X3** — preparar fase 0 de desacoplamento Flask/FastAPI (auth/context/error adapters)
10. **B10** — questionário indicativo de perfil investidor
11. **B11** — persistir/expor perfil sugerido + taxonomy_version
12. **PLT-BACKEND-DOCS** — criar `steering.md` + `.context/quality_gates.md` em `auraxis-api` (ver relatório de autonomia)
13. F1..F4 — entidades auxiliares e integração em transações
14. G5 — seed de dados local
15. B7 — discovery OTP (bloqueado por provedor/compliance)

## Discovery (ideias)
- Exportação CSV/XLSX por período
- Importação de relatórios bancários + conciliação
- Insights com LLM
- Aba de ferramentas financeiras
- Open Finance (fase posterior)

## Discovery (materializado)
- J1..J5 detalhados em `.context/discovery/`.
- Roadmap consolidado em `.context/discovery/discovery_execucao_roadmap.md`.
