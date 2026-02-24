# Próximas Prioridades

## ✅ SETUP MANUAL — concluído

> Todos os itens abaixo foram realizados pelo usuário. CI, secrets e configurações de repo estão prontos.

### SETUP-1 — SonarCloud ✅
- [x] Token criado para `auraxis-web` → secret configurado no repo
- [x] Token criado para `auraxis-app` → secret configurado no repo
- [x] Token de `auraxis-api` confirmado funcional (setup antigo)

### SETUP-2 — GitHub: auto-merge ✅
- [x] `auraxis-web` → Allow auto-merge habilitado
- [x] `auraxis-app` → Allow auto-merge habilitado
- [x] "Automatically delete head branches" habilitado em ambos

### SETUP-3 — Branch protection: status gate ✅
- [x] `auraxis-web` → Required status: `ci-passed` no master
- [x] `auraxis-app` → Required status: `ci-passed` no master
- [x] "Require branches to be up to date before merging" habilitado

### SETUP-4 — Lighthouse CI ✅
- [x] GitHub App instalado
- [x] `LHCI_GITHUB_APP_TOKEN` configurado como secret em `auraxis-web`

### SETUP-5 — IAM trust policy AWS (débito técnico — não bloqueante)
> Reclassificado: não é crítico para operação dos agentes. Deve ser feito oportunisticamente.
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
8. PLT-BACKEND-DOCS: ✅ CONCLUÍDO — `steering.md` atualizado + `.context/quality_gates.md` criado + `CODING_STANDARDS.md` criado em `auraxis-api`
9. **X4** — adoção faseada do Ruff em `auraxis-api` (fase advisory → substituição de flake8/black/isort, manter mypy)
10. **X3** — preparar fase 0 de desacoplamento Flask/FastAPI (auth/context/error adapters)
11. **APP9** — baseline de testes no app para remover `--passWithNoTests`
12. **WEB10** — baseline de testes no web para remover `--passWithNoTests`
13. **WEB9** — dockerizar `auraxis-web` (Nuxt) com `Dockerfile` + `.dockerignore` + runbook de execução
14. **B10** — questionário indicativo de perfil investidor
15. **B11** — persistir/expor perfil sugerido + taxonomy_version
16. F1..F4 — entidades auxiliares e integração em transações
17. G5 — seed de dados local
18. B7 — discovery OTP (bloqueado por provedor/compliance)

## Discovery (ideias)
- Exportação CSV/XLSX por período
- Importação de relatórios bancários + conciliação
- Insights com LLM
- Aba de ferramentas financeiras
- Open Finance (fase posterior)

## Discovery (materializado)
- J1..J5 detalhados em `.context/discovery/`.
- Roadmap consolidado em `.context/discovery/discovery_execucao_roadmap.md`.
