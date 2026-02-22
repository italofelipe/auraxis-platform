# Repo Bootstrap Checklist

## Antes de criar um novo repo
- Definir objetivo e fronteira do repo.
- Definir contrato com demais repos.
- Definir dono principal e política de revisão.

## Estrutura mínima no repo
- `README.md` (breve)
- `tasks.md` (status e progresso)
- `steering.md` (regras locais)
- `AGENTS.md` (instruções para IA)
- `docs/adr/` (decisões arquiteturais)

## Pipeline mínimo
- CI com lint + testes + segurança.
- Política de branch protection.
- Deploy strategy definida (quando aplicável).

## Observabilidade mínima
- Healthcheck.
- Logging estruturado.
- Indicadores de erro.
