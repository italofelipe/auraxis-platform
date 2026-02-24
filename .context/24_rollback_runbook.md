# Rollback Runbook

Procedimentos de rollback para os cenários mais comuns.
Referenciado por `13_release_governance.md`.

---

## Princípio geral

Todo commit deve ser reversível de forma isolada. Se um rollback exigir reverter múltiplos commits, é sinal de que os commits foram grandes demais — prevenir na próxima entrega.

**Regra de ouro:** em caso de incidente, **reverter primeiro, investigar depois**.

---

## Cenário 1 — Reverter um commit específico (sem afetar commits posteriores)

```bash
# Cria um novo commit que desfaz o commit alvo
git revert <commit-sha>

# Para múltiplos commits em sequência (do mais recente ao mais antigo)
git revert <sha-mais-recente>..<sha-mais-antigo>

# Push para aplicar em produção (requer PR em repos com branch protection)
git push origin main
```

**Quando usar:** bug introduzido em commit isolado, outros commits posteriores são válidos.

---

## Cenário 2 — Reverter deploy para versão anterior (via tag)

```bash
# Ver tags disponíveis
git tag --sort=-version:refname | head -10

# Criar branch de hotfix na tag estável anterior
git checkout -b hotfix/rollback-to-<versao> <tag-estavel>

# Aplicar via PR ou deploy direto (conforme pipeline)
```

**Quando usar:** release inteira com problema, rollback para última versão estável conhecida.

---

## Cenário 3 — Rollback de deploy em CI/CD (AWS / GitHub Actions)

### Se o deploy falhou no meio
O pipeline de CI já tem proteção por gate (build + testes + security). Se o pipeline falhou, o deploy anterior ainda está ativo — não há o que reverter no ambiente.

Ação: corrigir a causa raiz e fazer novo push.

### Se o deploy foi concluído mas gerou incidente
```bash
# 1. Identificar o SHA do deploy anterior estável
# (disponível nos logs do GitHub Actions ou AWS CodeDeploy)

# 2. Em auraxis-api: forçar deploy do SHA anterior via workflow manual
# GitHub Actions > workflow_dispatch com input sha=<sha-anterior>

# 3. Validar smoke test em DEV antes de aplicar em PROD
```

**Referência:** `repos/auraxis-api/docs/RUNBOOK.md` para procedimentos específicos do backend.

---

## Cenário 4 — Rollback de migração de banco de dados (Alembic)

```bash
# Ver histórico de migrações
alembic history

# Reverter para revisão específica
alembic downgrade <revision-id>

# Reverter uma revisão atrás do atual
alembic downgrade -1

# Reverter ao estado base (cuidado: destrói schema)
# alembic downgrade base  # USAR APENAS EM DEV
```

**Regras obrigatórias:**
- Toda migration nova DEVE ter `downgrade()` implementada (não `pass`).
- Testar `downgrade` em DEV antes de subir para PROD.
- Nunca rodar `downgrade` em PROD sem backup do banco.

---

## Cenário 5 — Rollback de submodule em auraxis-platform

```bash
# Ver histórico do pointer do submodule
git log --oneline -- repos/auraxis-api

# Reverter o pointer para commit anterior
git revert <commit-que-avancou-o-pointer>

# Ou manualmente: checkout do SHA antigo no submodule
cd repos/auraxis-api
git checkout <sha-estavel>
cd ..
git add repos/auraxis-api
git commit -m "chore(submodule): rollback auraxis-api pointer to <sha-estavel>"
```

---

## Após qualquer rollback — obrigatório

1. **Registrar incidente** no backlog técnico (`tasks.md` do repo afetado, status `[ ]` com label `INC`).
2. **Documentar** causa raiz, sintoma observado e ação tomada.
3. **Ação preventiva**: criar task para evitar recorrência (melhoria de teste, gate adicional, etc.).
4. **Atualizar** `01_status_atual.md` com o evento.

```markdown
# Exemplo de entrada de incidente em tasks.md:
- [ ] **INC-001** `fix` — [título do problema]
  - Causa raiz: [o que causou]
  - Sintoma: [o que foi observado em produção]
  - Rollback aplicado: `git revert abc1234`
  - Ação preventiva: [o que vai ser feito para não repetir]
```

---

## Referências

- `13_release_governance.md` — fluxo de release e gates
- `23_definition_of_done.md` — DoD que deveria ter prevenido o incidente
- `repos/auraxis-api/docs/RUNBOOK.md` — runbook operacional do backend
