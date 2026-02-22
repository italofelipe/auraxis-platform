# Próximas Prioridades

## Em aberto imediato
1. PLT1.1: migrar backend para `repos/auraxis-api` e validar checklist pós-migração (`.context/22_workspace_migration_checklist.md`)
2. PLT1.2: concluir estratégia operacional de multi-repo (submodules vs pastas locais) com governança/CI basal
3. X4: iniciar plano de adoção do Ruff (fase advisory -> substituição de flake8/black/isort), mantendo `mypy`
4. X3: preparar fase 0 de desacoplamento para coexistência Flask/FastAPI (auth/context/error adapters)
5. B10: questionário indicativo de perfil investidor
6. B11: persistir/expor perfil sugerido + taxonomy_version
7. F1..F4: entidades auxiliares e integração em transações
8. G5: seed de dados local
9. B7: discovery OTP (bloqueado por provedor/compliance)

## Discovery (ideias)
- Exportação CSV/XLSX por período
- Importação de relatórios bancários + conciliação
- Insights com LLM
- Aba de ferramentas financeiras
- Open Finance (fase posterior)

## Discovery (materializado)
- J1..J5 detalhados em `.context/discovery/`.
- Roadmap consolidado em `.context/discovery/discovery_execucao_roadmap.md`.
