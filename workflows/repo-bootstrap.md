# Workflow: Repo Bootstrap

**Gatilho:** Criação de um novo repositório de produto.
**Escopo:** Platform-level.

---

## Pré-condições

- `auraxis-platform` atualizado e com working tree limpo
- Decisão tomada sobre stack do novo repo (Nuxt.js, React Native, etc.)
- Repositório remoto criado no GitHub (se usar submodule mode)

---

## Opção A — Repo local (sem remote ainda)

Use quando o repo ainda não tem remote. Cria estrutura local com git init.

```bash
cd /path/to/auraxis-platform
./scripts/bootstrap-repo.sh <repo-name>
```

Exemplos:
```bash
./scripts/bootstrap-repo.sh auraxis-web
./scripts/bootstrap-repo.sh auraxis-mobile
```

Resultado: `repos/<repo-name>/` com governance baseline e commit inicial.

---

## Opção B — Submodule (com remote existente)

Use quando o remote já existe no GitHub.

```bash
cd /path/to/auraxis-platform
./scripts/bootstrap-repo.sh <repo-name> --submodule <git-url>
```

Exemplo:
```bash
./scripts/bootstrap-repo.sh auraxis-web \
  --submodule git@github.com:italofelipe/auraxis-web.git
```

Resultado: submodule registrado em `.gitmodules` e commitado no platform.

---

## Pós-bootstrap obrigatório

Após criar o repo (opção A ou B), adaptar os templates:

### 1. README.md
Descrever o repo: objetivo, stack, como rodar localmente.

### 2. steering.md
Adaptar para o domínio:
- Quality gates específicos da stack (ESLint, Vitest, etc.)
- Política de branching local
- Convenções de nomenclatura

### 3. tasks.md
Adicionar o primeiro backlog:
- Setup inicial da stack
- Configuração de CI
- Integração com auraxis-api

### 4. AGENTS.md
Adaptar para os agentes que vão atuar neste repo:
- Arquivos de bootstrap específicos
- Quality gates locais
- Fronteiras operacionais

### 5. docs/adr/ADR-001-stack-choice.md
Registrar a decisão de stack (Nuxt.js, React Native, etc.):
- Contexto
- Decisão
- Consequências

---

## Configurar CI mínimo

Todo repo de produto precisa de CI com:
- Lint (ESLint para JS/TS, flake8/ruff para Python)
- Testes automatizados
- Verificação de segurança básica

Para repos JS/TS, criar `.github/workflows/ci.yml`:
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
```

---

## Integrar ao health check

O `scripts/check-health.sh` detecta automaticamente repos em `repos/`.
Adicionar stack-specific checks se necessário editando `check_web()` ou
`check_mobile()` em `scripts/check-health.sh`.

---

## Validação final

```bash
# Verificar que o novo repo aparece no health check
./scripts/check-health.sh <repo-name>

# Verificar submodule (se aplicável)
git submodule status
```

---

## Critério de saída

- [ ] Repo criado com governance baseline (README, AGENTS/CLAUDE, tasks, steering, ADR)
- [ ] `.context/README.md` local presente
- [ ] Primeiro ADR registrado (decisão de stack)
- [ ] tasks.md com backlog inicial
- [ ] CI mínimo planejado ou configurado
- [ ] Health check passando para o novo repo
- [ ] Submodule registrado em platform (se aplicável)
- [ ] `.context/11_repo_map.md` da platform atualizado
