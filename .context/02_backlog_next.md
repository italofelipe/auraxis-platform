# Próximas Prioridades

Atualizado: 2026-02-28

## Sprint A — Autonomia operacional (P0)

Status:
- ✅ Auto-prepare de repositórios antes do run (`scripts/prepare-repo-for-agent-run.sh` + integração no `ai-next-task.sh`).
- ✅ Bloqueio hard de `task_id drift` no orquestrador multi-repo.
- ✅ Health check ampliado para detectar `detached HEAD` e mismatch de Node local vs CI.
- ✅ Runtime local Node `25.x` padronizado em app/web (paridade com CI).
- ✅ Hardening pós-mortem (P0/P1/P2): isolamento por worktree efêmero, rollback automático em bloqueio e regra hard de evidência para `Done`.

## Estado dos blocos de plataforma

1. `PLT2` (stores app + PWA): **45% — DEFERRED**
2. `PLT3` (versionamento automático multi-repo): **75%**
3. `PLT4` (feature toggles OSS): **96%**
4. `PLT5` (deploy mínimo frontends): **60% — DEFERRED (publicação externa)**

## Entregas concluídas sem ação manual

1. **PLT4.1** — Automação de higiene de flags
- Gate bloqueante no CI de web/app/api para validar owner, removeBy e expiração de flags.
- Paridade local atualizada nos scripts de CI-like.

## Próximas entregas (sem depender de ação manual)

1. **PLT4.2** — Integração runtime de flags ✅
- Runtime `unleash` + fallback local integrado em web/app/api.

2. **PLT4.3** — Bootstrap central de provider por ambiente ✅
- Script central (`scripts/bootstrap-feature-flag-provider.sh`) + runbook (`.context/34_feature_flag_provider_bootstrap.md`).
- Injeção automática no `scripts/ai-next-task.sh` para runs autônomos sem setup manual.

3. **PLT3.1** — Fechar policy de release cut ✅
- Política consolidada em `.context/33_release_cut_policy.md` (cadência, freeze, hotfix e checklist de aprovação).

4. **BLK-BACKEND-FEATURES** — Fechar bloco funcional backend atual
- Concluir backlog funcional ativo do backend antes de retomar publicação externa.

5. **API-local-resilience** — Fechar fricção de ambiente local
- Normalizar entrypoints Python da `.venv` (shebang legado) para evitar execução inconsistente em máquinas novas.

## Pendências manuais (DEFERRED para pós-bloco backend)

1. Credenciais e cadastros de loja (Play Store / App Store Connect).
2. Secrets finais para release/submissão (`EXPO_TOKEN`, IDs de store, assinaturas).
3. Habilitação operacional final de ambientes de deploy público (AWS web).

Referência operacional: `tasks_status/PLT2-PLT5_manual_steps.md`.

## Política operacional vigente

1. Até fechar o bloco funcional backend atual, o fluxo é **local-first**:
- app: Android Studio/Xcode + builds locais/EAS preview sem submissão.
- web: execução local e validação técnica sem publicação externa.

## Backlog funcional (produto)

1. `B10` — questionário indicativo de perfil investidor.
2. `B11` — persistência/exposição do perfil sugerido.
3. `B12` + `J6` — calculadora "Pedir aumento" (backend + ferramentas frontend).
4. `F1..F4` — entidades auxiliares e integração transacional.
5. `G5` — seed local.
6. `B7` — discovery OTP (bloqueado por compliance/provedor).

## Fila de discovery (refinar apos ciclo atual de execucao)

1. `J6` — Web: paginas publicas/privadas e SEO institucional.
2. `J7` — Ferramentas hibridas (publico + logado) com simulacao persistivel.
3. `J8` — Newsletter e growth loop.
4. `J9` — Integracao de meios de pagamento (BRL, parcelamento, baixa taxa).
5. `J10` — Feed de noticias de economia com IA/scrapers.
6. `J11` — Alertas por email de pendencias e contas a vencer.

## Tech debt estrutural

1. `X4` — adoção faseada do Ruff no backend.
2. `X3` — plano de desacoplamento Flask/FastAPI (fase 0).
