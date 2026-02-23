#!/usr/bin/env bash
# scripts/setup-submodules.sh
#
# One-shot environment setup for any agent or developer cloning auraxis-platform.
# Initializes and updates all git submodules, then verifies the environment.
#
# Usage:
#   ./scripts/setup-submodules.sh           # full setup
#   ./scripts/setup-submodules.sh --check   # only verify, do not init
#
# Intended for:
#   - New agents starting a session in a fresh clone
#   - CI environments bootstrapping the workspace
#   - Developers onboarding to the platform
#
# After running this script, all repos/ directories will be populated
# and the platform health check should pass.

set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$PLATFORM_ROOT/scripts"
MODE="${1:-}"

# ── Helpers ─────────────────────────────────────────────────────────────────

info()    { echo "  →  $*"; }
ok()      { echo "  ✅  $*"; }
warn()    { echo "  ⚠️   $*"; }
fail()    { echo "  ❌  $*"; exit 1; }
section() { echo ""; echo "── $* ──────────────────────────────────────────"; }

# ── Header ──────────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Auraxis Platform — Submodule Setup"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════"

# ── Verify mode ─────────────────────────────────────────────────────────────

if [[ "$MODE" == "--check" ]]; then
  section "Checking submodule state (read-only)"
  cd "$PLATFORM_ROOT"

  if [[ ! -f ".gitmodules" ]]; then
    fail ".gitmodules not found — is this auraxis-platform?"
  fi

  TOTAL=$(grep -c "\[submodule" .gitmodules)
  info "Registered submodules: $TOTAL"

  git submodule status | while read -r sha path _rest; do
    if [[ "$sha" == -* ]]; then
      warn "$path — not initialized (run without --check to init)"
    elif [[ "$sha" == +* ]]; then
      warn "$path — checked out at different commit than recorded"
    else
      ok "$path — OK ($(echo "$sha" | cut -c1-8))"
    fi
  done

  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "  Check complete. Run without --check to initialize."
  echo "════════════════════════════════════════════════════════"
  echo ""
  exit 0
fi

# ── Full setup ───────────────────────────────────────────────────────────────

section "Prerequisites"

# Git
if ! command -v git &>/dev/null; then
  fail "git not found — install git and retry"
fi
ok "git: $(git --version)"

# SSH key (optional but common for submodules)
if ssh-add -l &>/dev/null 2>&1; then
  ok "SSH agent has keys loaded"
else
  warn "SSH agent has no keys — submodule init may fail if repos use SSH URLs"
  warn "Run: ssh-add ~/.ssh/id_ed25519 (or your key path)"
fi

section "Submodule initialization"

cd "$PLATFORM_ROOT"

if [[ ! -f ".gitmodules" ]]; then
  fail ".gitmodules not found — is this auraxis-platform?"
fi

info "Initializing all submodules..."
git submodule update --init --recursive

ok "All submodules initialized"

section "Submodule status"

git submodule status | while read -r sha path _rest; do
  name="$(basename "$path")"
  short_sha="$(echo "$sha" | tr -d '+-' | cut -c1-8)"
  if [[ "$sha" == -* ]]; then
    warn "$name — still not initialized (SSH access issue?)"
  elif [[ "$sha" == +* ]]; then
    warn "$name — at $short_sha (ahead/behind recorded pointer)"
  else
    ok "$name — at $short_sha"
  fi
done

section "Platform health check"

info "Running check-health.sh..."
if bash "$SCRIPT_DIR/check-health.sh"; then
  ok "Health check passed"
else
  warn "Health check reported warnings — review output above"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Setup complete. All repos are ready."
echo ""
echo "  Next steps for agents:"
echo "  1. Read .context/06_context_index.md"
echo "  2. Read .context/07_steering_global.md"
echo "  3. Read .context/08_agent_contract.md"
echo "  4. Read .context/01_status_atual.md"
echo "  5. Acquire agent lock: scripts/agent-lock.sh acquire <name> <repo> '<task>'"
echo "  6. Create a feature branch and start working"
echo "════════════════════════════════════════════════════════"
echo ""
