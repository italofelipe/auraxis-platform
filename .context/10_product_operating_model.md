# Product Operating Model

---

## Como priorizar trabalho

Cada item de backlog é avaliado em quatro dimensões. A soma orienta a prioridade — não é uma fórmula rígida, mas um critério compartilhado para evitar decisões arbitrárias.

| Dimensão | Pergunta | Alta (3) | Média (2) | Baixa (1) |
|:---------|:---------|:---------|:---------|:---------|
| **Valor** | Qual o impacto direto para o usuário ou para o negócio? | Desbloqueia uso core / resolve dor crítica | Melhora experiência existente | Nice-to-have / cosmético |
| **Risco** | Qual o custo de não fazer agora? | Segurança, compliance, dados corrompidos | Regressão silenciosa, dívida acumulando | Baixo impacto se adiado |
| **Custo** | Quanto esforço para implementar? (inverso — maior custo = menor pontuação) | < 1 dia de trabalho focado | 1–3 dias | > 3 dias ou alta incerteza |
| **Dependência** | Outros itens dependem deste? | Bloqueia 2+ outros itens | Bloqueia 1 item | Independente |

**Regra prática:** itens com Risco = Alta sempre sobem ao topo, independente de Valor ou Custo.

### Exemplo de aplicação

| Task | Valor | Risco | Custo | Dep | Total | Decisão |
|:-----|:------|:------|:------|:----|:------|:--------|
| Corrigir XSS em formulário | 2 | 3 | 3 | 1 | 9 | **P0** |
| Dashboard de metas | 3 | 1 | 1 | 2 | 7 | P1 |
| Dark mode | 1 | 1 | 2 | 1 | 5 | P3 |

---

## Cadência de ciclos

- Blocos curtos com entrega fim-a-fim (objetivo claro, critério verificável, risco mapeado).
- Ao final de cada ciclo: atualizar `tasks.md`, registrar handoff, ajustar prioridades.
- Sem "big bang": cada bloco entrega valor ou reduz risco de forma isolada e reversível.

---

## Classificação de trabalho

| Tipo | Definição | Exemplo |
|:-----|:----------|:--------|
| **Estabilização** | Reduz incidentes ativos, falhas de pipeline ou inconsistências de dados | Corrigir migration com downgrade vazio; fix em auth que vaza token |
| **Feature** | Entrega valor direto e mensurável ao usuário | Tela de dashboard; exportação CSV; cadastro de metas |
| **Débito técnico** | Reduz atrito de desenvolvimento, sem mudar comportamento externo | Adoção de Ruff; migração Flask→FastAPI; refatoração de domínio |
| **Refinamento** | Melhora DX, observabilidade, governança ou documentação | Atualizar CLAUDE.md; melhorar mensagens de erro; adicionar log estruturado |

**Ciclo preferencial:** Estabilização → Features → Débito → Refinamento → Features.

Nunca iniciar Features com Estabilização pendente de alta severidade.

---

## Critérios de entrada no backlog

Para um item ser adicionado ao `tasks.md`, precisa ter:

- [ ] **Problema ou oportunidade** descritos em uma frase clara.
- [ ] **Critério de aceitação** verificável sem ambiguidade.
- [ ] **Risco principal** identificado (o que pode dar errado).
- [ ] **Dependências** mapeadas (outros tasks, sistemas externos, decisões humanas).
- [ ] **Classificação** (Estabilização / Feature / Débito / Refinamento).

**Itens sem critério de aceitação claro não entram no backlog** — viram notas em discovery.

---

## Critérios de saída do backlog (= Done)

Ver `23_definition_of_done.md` — documento canônico.

Resumo operacional:
- Status atualizado para `Done` em `tasks.md`.
- Commit(s) referenciados na entrada.
- Risco residual documentado (mesmo que "nenhum").
- Handoff atualizado se a sessão encerrar após este item.

---

## O que vai para discovery, não para backlog

- Ideias sem problema definido ("seria legal ter…").
- Features que dependem de decisão de compliance/regulatório.
- Itens com estimativa de > 2 semanas de trabalho contínuo (quebrar antes de entrar).

Discovery atual: `discovery/discovery_execucao_roadmap.md`.
