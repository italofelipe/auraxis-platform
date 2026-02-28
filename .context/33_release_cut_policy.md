# Release Cut Policy (PLT3.1)

Atualizado: 2026-02-27

## Objetivo

Definir um fluxo único de release para `auraxis-api`, `auraxis-web` e `auraxis-app`, com previsibilidade operacional e baixo risco de drift entre repositórios.

## Cadência

- `main/master` permanece sempre deployável.
- Releases seguem janela semanal por padrão.
- Hotfix pode furar fila quando houver:
  - incidente em produção;
  - vulnerabilidade de segurança com severidade alta/crítica;
  - quebra de contrato público.

## Estratégia de versionamento

- Base canônica: Conventional Commits + release-please.
- Sem bump manual de versão.
- Qualquer mudança breaking exige:
  - marcador semântico explícito (`feat!` ou `BREAKING CHANGE`);
  - plano de migração documentado (compat policy + handoff).

## Regras de freeze

- Freeze parcial de release inicia no momento de criação/cálculo da release PR.
- Durante freeze:
  - permitido: correções de release/hotfix e ajustes de pipeline;
  - não permitido: features não relacionadas ao release cut ativo.
- Se houver bloqueio em gate crítico, release volta para estado de preparo e o freeze é encerrado.

## Gate mínimo obrigatório (todos os repos)

- lint + typecheck + testes + cobertura mínima.
- segurança (secret scan + dependency gate).
- Sonar em CI scanner obrigatório.
- contrato (OpenAPI/contract packs) sem drift.

## Política de Sonar local vs CI

- CI: sempre `enforce` (bloqueante).
- Local developer loop:
  - permitido modo `advisory` para evitar bloqueio por indisponibilidade/latência de gate remoto;
  - nunca substitui o gate bloqueante do CI.
- Na API, o hook local foi padronizado para esse comportamento via `scripts/sonar_local_check.sh`.

## Fluxo de hotfix

1. Criar branch `hotfix/<escopo-curto>`.
2. Aplicar correção mínima e reversível.
3. Rodar gates locais relevantes.
4. Abrir PR com etiqueta/descrição de hotfix.
5. Merge + deploy acelerado.
6. Registrar incidente e prevenção em docs/runbook/TASKS.

## Checklist de aprovação de PR de release

1. Todos os required checks verdes.
2. Sem conflito entre tasks.md/TASKS.md e artefatos implementados.
3. Handoff atualizado com riscos residuais.
4. Rollback conhecido e validado em runbook.
5. Nenhum drift de contrato (`contracts:check`) no frontend.
6. Security hotspots críticos triados/aceitos formalmente.

## Critério de pronto (Done) para PLT3.1

- Policy versionada e referenciada no índice de contexto.
- Checklist de aprovação disponível para agentes.
- Fluxo padronizado válido para API, Web e App.
