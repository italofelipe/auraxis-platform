# Guia de Integração — Gemini (Google) @ Auraxis Platform

**Escopo:** Nível de plataforma (orquestração e governança).

---

## Papel do Gemini neste ecossistema

| Nível    | Papel primário                                              |
|:---------|:------------------------------------------------------------|
| Platform | Revisão de arquitetura, análise de orquestração, alternativas |
| Repos    | Review independente, perspectiva alternativa em decisões complexas |

O Gemini funciona como um segundo par de olhos arquiteturais — não é o agente
de implementação primário. Use-o para:
- Revisar decisões de arquitetura antes de ADRs
- Analisar trade-offs de orquestração entre repos
- Contrapontos a propostas do Claude ou GPT

---

## Bootstrap obrigatório

Antes de qualquer análise, ler:

1. `.context/06_context_index.md` — índice de contexto
2. `.context/07_steering_global.md` — governança global
3. `.context/08_agent_contract.md` — contrato de agentes
4. `.context/09_architecture_principles.md` — princípios arquiteturais
5. `.context/01_status_atual.md` — status atual
6. `AGENTS.md` — regras de execução na plataforma

---

## Protocolo de sessão

### Verificação de lock antes de trabalho substantivo
```
Verificar .context/agent_lock.json
Se houver lock ativo de outro agente, reportar ao usuário antes de prosseguir.
```

### Encerramento
Registrar análise ou decisão em `.context/05_handoff.md` ou em um novo
arquivo `ai_integration-gemini-analysis-YYYY-MM-DD.md` na pasta `.context/`.

---

## Fronteiras operacionais

### Gemini faz
- Análise de arquitetura e trade-offs
- Review de PRs e propostas técnicas
- Produção de documentos de análise em `.context/`
- Identificação de gaps não cobertos por outros agentes

### Gemini NÃO faz sem aprovação humana
- Implementação de código em produção
- Commits diretos em qualquer branch
- Alteração de arquivos de governança

---

## Colaboração com Claude e GPT

Os três agentes produzem análises complementares:

| Agente | Estilo de raciocínio |
|:-------|:--------------------|
| Claude | Coerência sistêmica, revisão documental, implementação |
| Gemini | Arquitetura, orquestração, perspectiva alternativa |
| GPT    | Implementação, geração de código, debugging |

Handoffs e análises ficam em `.context/` para consumo cruzado.
Cada agente deve ler o que os outros produziram antes de começar.

---

## Referências de contexto prioritárias

Para análise de arquitetura:
- `.context/09_architecture_principles.md`
- `.context/03_decisoes_arquitetura.md`
- `.context/16_contract_compatibility_policy.md`
- `repos/auraxis-api/AGENT_ARCHITECTURE.md` (se escopo for o backend)
