# steering.md — [Nome do Repo]

---

## Objetivo do repositório

[Uma frase clara: o que este repo entrega e para quem.]

Exemplos:
- "Expõe a API REST e GraphQL do Auraxis. Fonte de verdade para regras de negócio e contratos."
- "Aplicação web do Auraxis. Consome contratos da API e entrega UX para usuários finais."

---

## Princípios técnicos

- **[Linguagem] strict**: toda função pública com tipos anotados. Sem `any` implícito.
- **Sem lógica de negócio na borda**: controllers/views apenas orquestram — regras ficam em domínio/serviços.
- **Contratos explícitos**: toda integração externa documentada e versionada.
- **Testes como documentação**: nomes de teste descrevem comportamento, não implementação.
- **Commits reversíveis**: cada commit pode ser revertido sem impacto em outros.

---

## Convenções de código

| Camada | Onde fica | Regra |
|:-------|:----------|:------|
| Domínio/negócio | `[pasta]` | Sem dependência de framework |
| Integração externa | `[pasta]` | Sempre atrás de adapter/interface |
| Testes | `[pasta]` | Unit isolado de IO; integration com mock de borda |
| Configuração | `[pasta]` | Nunca hardcoded; sempre via env ou config object |

---

## Qualidade e gates

```bash
# Lint
[comando de lint]

# Type-check
[comando de type-check]

# Testes
[comando de testes]

# Todos os gates juntos (equivalente ao CI)
[comando combinado ou make target]
```

**Gate bloqueante:** lint + type-check + testes devem passar antes de qualquer PR.
**Referência:** `auraxis-platform/.context/12_quality_security_baseline.md`

---

## Segurança

- Secrets nunca em código — usar variáveis de ambiente.
- Dados sensíveis nunca em logs.
- Dependências auditadas periodicamente (`[ferramenta de audit]`).
- [Adicionar regras específicas do domínio]

---

## Integrações e contratos

| Sistema | Tipo | Direção | Versão |
|:--------|:-----|:--------|:-------|
| [sistema] | REST/GraphQL/Event | consome / expõe | v[N] |

**Política de mudança de contrato:** ver `auraxis-platform/.context/16_contract_compatibility_policy.md`.

---

## Regras de entrega

- Branch no formato `type/scope-descricao`.
- Commits Conventional Commits, granulares e reversíveis.
- `tasks.md` atualizado ao final de cada bloco com status e rastreabilidade.
- Handoff registrado em `auraxis-platform/.context/05_handoff.md` ao encerrar sessão.

**DoD completo:** `auraxis-platform/.context/23_definition_of_done.md`.

---

## Referências globais

- Governança: `auraxis-platform/.context/07_steering_global.md`
- Contrato de agente: `auraxis-platform/.context/08_agent_contract.md`
- Convenções de branch/commit: `auraxis-platform/.context/15_workflow_conventions.md`
