# Decision Log

Registro cronológico de decisões arquiteturais, técnicas e de processo.
Cada entrada responde: **o quê**, **por quê**, **alternativas rejeitadas**, **dono**, **impacto**.

---

## 2026-02-22

### DEC-001 — Criar `auraxis-platform` como repositório orquestrador

**Decisão:** o projeto terá um repo raiz (`auraxis-platform`) que não contém código de produto — apenas governança, contexto compartilhado, scripts e submodules.

**Racional:** múltiplos agentes (Claude, GPT, Gemini, CrewAI) precisam de uma fonte de verdade única para contexto, convenções e estado. Misturar isso dentro de um dos repos de produto criaria acoplamento e conflito de ownership.

**Alternativas rejeitadas:**
- Centralizar em `auraxis-api` (acoplamento desnecessário ao backend).
- Usar um repositório de documentação separado sem submodules (sem rastreabilidade de estado dos repos).

**Dono:** humano (Italo) + Claude (governança).
**Impacto:** todos os agentes leem `.context/` antes de agir. Custo inicial de setup; ganho de alinhamento contínuo.

---

### DEC-002 — Repositórios de produto separados como git submodules

**Decisão:** cada produto (`auraxis-api`, `auraxis-app`, `auraxis-web`) é um repositório independente, registrado como submodule em `auraxis-platform`.

**Racional:** permite deploys independentes, pipelines de CI isolados, ownership claro de domínio por agente, e histórico git limpo por produto. Submodules garantem rastreabilidade exata de qual commit de cada produto está integrado.

**Alternativas rejeitadas:**
- Monorepo único: mais simples, mas cria acoplamento de deploy e torna difícil isolar agentes por domínio.
- Repos separados sem submodule: perde rastreabilidade e dificulta onboarding automatizado.

**Dono:** humano (Italo).
**Impacto:** novos repos requerem `git submodule add` + push + init. Clone exige `--recurse-submodules`. Script `setup-submodules.sh` mitiga o atrito.

---

### DEC-003 — Centralizar governança em `.context/` na platform

**Decisão:** toda decisão de arquitetura, processo, qualidade e contrato é registrada em `.context/` dentro de `auraxis-platform`. Repos de produto mantêm apenas contexto local (`tasks.md`, `steering.md`, `CLAUDE.md`).

**Racional:** agentes com contexto de sessão limitado precisam de um ponto de entrada predefinido. Redundância entre repos geraria drift e contradições.

**Alternativas rejeitadas:**
- Wiki no GitHub: fora do controle de versão junto com o código.
- Notion/Confluence: inacessível por agentes sem integração específica.

**Dono:** Claude (manutenção), humano (aprovação de mudanças estruturais).
**Impacto:** todo agente DEVE ler `.context/06_context_index.md` antes de qualquer ação. `.context/` cresce conforme o projeto, mas tem política de manutenção em `19_context_maintenance.md`.

---

### DEC-004 — Stack web: Nuxt 3 + TypeScript + Biome

**Decisão:** `auraxis-web` usará Nuxt 3 como framework SSR/SPA, TypeScript strict, e Biome para lint/format (substituindo ESLint + Prettier).

**Racional:** Nuxt 3 oferece file-based routing, SSR nativo e ecossistema Vue maduro. Biome unifica lint e format em uma ferramenta, reduzindo configuração e aumentando velocidade.

**Alternativas rejeitadas:**
- Next.js (React): preferência de stack Vue no frontend web.
- Remix: menor ecossistema no contexto atual.
- ESLint + Prettier: dois processos separados, mais configuração, Biome cobre os dois com melhor performance.

**Dono:** humano (Italo).
**Status:** ADR formal pendente (a criar em `repos/auraxis-web/docs/adr/`).
**Impacto:** define toolchain de CI para `auraxis-web`.

---

### DEC-005 — Stack mobile: React Native + Expo SDK 54

**Decisão:** `auraxis-app` usará React Native com Expo SDK 54 e Expo Router para navegação file-based.

**Racional:** Expo simplifica o ciclo de build/preview, elimina a necessidade de Xcode/Android Studio para desenvolvimento inicial, e Expo Router alinha a convenção de navegação com o file-based routing do Nuxt.

**Alternativas rejeitadas:**
- Flutter: curva de aprendizado e ecossistema Dart separado do TypeScript.
- React Native sem Expo (bare): overhead de configuração de builds sem ganho no estágio atual.

**Dono:** humano (Italo).
**Status:** ADR formal pendente.
**Impacto:** define pipeline EAS Build/Update para CI mobile.

---

### DEC-006 — Executar X4 (Ruff) antes de X3 (FastAPI) em `auraxis-api`

**Decisão:** a adoção do Ruff (substituindo flake8/black/isort) precede qualquer trabalho de migração Flask → FastAPI.

**Racional:** X4 tem escopo contido (toolchain, sem impacto em runtime), entrega DX imediato e não requer pré-condições arquiteturais. X3 exige adapters de auth/error/observabilidade framework-agnósticos, o que é trabalho de maior risco. Fazer X3 antes de X4 significa migrar com toolchain legado.

**Alternativas rejeitadas:**
- X3 primeiro: maior risco, requer pré-condições não resolvidas.
- Simultâneo: conflito de escopo em PR review e aumento de noise em diff.

**Dono:** Claude (execução técnica), humano (aprovação).
**Impacto:** afeta `.pre-commit-config.yaml`, `pyproject.toml` e CI de `auraxis-api`.

---

### DEC-007 — Migração Flask → FastAPI por coexistência faseada (X3)

**Decisão:** quando X3 for iniciado, Flask e FastAPI coexistirão no mesmo processo por prefixo de rota, sem big-bang. Flask mantém rotas existentes; FastAPI recebe novas rotas.

**Racional:** migração big-bang é alto risco em API com contratos vivos. Coexistência permite rollback por rota, validação incremental, e zero downtime.

**Alternativas rejeitadas:**
- Reescrita completa: risco de regressão total, downtime, e perda de contexto de segurança acumulado.
- Novo serviço separado: overhead de infra, problema de autenticação compartilhada.

**Dono:** Claude/GPT (execução), humano (aprovação de cada fase).
**Status:** bloqueado — pré-condições não atendidas (auth adapter, error contract, observabilidade cross-framework). Ver `tech_debt/X3_fastapi_migration_coexistence.md`.

---

### DEC-008 — `mypy` mantido como gate obrigatório durante X4

**Decisão:** Ruff não substitui `mypy`. Type-checking estrito continua como gate bloqueante mesmo após adoção completa do Ruff.

**Racional:** Ruff não faz inferência de tipos profunda. O projeto já tem tipagem estrita consolidada (`disallow_untyped_defs`, `strict = true`). Reduzir o rigor durante uma migração de toolchain introduziria regressão silenciosa de segurança de tipos.

**Alternativas rejeitadas:**
- Substituir mypy por pyright: pode ser avaliado em item separado, não durante X4.
- Remover type-checking: não aceitável dado o nível atual de cobertura.

**Dono:** Claude.
**Impacto:** `.pre-commit-config.yaml` mantém hook `mypy` após remoção de flake8/black/isort.

---

## 2026-02-24

### DEC-014 — Branch protection versionado como codigo para api/app/web

**Decisão:** versionar as regras de branch protection em JSON dentro da platform e aplicar via script de API (`curl + jq`), em vez de manter apenas configuração manual no UI do GitHub.

**Racional:** reduz drift entre repositórios, permite auditoria por commit e acelera bootstrap de novos ambientes/agentes com a mesma política de proteção.

**Alternativas rejeitadas:**
- Configuração manual via UI: sem rastreabilidade e propensa a drift.
- Dependência exclusiva de GitHub Rulesets sem automação local: maior acoplamento a permissões/flows do UI.

**Dono:** plataforma (governança global).
**Impacto:** política de proteção para `auraxis-api`, `auraxis-app` e `auraxis-web` fica reproduzível e reaplicável via `scripts/apply-branch-protection.sh`.

**Execução (2026-02-24):** aplicado em produção para `italofelipe/auraxis-api:master`, `italofelipe/auraxis-app:main` e `italofelipe/auraxis-web:main`.

---

### DEC-015 — SonarCloud padronizado em CI scanner-only

**Decisão:** os 3 repositórios de produto devem operar SonarCloud exclusivamente por scanner em CI, com Automatic Analysis desabilitado no painel.

**Racional:** elimina conflito entre modos de análise, torna o gate determinístico por PR/pipeline e preserva rastreabilidade por commit/workflow.

**Alternativas rejeitadas:**
- Manter modo híbrido (automatic + CI): gera falhas intermitentes e ambiguidade de fonte de verdade.
- Usar apenas Automatic Analysis: reduz controle fino de parâmetros, coverage e sequência de gates no CI.

**Dono:** plataforma + owners de repo.
**Impacto:** workflows de app/web/api tornam-se a única via oficial de análise Sonar.

---

### DEC-016 — Dependency review estritamente bloqueante em frontend

**Decisão:** remover fallback permissivo dos workflows `dependency-review.yml` de `auraxis-app` e `auraxis-web`.

**Racional:** com branch protection exigindo `Dependency Review`, o fallback transformava um check obrigatório em sinal advisory, reduzindo efetividade do gate de supply-chain.

**Alternativas rejeitadas:**
- Manter fallback até novo ciclo: mantém lacuna de enforcement em PRs.
- Bloquear apenas por `npm/pnpm audit`: cobre runtime local, mas não substitui o gate de introdução de novas dependências vulneráveis no PR.

**Dono:** plataforma + frontend repos.
**Impacto:** o check de dependency-review passa a bloquear merge de forma consistente.

---

### DEC-017 — Modo compatibilidade temporário para CI frontend

**Decisão:** aplicar modo compatibilidade transitório em `auraxis-app` e `auraxis-web` para desbloquear CI enquanto configurações externas não estão estáveis:
- `dependency-review` com fallback controlado em erro de "repository not supported";
- `sonarcloud` condicionado por `ENABLE_SONAR_CI`.

**Racional:** houve falha sistêmica de pipeline por dependência de configuração fora do repositório (Dependency Graph e Automatic Analysis no SonarCloud). O modo compatibilidade evita bloqueio contínuo sem esconder a pendência.

**Alternativas rejeitadas:**
- Manter modo estrito e aceitar CI vermelho contínuo.
- Remover os checks dos workflows.

**Dono:** plataforma + owners frontend.
**Impacto:** CI volta a ser executável imediatamente; retorno ao modo estrito depende de ajustes manuais no GitHub/SonarCloud.

---

## Decisões pendentes

| ID | Tema | Bloqueador | Prazo estimado |
|:---|:-----|:-----------|:---------------|
| DEC-009 | ADR formal de stack web (Nuxt 3) | nenhum | ao iniciar WEB1 |
| DEC-010 | ADR formal de stack mobile (Expo) | nenhum | ao iniciar APP2 |
| DEC-011 | Estratégia de CI cross-repo (contract testing) | `auraxis-api` precisa exportar schema versionado | após X4 |
| DEC-012 | Política de shared types entre repos | DEC-011 | após DEC-011 |
| DEC-013 | Avaliação pyright vs. mypy | X4 concluído | após X4 |
