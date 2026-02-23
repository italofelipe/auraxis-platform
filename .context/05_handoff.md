# Handoff (Atual)

Data: 2026-02-22 (atualizado — PLT1.3 concluído)

## O que foi feito (rodada PLT1.3 — setup multi-repo para agentes)

### Submodules registrados
- `auraxis-app` (React Native + Expo SDK 54) — git inicializado, remote configurado, commits iniciais, registrado em `.gitmodules`.
- `auraxis-web` (Nuxt 3) — git inicializado, remote configurado, commits iniciais, registrado em `.gitmodules`.
- `.git/modules/repos/{auraxis-app,auraxis-web}` — git dirs absorvidos pelo submodule system da platform.

### Governance baseline em auraxis-app e auraxis-web
- `CLAUDE.md` — diretiva de identidade, session bootstrap, limites operacionais.
- `.gitignore` — adequado para cada stack (Expo / Nuxt).
- `tasks.md` — backlog inicial com estado atual e próximas tasks.
- `steering.md` — princípios técnicos, convenções e integrações externas.

### Scripts de plataforma atualizados
- `scripts/setup-submodules.sh` (NOVO) — setup one-shot para qualquer agente ou dev que clonar a platform. Verifica pré-requisitos, inicializa todos os submodules, roda o health check.
- `scripts/check-health.sh` (ATUALIZADO):
  - Detecção de `.git` file (submodule absorvido) além de `.git/` dir.
  - Stack check dedicado para `auraxis-app` (Mobile — Expo) e `auraxis-web` (Web — Nuxt).
  - Correção do nome `auraxis-app` (era `auraxis-mobile` no roteamento).
- `.context/11_repo_map.md` (ATUALIZADO) — mapa completo dos 3 submodules com remote URLs, stack e status.

## O que foi validado
- `check-health.sh`: todos os ✅ nos 3 repos. Só warnings esperados (platform uncommitted antes do commit, auraxis-web sem package.json por estar em bootstrap).
- `setup-submodules.sh --check`: detecta corretamente os 3 submodules e seu estado.
- Submodule pointers atualizados para os commits de governance baseline.

## Pendências manuais (ação do usuário)

### Ainda pendente de rodadas anteriores
- **AWS IAM**: atualizar trust policy dos roles dev/prod — subject hint mudou de
  `repo:italofelipe/flask-expenses-manager:environment:*` para
  `repo:italofelipe/auraxis-api:environment:*`.
- **SonarCloud**: renomear project key de `italofelipe_flask-expenses-manager`
  para `italofelipe_auraxis-api` e atualizar variável `SONAR_PROJECT_KEY` no GitHub.

### Novos — push dos repos para o GitHub
- **auraxis-app**: criar repo em github.com/italofelipe/auraxis-app e fazer push.
- **auraxis-web**: criar repo em github.com/italofelipe/auraxis-web e fazer push.

Comandos prontos para executar no terminal:
```bash
# Criar repos no GitHub (requer gh CLI ou acesso à web)
gh repo create italofelipe/auraxis-app --public --description "Auraxis mobile app — React Native + Expo"
gh repo create italofelipe/auraxis-web --public --description "Auraxis web app — Nuxt 3 + TypeScript"

# Push auraxis-app
cd repos/auraxis-app
git push -u origin main

# Push auraxis-web
cd ../auraxis-web
git push -u origin main
```

Após o push, os submodules deixarão de aparecer como `-SHA` (não inicializado) no `git submodule status`.

## Próximo passo recomendado
1. Usuário faz o push de `auraxis-app` e `auraxis-web` para o GitHub.
2. Usuário atualiza AWS IAM trust policy e SonarCloud project key.
3. Próxima sessão de agente pode iniciar **X4** (Ruff advisory em auraxis-api) ou **B10** (feature de produto).

## Commits desta rodada (platform)
- `fb96fd7` chore(submodules): register auraxis-app and auraxis-web as git submodules
- `6bd231a` chore(platform): update repo map and health check for 3-submodule layout
- `4f1420a` chore(submodules): advance auraxis-app and auraxis-web pointers to governance baseline commits

## Commits desta rodada (auraxis-app)
- `4f5aed7` chore(platform): add governance baseline (CLAUDE.md + .gitignore)
- `9d3b6a3` feat(app): initial expo project scaffold (SDK 54 + RN 0.81)
- `05ca2ff` chore(governance): add tasks.md and steering.md baseline

## Commits desta rodada (auraxis-web)
- `4817df7` chore(platform): add governance baseline (CLAUDE.md + .gitignore) and initial README
- `2b138fa` chore(governance): add tasks.md and steering.md baseline
