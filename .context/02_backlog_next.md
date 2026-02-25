# Próximas Prioridades

Atualizado: 2026-02-25

## Estado dos blocos de plataforma

1. `PLT2` (stores app + PWA): **45%**
2. `PLT3` (versionamento automático multi-repo): **65%**
3. `PLT4` (feature toggles OSS): **55%**
4. `PLT5` (deploy mínimo frontends): **60%**

## Entregas concluídas sem ação manual

1. **PLT4.1** — Automação de higiene de flags
- Gate bloqueante no CI de web/app/api para validar owner, removeBy e expiração de flags.
- Paridade local atualizada nos scripts de CI-like.

## Próximas entregas (sem depender de ação manual)

1. **PLT4.2** — Integração runtime de flags
- Conectar runtime web/app/api ao provider OSS com fallback local.

2. **PLT3.1** — Fechar policy de release cut
- Consolidar política operacional de release (cadência, freeze, hotfix) e checklist de aprovação de PR de release.

3. **PLT5.1** — Hardening de smoke checks pós-deploy
- Automatizar smoke mínimo (`/` e `/health`) após deploy baseline no web/app.

4. **API-local-resilience** — Fechar fricção de ambiente local
- Normalizar entrypoints Python da `.venv` (shebang legado) para evitar execução inconsistente em máquinas novas.

## Pendências manuais (executar quando disponível)

1. Credenciais e cadastros de loja (Play Store / App Store Connect).
2. Secrets finais para release/submissão (`EXPO_TOKEN`, IDs de store, assinaturas).
3. Habilitação operacional final de ambientes de deploy público.

Referência operacional: `tasks_status/PLT2-PLT5_manual_steps.md`.

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

## Tech debt estrutural

1. `X4` — adoção faseada do Ruff no backend.
2. `X3` — plano de desacoplamento Flask/FastAPI (fase 0).
