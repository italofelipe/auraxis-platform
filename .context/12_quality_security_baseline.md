# Quality and Security Baseline

## Objetivo
Definir baseline agnóstica de stack para qualidade e segurança.

## Qualidade mínima obrigatória
- Lint em modo bloqueante.
- Type-check em modo bloqueante.
- Testes automatizados em CI.
- Cobertura mínima definida por repo e evoluída gradualmente.

## Segurança mínima obrigatória
- Secret scanning em pre-commit e CI.
- SAST e audit de dependências em CI.
- Política de atualização de dependências com janela regular.
- Hardening de headers, auth, validação e sanitização nas fronteiras.

## Governança de vulnerabilidades
- Severidade crítica/alta: tratar prioritariamente.
- Registrar exceções com prazo e justificativa.
- Reavaliar backlog de segurança periodicamente.

## Confiabilidade de release
- Smoke test pós-deploy.
- Evidência de rollback documentada.
- Logs e trilha de auditoria para fluxos sensíveis.
