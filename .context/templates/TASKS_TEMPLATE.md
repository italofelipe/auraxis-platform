# tasks.md — [Nome do Repo]

Última atualização: YYYY-MM-DD

---

## Legenda

| Símbolo | Significado |
|:--------|:------------|
| `[ ]` | Todo — ainda não iniciado |
| `[~]` | In Progress — em andamento nesta sessão |
| `[!]` | Blocked — aguardando dependência externa |
| `[x]` | Done — concluído e verificado |

**Prioridade:** P0 = bloqueante / P1 = alta / P2 = normal / P3 = baixa

---

## Ciclo atual: [nome do ciclo, ex: Ciclo A — Fundação]

### P0 — Bloqueante

- [x] **[ID]-[SIGLA]** `feat` — [título curto]
  - Critério: [o que precisa ser verdade para marcar Done]
  - Dependência: [nenhuma | ID de outra task]
  - Commit: `abc1234`
  - Risco residual: nenhum

- [~] **[ID]-[SIGLA]** `fix` — [título curto]
  - Critério: [descrição objetiva]
  - Dependência: nenhuma
  - Commit: —
  - Risco residual: [descrever se houver]

### P1 — Alta

- [ ] **[ID]-[SIGLA]** `feat` — [título curto]
  - Critério: [descrição]
  - Dependência: [ID ou "nenhuma"]
  - Commit: —
  - Risco residual: —

### P2 — Normal

- [ ] **[ID]-[SIGLA]** `chore` — [título curto]
  - Critério: [descrição]
  - Dependência: nenhuma
  - Commit: —

### Bloqueados

- [!] **[ID]-[SIGLA]** — [título]
  - Bloqueador: [o que precisa acontecer para desbloquear]
  - Dono do bloqueio: [humano / agente / sistema externo]

---

## Concluídos (histórico)

- [x] **[ID]-[SIGLA]** — [título] | Commit: `abc1234` | Data: YYYY-MM-DD

---

## Como preencher este arquivo

**ID**: prefixo do repo + número sequencial. Ex: `B1`, `APP3`, `WEB2`, `PLT4`.

**SIGLA**: área técnica. Ex: `AUTH`, `INFRA`, `UI`, `API`, `TEST`, `DOCS`.

**Critério de aceitação**: deve ser verificável sem ambiguidade.
- Ruim: "melhorar performance"
- Bom: "endpoint `/auth/login` responde em < 200ms com 100 req/s no DEV"

**Risco residual**: o que pode falhar mesmo após Done.
- Ruim: "pode dar problema"
- Bom: "sessões existentes não são invalidadas — aceitável para esta versão"

**Referência:** DoD completo em `auraxis-platform/.context/23_definition_of_done.md`.
