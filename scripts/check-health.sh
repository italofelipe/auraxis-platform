#!/usr/bin/env bash
# scripts/check-health.sh
# Diagnoses the health of the Auraxis platform and all product repos.
# Run this before starting any agent session to detect inconsistent state.
#
# Usage:
#   ./scripts/check-health.sh              # check platform + all repos
#   ./scripts/check-health.sh auraxis-api  # check only one repo
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more warnings or failures detected

set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS_DIR="$PLATFORM_ROOT/repos"
CONTEXT_DIR="$PLATFORM_ROOT/.context"
LOCK_FILE="$CONTEXT_DIR/agent_lock.json"

TARGET_REPO="${1:-}"

PASS=0
WARN=1
FAIL=2

overall=0

# ── Helpers ────────────────────────────────────────────────────────────────────

ok() {
  echo "  ✅  $*"
  return 0
}

warn() {
  echo "  ⚠️   $*"
  if [[ $overall -lt $WARN ]]; then
    overall=$WARN
  fi
  return 0
}

fail() {
  echo "  ❌  $*"
  if [[ $overall -lt $FAIL ]]; then
    overall=$FAIL
  fi
  return 0
}
section() { echo ""; echo "── $* ──────────────────────────────────────────"; }

# ── Platform checks ────────────────────────────────────────────────────────────

check_platform() {
  section "Platform root"

  # Mandatory files
  for f in README.md CLAUDE.md AGENTS.md .context/07_steering_global.md \
            .context/08_agent_contract.md .context/01_status_atual.md \
            .context/02_backlog_next.md; do
    if [[ -f "$PLATFORM_ROOT/$f" ]]; then
      ok "$f present"
    else
      fail "Missing: $f"
    fi
  done

  # Git status of platform
  cd "$PLATFORM_ROOT"
  UNCOMMITTED=$(git status --porcelain | grep -v "^??" || true)
  if [[ -z "$UNCOMMITTED" ]]; then
    ok "Platform git: clean working tree"
  else
    warn "Platform git: uncommitted changes"
    echo "$UNCOMMITTED" | sed 's/^/       /'
  fi

  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$BRANCH" == "master" ]]; then
    ok "Platform branch: master"
  else
    warn "Platform branch: $BRANCH (not master)"
  fi

  # Nested repository in repos/ is an operational hazard for submodules.
  if [[ -d "$REPOS_DIR/.git" ]]; then
    warn "Nested git repo detected at repos/.git (remove to avoid submodule conflicts)"
  fi
}

# ── Agent lock check ───────────────────────────────────────────────────────────

check_agent_lock() {
  section "Agent lock"

  if [[ ! -f "$LOCK_FILE" ]]; then
    ok "No active agent lock"
    return
  fi

  # Parse lock (basic — avoids jq dependency)
  AGENT=$(python3 -c "import json,sys; d=json.load(open('$LOCK_FILE')); print(d.get('agent','?'))" 2>/dev/null || echo "unknown")
  SINCE=$(python3 -c "import json,sys; d=json.load(open('$LOCK_FILE')); print(d.get('since','?'))" 2>/dev/null || echo "unknown")
  REPO=$(python3 -c  "import json,sys; d=json.load(open('$LOCK_FILE')); print(d.get('repo','?'))"  2>/dev/null || echo "unknown")

  warn "Agent lock held by: $AGENT (since $SINCE, repo: $REPO)"
  echo "       If stale, run: scripts/agent-lock.sh release"
}

# ── Repo checks ────────────────────────────────────────────────────────────────

check_repo() {
  local repo_name="$1"
  local repo_path="$REPOS_DIR/$repo_name"

  section "Repo: $repo_name"

  if [[ ! -d "$repo_path" ]]; then
    fail "$repo_name not found at $repo_path"
    return
  fi

  # Mandatory governance files
  # AGENTS.md and CLAUDE.md are interchangeable (repo may use either convention)
  for f in README.md tasks.md steering.md; do
    if [[ -f "$repo_path/$f" ]]; then
      ok "$f present"
    else
      warn "Missing: $f"
    fi
  done
  if [[ -f "$repo_path/AGENTS.md" ]] || [[ -f "$repo_path/CLAUDE.md" ]]; then
    ok "Agent directive present (AGENTS.md or CLAUDE.md)"
  else
    warn "Missing agent directive: create AGENTS.md or CLAUDE.md"
  fi

  # Git status — submodules have a .git file (not dir) pointing to .git/modules/
  if [[ -d "$repo_path/.git" ]] || [[ -f "$repo_path/.git" ]]; then
    cd "$repo_path"
    UNCOMMITTED=$(git status --porcelain | grep -v "^??" || true)
    if [[ -z "$UNCOMMITTED" ]]; then
      ok "Git: clean working tree"
    else
      warn "Git: uncommitted changes"
      echo "$UNCOMMITTED" | sed 's/^/       /'
    fi

    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    ok "Branch: $BRANCH"

    REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ -z "$REMOTE" ]]; then
      warn "No remote configured"
    else
      ok "Remote: $REMOTE"
    fi
  else
    fail "No .git found — not a git repo"
  fi

  # Stack-specific checks
  case "$repo_name" in
    auraxis-api)
      check_backend "$repo_path"
      ;;
    auraxis-web)
      check_web "$repo_path"
      ;;
    auraxis-app)
      check_mobile "$repo_path"
      ;;
  esac
}

check_backend() {
  local path="$1"
  section "Backend health (auraxis-api)"

  # Python
  if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    ok "Python: $PY_VERSION"
  else
    fail "python3 not found"
  fi

  # Virtual env
  if [[ -d "$path/.venv" ]] || [[ -d "$path/venv" ]]; then
    ok "Virtual env present"
  else
    warn "No virtual env found (.venv or venv)"
  fi

  # Pre-commit
  if [[ -f "$path/.pre-commit-config.yaml" ]]; then
    ok ".pre-commit-config.yaml present"
  else
    warn "Missing .pre-commit-config.yaml"
  fi

  # CLAUDE.md
  if [[ -f "$path/CLAUDE.md" ]]; then
    ok "CLAUDE.md present"
  else
    warn "Missing CLAUDE.md"
  fi

  # ai_squad
  if [[ -d "$path/ai_squad" ]]; then
    ok "ai_squad/ present"
    if [[ -f "$path/ai_squad/main.py" ]]; then
      ok "ai_squad/main.py present"
    else
      warn "ai_squad/main.py missing"
    fi
  else
    warn "ai_squad/ not found"
  fi
}

check_web() {
  local path="$1"
  section "Web health (auraxis-web)"
  if [[ -f "$path/package.json" ]]; then
    ok "package.json present"
    if command -v node &>/dev/null; then
      ok "Node: $(node --version)"
    else
      warn "node not found in PATH"
    fi
    if [[ -f "$path/nuxt.config.ts" ]] || [[ -f "$path/nuxt.config.js" ]]; then
      ok "nuxt.config present"
    else
      warn "nuxt.config not found (Nuxt not initialized yet)"
    fi
  else
    warn "package.json not found (Nuxt not initialized yet — bootstrap pending)"
  fi
}

check_mobile() {
  local path="$1"
  section "Mobile health (auraxis-app)"
  if [[ -f "$path/package.json" ]]; then
    ok "package.json present"
    if command -v node &>/dev/null; then
      ok "Node: $(node --version)"
    else
      warn "node not found in PATH"
    fi
    if [[ -f "$path/app.json" ]]; then
      ok "app.json present (Expo config)"
    else
      warn "app.json not found"
    fi
    if [[ -f "$path/tsconfig.json" ]]; then
      ok "tsconfig.json present"
    else
      warn "tsconfig.json not found"
    fi
  else
    warn "package.json not found (Expo not initialized yet)"
  fi
}

# ── Submodule check ────────────────────────────────────────────────────────────

check_submodules() {
  section "Git submodules"
  cd "$PLATFORM_ROOT"

  if [[ -f ".gitmodules" ]]; then
    SUBMODULE_COUNT=$(grep -c "\[submodule" .gitmodules 2>/dev/null || echo 0)
    ok ".gitmodules present ($SUBMODULE_COUNT submodule(s) registered)"
    git submodule status 2>/dev/null | sed 's/^/       /'
  else
    warn ".gitmodules not found — repos are local directories, not submodules"
    echo "       See README.md > Bootstrap for instructions on adding submodules."
  fi
}

# ── Main ───────────────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Auraxis Platform — Health Check"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════"

check_platform
check_agent_lock
check_submodules

if [[ -n "$TARGET_REPO" ]]; then
  check_repo "$TARGET_REPO"
else
  # Check all repos that exist
  for repo_dir in "$REPOS_DIR"/*/; do
    [[ -d "$repo_dir" ]] && check_repo "$(basename "$repo_dir")"
  done
fi

echo ""
echo "════════════════════════════════════════════════════════"
if [[ $overall -eq $PASS ]]; then
  echo "  ✅  All checks passed — safe to proceed"
elif [[ $overall -eq $WARN ]]; then
  echo "  ⚠️   Warnings detected — review before proceeding"
else
  echo "  ❌  Failures detected — resolve before proceeding"
fi
echo "════════════════════════════════════════════════════════"
echo ""

exit $overall
