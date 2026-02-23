#!/usr/bin/env bash
# verify-agent-session.sh — Verificação de prereqs antes de qualquer sessão de agente
# Uso: ./scripts/verify-agent-session.sh [--quiet]
# Exit code: 0 = tudo OK, 1 = falhas críticas

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QUIET="${1:-}"
FAILURES=0
WARNINGS=0

# --- Helpers ---
ok()   { [[ "$QUIET" != "--quiet" ]] && echo "  ✅ $*"; }
warn() { [[ "$QUIET" != "--quiet" ]] && echo "  ⚠️  $*"; WARNINGS=$((WARNINGS + 1)); }
fail() { echo "  ❌ $*"; FAILURES=$((FAILURES + 1)); }
section() { [[ "$QUIET" != "--quiet" ]] && echo ""; echo "── $* ──────────────────────────────────"; }

# --- Main ---
[[ "$QUIET" != "--quiet" ]] && echo "🔍 Verificando prereqs para sessão de agente..."
[[ "$QUIET" != "--quiet" ]] && echo "   Platform root: $PLATFORM_ROOT"

# 1. Git
section "Git"
if command -v git &>/dev/null; then
  GIT_VERSION=$(git --version | awk '{print $3}')
  ok "git $GIT_VERSION"
else
  fail "git não encontrado. Instalar antes de continuar."
fi

# Verifica identity via config explícita ou via inferência do sistema
GIT_NAME=$(git config --get user.name 2>/dev/null || git log --format="%an" -1 2>/dev/null || echo "")
GIT_EMAIL=$(git config --get user.email 2>/dev/null || git log --format="%ae" -1 2>/dev/null || echo "")
if [[ -n "$GIT_NAME" && -n "$GIT_EMAIL" ]]; then
  ok "git identity: $GIT_NAME <$GIT_EMAIL>"
else
  fail "git user.name ou user.email não configurados. Rodar: git config --global user.name 'Nome' && git config --global user.email 'email@x.com'"
fi

# 2. SSH
section "SSH"
if command -v ssh-add &>/dev/null; then
  if ssh-add -l &>/dev/null 2>&1; then
    KEY_COUNT=$(ssh-add -l 2>/dev/null | wc -l | tr -d ' ')
    ok "SSH agent ativo com $KEY_COUNT chave(s)"
  else
    warn "SSH agent sem chaves carregadas. Submodules com SSH URL podem falhar. Rodar: ssh-add ~/.ssh/id_ed25519 (ou equivalente)"
  fi
else
  warn "ssh-add não encontrado. Operações SSH podem falhar."
fi

# 3. Python 3
section "Python"
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
  ok "python3 $PY_VERSION"
else
  fail "python3 não encontrado. Necessário para agent-lock.sh e scripts de plataforma."
fi

# Verificar módulo json (usado pelo agent-lock.sh)
if python3 -c "import json, sys" &>/dev/null; then
  ok "python3 json module disponível"
else
  fail "python3 sem módulo json (inesperado — verificar instalação)"
fi

# 4. Scripts de plataforma
section "Scripts de plataforma"
for script in agent-lock.sh check-health.sh setup-submodules.sh; do
  SCRIPT_PATH="$PLATFORM_ROOT/scripts/$script"
  if [[ -f "$SCRIPT_PATH" ]]; then
    if [[ -x "$SCRIPT_PATH" ]]; then
      ok "$script (executável)"
    else
      fail "$script existe mas não é executável. Rodar: chmod +x scripts/$script"
    fi
  else
    fail "$script não encontrado em scripts/"
  fi
done

# 5. Submodules
section "Submodules"
cd "$PLATFORM_ROOT"
if [[ -f ".gitmodules" ]]; then
  EXPECTED_REPOS=("auraxis-api" "auraxis-app" "auraxis-web")
  for repo in "${EXPECTED_REPOS[@]}"; do
    REPO_PATH="repos/$repo"
    if [[ -d "$REPO_PATH" ]]; then
      # Verificar se é submodule inicializado (tem .git file ou dir)
      if [[ -f "$REPO_PATH/.git" ]] || [[ -d "$REPO_PATH/.git" ]]; then
        # Verificar se o submodule tem commits (não está vazio)
        if git -C "$REPO_PATH" rev-parse HEAD &>/dev/null; then
          BRANCH=$(git -C "$REPO_PATH" branch --show-current 2>/dev/null || echo "detached")
          ok "$repo ($BRANCH)"
        else
          warn "$repo: sem commits — pode estar em bootstrap"
        fi
      else
        fail "$repo: diretório existe mas não é submodule inicializado. Rodar: git submodule update --init repos/$repo"
      fi
    else
      fail "$repo: diretório não encontrado. Rodar: git submodule update --init --recursive"
    fi
  done
else
  fail ".gitmodules não encontrado — não é um repositório da platform corretamente configurado."
fi

# 6. Arquivos de contexto obrigatórios
section "Contexto (.context/)"
REQUIRED_CONTEXT=(
  ".context/06_context_index.md"
  ".context/07_steering_global.md"
  ".context/08_agent_contract.md"
  ".context/01_status_atual.md"
  ".context/02_backlog_next.md"
  ".context/23_definition_of_done.md"
)
for ctx_file in "${REQUIRED_CONTEXT[@]}"; do
  if [[ -f "$PLATFORM_ROOT/$ctx_file" ]]; then
    ok "$ctx_file"
  else
    fail "$ctx_file não encontrado — contexto de governança incompleto"
  fi
done

# 7. Agent lock
section "Agent Lock"
LOCK_FILE="$PLATFORM_ROOT/.context/agent_lock.json"
LOCK_SCHEMA="$PLATFORM_ROOT/.context/agent_lock.schema.json"

if [[ -f "$LOCK_SCHEMA" ]]; then
  ok "agent_lock.schema.json presente"
else
  warn "agent_lock.schema.json não encontrado — schema de lock não verificável"
fi

if [[ -f "$LOCK_FILE" ]]; then
  # Lock existe — verificar se é válido e não expirado
  LOCK_AGENT=$(python3 -c "import json; d=json.load(open('$LOCK_FILE')); print(d.get('agent','?'))" 2>/dev/null || echo "?")
  LOCK_TASK=$(python3 -c "import json; d=json.load(open('$LOCK_FILE')); print(d.get('task','?'))" 2>/dev/null || echo "?")
  warn "Agent lock ATIVO: agente='$LOCK_AGENT', task='$LOCK_TASK'. Se for seu lock, prossiga. Se for de outro agente, coordene antes de continuar."
else
  ok "Agent lock livre — pode adquirir com: ./scripts/agent-lock.sh acquire <agente> <repo> '<tarefa>'"
fi

# 8. CLAUDE.md nos repos de produto
section "CLAUDE.md por repo"
for repo in auraxis-api auraxis-app auraxis-web; do
  CLAUDE_PATH="$PLATFORM_ROOT/repos/$repo/CLAUDE.md"
  if [[ -f "$CLAUDE_PATH" ]]; then
    ok "$repo/CLAUDE.md"
  else
    fail "$repo/CLAUDE.md não encontrado — agente não terá diretiva de identidade para este repo"
  fi
done

# 9. .context/ local nos repos (avisos — não bloqueia)
section ".context/ local por repo"
for repo in auraxis-api auraxis-app auraxis-web; do
  CTX_PATH="$PLATFORM_ROOT/repos/$repo/.context"
  if [[ -d "$CTX_PATH" ]]; then
    CTX_FILES=$(ls "$CTX_PATH" 2>/dev/null | wc -l | tr -d ' ')
    ok "$repo/.context/ ($CTX_FILES arquivo(s))"
  else
    warn "$repo/.context/ não existe — agente usará apenas contexto da platform"
  fi
done

# --- Resultado ---
echo ""
echo "══════════════════════════════════════════════════"
if [[ $FAILURES -eq 0 && $WARNINGS -eq 0 ]]; then
  echo "✅ Tudo OK — sessão de agente pode iniciar."
elif [[ $FAILURES -eq 0 ]]; then
  echo "⚠️  $WARNINGS warning(s) — sessão pode iniciar com consciência dos avisos."
else
  echo "❌ $FAILURES falha(s) crítica(s) e $WARNINGS aviso(s). Resolver falhas antes de iniciar sessão."
fi
echo "══════════════════════════════════════════════════"

exit $FAILURES
