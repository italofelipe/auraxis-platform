# Handoff (Atual)

Data: 2026-02-22 (atualizado — PLT1.1 + PLT1.2 concluídos)

## O que foi feito (rodada PLT1.1 — renomeação e submodule)
- Repo GitHub renomeado de `flask-expenses-manager` → `auraxis-api`.
- Remote local atualizado para `git@github.com:italofelipe/auraxis-api.git`.
- `auraxis-api` registrado como submodule oficial em `auraxis-platform` (`.gitmodules`).
- `scripts/aws_iam_audit_i8.py`: OIDC subject hints corrigidos para `auraxis-api`.
- `docs/RUNBOOK.md`: procedimento de recovery atualizado para layout de submodule.
- `docs/STABILIZATION_01_TRACEABILITY.md`: task de renomeação marcada como concluída.
- `.claude/settings.local.json`: paths obsoletos do diretório antigo removidos (arquivo local, não versionado).
- `.mypy_cache` limpo (tinha paths absolutos do diretório antigo, causava crash no pre-commit).
- Pointer do submodule na platform avançado para incluir todos os commits de cleanup.

## O que foi feito (rodada PLT1.2 — setup de orquestração)
- `CLAUDE.md` criado na raiz do `auraxis-platform`.
- `scripts/check-health.sh`, `bootstrap-repo.sh`, `agent-lock.sh` criados.
- `.context/agent_lock.schema.json` — schema JSON do protocolo de lock.
- `workflows/` populado com 3 documentos executáveis.
- `ai_integration-claude.md`, `ai_integration-gemini.md`, `ai_integration-gpt.md` na raiz.

## O que foi validado
- `check-health.sh`: plataforma com todos os ✅ (submodule agora reconhecido).
- `agent-lock.sh`: acquire/status/release testados e funcionando.
- Pre-commit do `auraxis-api` passando (black, flake8, isort, bandit, gitleaks, mypy).
- Submodule apontando para `b138d11` (último commit de cleanup).

## Pendências manuais (ação do usuário)
- **AWS IAM**: atualizar trust policy dos roles dev/prod — subject hint mudou de
  `repo:italofelipe/flask-expenses-manager:environment:*` para
  `repo:italofelipe/auraxis-api:environment:*`.
- **SonarCloud**: renomear project key de `italofelipe_flask-expenses-manager`
  para `italofelipe_auraxis-api` e atualizar variável `SONAR_PROJECT_KEY` no GitHub.

## Próximo passo recomendado
1. **X4**: iniciar execução da adoção faseada de Ruff (advisory → substituição de flake8/black/isort).
2. **B10**: questionário indicativo de perfil investidor (próxima feature de produto).

## Riscos/atenções
- Deploy CI/CD falhará até que a trust policy do IAM seja atualizada (subject hint antigo não casa mais).
- SonarCloud vai criar um novo projeto com nome errado se o key não for atualizado antes do próximo push.
- Adotar Ruff sem rollout faseado pode gerar ruído de estilo.

## Commits desta rodada (platform)
- `aa003b4` chore(submodule): register auraxis-api as git submodule
- `b548bd7` chore(submodule): advance auraxis-api pointer after rename cleanup

## Commits desta rodada (auraxis-api)
- `d6f03fe` fix(aws): update OIDC subject hints to auraxis-api repo name
- `33f28b0` docs(runbook): update workspace recovery procedure for auraxis-api rename
- `b138d11` docs(traceability): mark path/name update task as done after rename
