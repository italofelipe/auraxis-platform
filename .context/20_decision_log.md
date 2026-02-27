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

**Atualização (2026-02-24):** após desativação do Automatic Analysis no SonarCloud (app/web), o modo estrito de Sonar em CI foi reativado. O fallback de dependency-review permanece temporariamente.

---

### DEC-018 — Branch protection sem aprovador obrigatório (solo maintainer)

**Decisão:** manter proteção de branch com PR/checks, porém sem exigência de aprovação de review (`required_approving_review_count=0`).

**Racional:** o projeto está em operação por um único mantenedor; exigir aprovador bloqueia merge sem ganho real de segregação de funções.

**Alternativas rejeitadas:**
- Manter 1 aprovação obrigatória e usar autoaprovação/manual workaround.
- Remover totalmente `required_pull_request_reviews`.

**Dono:** maintainer do repositório.
**Impacto:** merge destravado para fluxo solo, mantendo os gates automáticos obrigatórios de CI/segurança.

---

### DEC-019 — Remover `passWithNoTests` com baseline mínimo real em app/web

**Decisão:** concluir `APP9` e `WEB10` removendo o bypass `--passWithNoTests` e introduzindo suítes reais mínimas para manter gate de teste estritamente bloqueante.

**Racional:** manter bypass em scaffold inicial mascara regressões e reduz confiabilidade de agentes autônomos. O baseline mínimo permite evolução incremental sem travar o fluxo por cobertura inexistente.

**Alternativas rejeitadas:**
- manter `passWithNoTests` até início das features;
- remover bypass sem introduzir suíte real (quebraria pipeline imediatamente).

**Dono:** plataforma + owners frontend.
**Impacto:** testes tornam-se obrigatórios desde já; backlog técnico remanescente é expandir escopo de cobertura em `APP8`/`WEB8`.

---

### DEC-020 — Perfil ESLint estrito e consistente em app/web

**Decisão:** padronizar `auraxis-app` e `auraxis-web` com perfil ESLint estrito (estilo + complexidade + disciplina TypeScript), mantendo abordagem mista OO/funcional.

**Racional:** agentes/autoria híbrida aumentam risco de variação de estilo e complexidade acidental. Regras estritas com `--max-warnings 0` reduzem drift e melhoram previsibilidade em revisão e manutenção.

**Alternativas rejeitadas:**
- manter apenas regras padrão de Expo/Nuxt;
- impor OO puro em toda a base (incompatível com padrões idiomáticos de UI React/Vue).

**Dono:** plataforma + owners frontend.
**Impacto:** padronização obrigatória de estilo e limites de complexidade; camadas de domínio/aplicação seguem orientação mais OO, enquanto UI/composables seguem estilo funcional com guardrails.

---

### DEC-021 — Coverage mínimo de 85% e normalização de URL sem regex vulnerável

**Decisão:** padronizar o piso mínimo de cobertura em `85%` para `lines/functions/statements/branches` nos projetos frontend (`auraxis-app` e `auraxis-web`) e proibir normalização de base URL com regex potencialmente suscetível a backtracking.

**Racional:** o modelo de execução com agentes autônomos exige gates determinísticos de qualidade e segurança. O alerta do Sonar sobre regex em trim de barras finais aponta risco de ReDoS; a substituição por algoritmo linear elimina esse vetor. O threshold único de 85% reduz ambiguidade entre repos e evita regressão silenciosa de testes em código novo.

**Alternativas rejeitadas:**
- manter thresholds distintos (80/85) entre app e web;
- manter regex com exceção/waiver no Sonar;
- reduzir rigor de branches para acelerar merge.

**Dono:** plataforma + owners frontend.
**Impacto:** `jest.config.js` e `vitest.config.ts` alinhados para 85% global; testes do cliente API em app/web ampliados; documentação de governança e quality gates atualizada.

---

### DEC-022 — CI-like local obrigatório para frontend + dependency-review compatível por capability

**Decisão:** adotar scripts `run_ci_like_actions_local.sh` em `auraxis-app` e `auraxis-web` para espelhar os gates críticos do GitHub Actions localmente; para `dependency-review`, executar gate estrito somente quando `Dependency Graph` estiver disponível/habilitado no repositório e aplicar fallback explícito com warning quando não estiver.

**Racional:** o principal ruído recente veio de diferenças entre ambiente local e CI, além de falhas não determinísticas em `dependency-review` por limitação de capability do repositório. A combinação de CI-like local + fallback capability-aware reduz quebra surpresa sem mascarar riscos.

**Alternativas rejeitadas:**
- manter `dependency-review` estrito sem capability check (quebra contínua quando repo não suportar);
- desabilitar `dependency-review` permanentemente;
- manter lógica de audit inline em YAML (drift alto entre local e CI).

**Dono:** plataforma + owners frontend.
**Impacto:** pipelines frontend mais previsíveis; auditoria de dependências reutiliza scripts versionados; execução local passa a ser pré-condição prática antes de push em blocos críticos.

---

### DEC-023 — Sistema visual unificado + stack de UI oficial no frontend

**Decisão:** padronizar `auraxis-web` e `auraxis-app` com um sistema visual único e stack de UI oficial:
- paleta oficial: `#262121`, `#ffbe4d`, `#413939`, `#0b0909`, `#ffd180`, `#ffab1a`;
- tipografia oficial: `Playfair Display` (headings) + `Raleway` (body);
- grid base: `8px`;
- web com componentes baseados em **Chakra UI** (customizados);
- mobile com **React Native Paper** como padrão (substituição apenas via ADR);
- **Tailwind proibido** nas duas plataformas.

**Racional:** agentes autônomos exigem regras visuais e tecnológicas explícitas para evitar drift de implementação e inconsistência entre app/web. Definir paleta/fonte/grid e biblioteca-base reduz ambiguidade de código gerado e acelera revisão.

**Alternativas rejeitadas:**
- manter liberdade de escolha de UI kit por tarefa/agente;
- continuar com utilitários Tailwind no frontend;
- adiar padronização visual para fase pós-features.

**Dono:** plataforma + owners frontend.
**Impacto:** `steering.md`, `CODING_STANDARDS.md`, `tasks.md` e arquitetura frontend passam a exigir o padrão unificado; backlog de migração/adoção de UI base e server-state fica explícito.

---

### DEC-024 — `ai_squad` promovido para nível de platform + telemetria local `tasks_status`

**Decisão:** mover `ai_squad` de `repos/auraxis-api/ai_squad` para `auraxis-platform/ai_squad`, mantendo execução funcional e adicionando resolução de repo-alvo por ambiente:
- `AURAXIS_TARGET_REPO` (default: `auraxis-api`);
- `AURAXIS_PROJECT_ROOT` (override explícito).

Além disso, padronizar telemetria operacional local dos agentes em `auraxis-platform/tasks_status/` para status de execução e bloqueios.

**Racional:** o squad não deve ser acoplado fisicamente a um único repo de produto. No nível de plataforma, o orquestrador fica alinhado ao modelo multi-repo e facilita expansão futura para web/app. O diretório `tasks_status` melhora coordenação entre agentes em paralelo sem competir com a fonte oficial de status (`tasks.md`/`TASKS.md`).

**Alternativas rejeitadas:**
- manter `ai_squad` dentro de `auraxis-api`;
- centralizar status operacional dentro de `tasks.md` (aumenta ruído e conflita com rastreio oficial);
- versionar `tasks_status` no git.

**Dono:** plataforma.
**Impacto:** scripts/documentação atualizados para novo entrypoint; `tasks_status/` passa a ser artefato local ignorado no git; `TASKS.md/tasks.md` permanece como única fonte de verdade de progresso.

---

### DEC-025 — Remover gate sintético `CI Passed` e exigir checks reais por repo

**Decisão:** descontinuar o job agregador `ci-passed` nos pipelines de `auraxis-web` e `auraxis-app`, e atualizar a política de branch protection para exigir diretamente os checks reais de CI (lint/typecheck/test/build/security/sonar/dependency review).

Para `auraxis-api`, manter sem `ci-passed` (já inexistente no workflow) e remover sua exigência residual em branch protection.

**Racional:** o check sintético gera acoplamento desnecessário, risco de pendência infinita quando o contexto não existe no workflow e pouca observabilidade sobre qual gate real falhou. Exigir checks reais simplifica debugging e reduz falsos bloqueios.

**Alternativas rejeitadas:**
- manter `ci-passed` e tentar estabilizar por ajustes incrementais;
- remover required checks e confiar apenas em disciplina manual;
- exigir somente um check mínimo (ex.: dependency review).

**Dono:** plataforma + owners de repo.
**Impacto:** workflows ficam mais simples, branch protection mais explícita e alinhada com os jobs efetivos de cada produto.

---

### DEC-026 — PLT4.1 obrigatório: hygiene gate de feature flags no CI

**Decisão:** tornar obrigatória a validação de lifecycle de flags em todos os repositórios de produto (`auraxis-web`, `auraxis-app`, `auraxis-api`) com catálogo versionado + gate bloqueante no CI.

**Racional:** sem enforcement automático, flags ficam sem owner/removal-date e acumulam débito técnico invisível. O gate reduz risco de drift e impede rollout sem governança mínima.

**Alternativas rejeitadas:**
- manter validação manual em review;
- aplicar gate apenas em um repositório;
- validar somente formato, sem checar expiração.

**Dono:** plataforma + owners de repo.
**Impacto:** novos validadores locais/CI adicionados; qualquer flag sem `owner`/`removeBy` ou expirada sem cleanup bloqueia pipeline.

---

### DEC-027 — Postergar publicação externa até fechar bloco funcional backend atual

**Decisão:** postergar o ciclo de publicação externa (Play Store/App Store para app e publicação web pública) para depois do fechamento do bloco funcional backend atualmente em execução.

**Racional:** o setup de publicação em lojas exige custos e overhead operacional neste momento. O foco imediato é estabilidade de fundação + entrega de features backend com validação local de frontend/mobile.

**Alternativas rejeitadas:**
- manter trilha de publicação externa em paralelo com backend;
- avançar com App Store neste ciclo (custo imediato sem ganho de curto prazo);
- forçar release público antecipado da web antes do fechamento funcional backend.

**Dono:** maintainer + plataforma.
**Impacto:** estratégia operacional passa a ser local-first temporariamente:
- app: Android Studio/Xcode e builds de preview sem submissão;
- web: execução/validação local sem release público;
- retomada de PLT2/PLT5 externo somente após conclusão do bloco backend.

---

### DEC-028 — Checkpoint de validação do app antes da próxima major feature backend (sem freeze)

**Decisão:** não adotar freeze formal do backlog backend. Em vez disso, sempre que um bloco backend atual for concluído, a próxima major feature backend só inicia após subir/validar uma versão do app (preview/internal) para verificação integrada.

**Racional:** evita acúmulo de drift entre backend e app sem travar a evolução contínua do backlog backend. Mantém cadência de validação real em dispositivo sem impor overhead de congelamento.

**Alternativas rejeitadas:**
- congelar backend antes de cada ciclo de validação do app;
- adiar validações do app para milestones longos;
- validar apenas por testes locais sem build/install real.

**Dono:** maintainer + plataforma.
**Impacto:** política de execução:
- backend segue com backlog próprio sem freeze;
- checkpoint obrigatório de app release/preview antes de iniciar próxima major feature backend;
- novos itens adicionados ao backend podem coexistir, respeitando o checkpoint entre blocos maiores.

---

### DEC-029 — Design assets em `designs/` como fonte visual canonica para frontend

**Decisão:** oficializar os arquivos `designs/1920w default.png` e `designs/Background.svg` como
fonte visual canonica para tarefas de layout no `auraxis-web` e `auraxis-app`, com execução
padronizada via `.context/30_design_reference.md`.

**Racional:** a autonomia dos agentes depende de reduzir ambiguidade na interpretacao de layout.
Sem referencia visual explicita, agentes tendem a gerar variacoes nao alinhadas ao tema e a
hierarquia de blocos. O spec visual centraliza tokens extraidos, composicao esperada e criterios
de aceite para diminuir retrabalho.

**Alternativas rejeitadas:**
- manter apenas instrucoes textuais de paleta/tipografia sem blueprint visual;
- deixar cada repo frontend definir seu proprio reference file;
- interpretar imagens ad hoc por tarefa sem checklist operacional.

**Dono:** plataforma + owners frontend.
**Impacto:** leitura de design passa a ser mandatória para tarefas de UI/layout, com atualizacoes em:
- `.context/30_design_reference.md` (novo spec visual operacional);
- `.context/06_context_index.md` (indice de leitura complementar);
- `.context/08_agent_contract.md` (contrato de leitura para UI/layout);
- `.context/26_frontend_architecture.md` e `product.md` (vinculo com a fonte visual canonica).

---

### DEC-030 — Master run com comando único + remoção do `ai_squad` legado na API

**Decisão:** consolidar o orquestrador apenas em `auraxis-platform/ai_squad`, remover o legado
`repos/auraxis-api/ai_squad` e tornar o fluxo padrão de execução zero-overhead via
`make next-task`.

**Racional:** o objetivo operacional é permitir que o maintainer acione o sistema com um único
prompt/comando ("Execute a tarefa"), sem etapas manuais repetitivas de lock/env/target.
Manter cópia legado no repo da API gera ambiguidade e risco de desvio de execução.

**Alternativas rejeitadas:**
- manter dois `ai_squad` em paralelo (platform + api);
- exigir export manual de variáveis a cada run;
- deixar lock como passo opcional/manual no fluxo padrão.

**Dono:** plataforma.
**Impacto:**
- `repos/auraxis-api/ai_squad` removido;
- `ai_squad/main.py` com default multi-repo (`AURAXIS_TARGET_REPO=all`) e briefing padrão `Execute a tarefa`;
- `scripts/ai-next-task.sh` com bootstrap de venv automático + lock acquire/release automático;
- `make next-task` definido como interface principal para acionar o master.

---

## Decisões pendentes

| ID | Tema | Bloqueador | Prazo estimado |
|:---|:-----|:-----------|:---------------|
| DEC-009 | ADR formal de stack web (Nuxt 3) | nenhum | ao iniciar WEB1 |
| DEC-010 | ADR formal de stack mobile (Expo) | nenhum | ao iniciar APP2 |
| DEC-011 | Estratégia de CI cross-repo (contract testing) | `auraxis-api` precisa exportar schema versionado | após X4 |
| DEC-012 | Política de shared types entre repos | DEC-011 | após DEC-011 |
| DEC-013 | Avaliação pyright vs. mypy | X4 concluído | após X4 |
