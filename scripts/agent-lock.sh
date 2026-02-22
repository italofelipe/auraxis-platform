#!/usr/bin/env bash
# scripts/agent-lock.sh
# Mutex protocol for multi-agent coordination in Auraxis Platform.
# Prevents two AI agents from operating on the same repo simultaneously.
#
# Usage:
#   ./scripts/agent-lock.sh acquire <agent> <repo> "<task>"
#   ./scripts/agent-lock.sh release [agent]
#   ./scripts/agent-lock.sh status
#
# Arguments:
#   agent  — one of: claude, gemini, gpt, crewai, human
#   repo   — e.g. auraxis-api, auraxis-web, platform
#   task   — short description of the current task (quoted)
#
# Examples:
#   ./scripts/agent-lock.sh acquire claude auraxis-api "Implement PLT1.2 governance scripts"
#   ./scripts/agent-lock.sh status
#   ./scripts/agent-lock.sh release claude
#   ./scripts/agent-lock.sh release        # force-release regardless of owner

set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK_FILE="$PLATFORM_ROOT/.context/agent_lock.json"
VALID_AGENTS="claude gemini gpt crewai human"

# ── Helpers ────────────────────────────────────────────────────────────────────

die()  { echo "❌  $*" >&2; exit 1; }
ok()   { echo "✅  $*"; }
info() { echo "ℹ️   $*"; }
warn() { echo "⚠️   $*"; }

is_valid_agent() {
  local agent="$1"
  for a in $VALID_AGENTS; do [[ "$a" == "$agent" ]] && return 0; done
  return 1
}

read_lock_field() {
  local field="$1"
  python3 -c "import json; d=json.load(open('$LOCK_FILE')); print(d.get('$field',''))" 2>/dev/null || echo ""
}

# ── Commands ───────────────────────────────────────────────────────────────────

cmd_acquire() {
  local agent="${1:-}"
  local repo="${2:-}"
  local task="${3:-}"

  [[ -z "$agent" ]] && die "Usage: acquire <agent> <repo> \"<task>\""
  [[ -z "$repo"  ]] && die "Usage: acquire <agent> <repo> \"<task>\""
  [[ -z "$task"  ]] && die "Usage: acquire <agent> <repo> \"<task>\""

  is_valid_agent "$agent" || die "Unknown agent '$agent'. Valid: $VALID_AGENTS"

  if [[ -f "$LOCK_FILE" ]]; then
    CURRENT_AGENT=$(read_lock_field "agent")
    CURRENT_REPO=$(read_lock_field "repo")
    CURRENT_SINCE=$(read_lock_field "since")
    CURRENT_TASK=$(read_lock_field "task")

    if [[ "$CURRENT_AGENT" == "$agent" ]]; then
      warn "Lock already held by you ($agent). Updating task..."
    else
      echo ""
      die "Lock is held by '$CURRENT_AGENT' on '$CURRENT_REPO' since $CURRENT_SINCE.
    Task: $CURRENT_TASK
    Wait for the lock to be released or run:
      scripts/agent-lock.sh release"
    fi
  fi

  BRANCH=$(git -C "$PLATFORM_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  PID=$$

  python3 - <<EOF
import json
lock = {
    "agent": "$agent",
    "repo":  "$repo",
    "since": "$NOW",
    "task":  "$task",
    "pid":   $PID,
    "branch": "$BRANCH"
}
with open("$LOCK_FILE", "w") as f:
    json.dump(lock, f, indent=2)
print(json.dumps(lock, indent=2))
EOF

  echo ""
  ok "Lock acquired by $agent on $repo"
  info "Task: $task"
  info "Lock file: $LOCK_FILE"
  echo ""
  echo "  Remember to release when done:"
  echo "    scripts/agent-lock.sh release $agent"
  echo ""
}

cmd_release() {
  local agent="${1:-}"

  if [[ ! -f "$LOCK_FILE" ]]; then
    info "No lock file found — nothing to release."
    return
  fi

  CURRENT_AGENT=$(read_lock_field "agent")

  if [[ -n "$agent" ]] && [[ "$CURRENT_AGENT" != "$agent" ]]; then
    warn "Lock is held by '$CURRENT_AGENT', not '$agent'."
    echo "  Use: scripts/agent-lock.sh release  (no arg = force release)"
    exit 1
  fi

  SINCE=$(read_lock_field "since")
  rm "$LOCK_FILE"

  ok "Lock released (was held by $CURRENT_AGENT since $SINCE)"
}

cmd_status() {
  if [[ ! -f "$LOCK_FILE" ]]; then
    ok "No active lock — platform is free"
    return
  fi

  AGENT=$(read_lock_field "agent")
  REPO=$(read_lock_field "repo")
  SINCE=$(read_lock_field "since")
  TASK=$(read_lock_field "task")
  BRANCH=$(read_lock_field "branch")

  echo ""
  echo "  Lock status:"
  echo "  ┌──────────────────────────────────────────"
  echo "  │  Agent:   $AGENT"
  echo "  │  Repo:    $REPO"
  echo "  │  Branch:  $BRANCH"
  echo "  │  Since:   $SINCE"
  echo "  │  Task:    $TASK"
  echo "  └──────────────────────────────────────────"
  echo ""
}

# ── Main ───────────────────────────────────────────────────────────────────────

CMD="${1:-status}"

case "$CMD" in
  acquire) shift; cmd_acquire "$@" ;;
  release) shift; cmd_release "$@" ;;
  status)  cmd_status ;;
  *)
    echo "Usage: $0 <acquire|release|status> [args...]"
    echo ""
    echo "  acquire <agent> <repo> \"<task>\"  — acquire lock"
    echo "  release [agent]                  — release lock"
    echo "  status                           — show current lock"
    exit 1
    ;;
esac
