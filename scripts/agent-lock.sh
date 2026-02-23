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
LOCK_TTL_SECONDS="${AGENT_LOCK_TTL_SECONDS:-14400}" # 4h default

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

iso_to_epoch() {
  local iso="$1"
  python3 - "$iso" <<'PY'
from datetime import datetime
import sys
raw = sys.argv[1]
try:
    dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    print(int(dt.timestamp()))
except Exception:
    print('')
PY
}

compute_expires_at() {
  local since_iso="$1"
  local ttl_seconds="$2"
  python3 - "$since_iso" "$ttl_seconds" <<'PY'
from datetime import datetime, timedelta, timezone
import sys
since_raw = sys.argv[1]
ttl = int(sys.argv[2])
try:
    since_dt = datetime.fromisoformat(since_raw.replace('Z', '+00:00'))
except Exception:
    since_dt = datetime.now(timezone.utc)
expires = since_dt + timedelta(seconds=ttl)
print(expires.strftime('%Y-%m-%dT%H:%M:%SZ'))
PY
}

lock_age_seconds() {
  [[ ! -f "$LOCK_FILE" ]] && { echo "-1"; return; }

  local since_iso
  local since_epoch
  local now_epoch
  since_iso="$(read_lock_field "since")"
  since_epoch="$(iso_to_epoch "$since_iso")"
  now_epoch="$(date -u '+%s')"

  if [[ -z "$since_epoch" ]]; then
    echo "-1"
    return
  fi

  echo "$(( now_epoch - since_epoch ))"
}

is_lock_expired() {
  [[ ! -f "$LOCK_FILE" ]] && return 1

  local now_epoch
  local expires_iso
  local expires_epoch
  local since_iso
  local since_epoch

  now_epoch="$(date -u '+%s')"
  expires_iso="$(read_lock_field "expires_at")"

  if [[ -n "$expires_iso" ]]; then
    expires_epoch="$(iso_to_epoch "$expires_iso")"
  else
    # Backward compatibility for older lock files without expires_at.
    since_iso="$(read_lock_field "since")"
    since_epoch="$(iso_to_epoch "$since_iso")"
    if [[ -z "$since_epoch" ]]; then
      return 1
    fi
    expires_epoch="$(( since_epoch + LOCK_TTL_SECONDS ))"
  fi

  if [[ -z "$expires_epoch" ]]; then
    return 1
  fi

  [[ "$now_epoch" -ge "$expires_epoch" ]]
}

purge_expired_lock_if_needed() {
  [[ ! -f "$LOCK_FILE" ]] && return 1

  if is_lock_expired; then
    local expired_agent
    local expired_repo
    local expired_since
    local expired_task
    expired_agent="$(read_lock_field "agent")"
    expired_repo="$(read_lock_field "repo")"
    expired_since="$(read_lock_field "since")"
    expired_task="$(read_lock_field "task")"

    warn "Expired lock detected for '$expired_agent' on '$expired_repo' (since $expired_since)."
    warn "Task was: $expired_task"
    rm -f "$LOCK_FILE"
    ok "Expired lock auto-released"
    return 0
  fi

  return 1
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
    purge_expired_lock_if_needed >/dev/null || true
  fi

  if [[ -f "$LOCK_FILE" ]]; then
    CURRENT_AGENT=$(read_lock_field "agent")
    CURRENT_REPO=$(read_lock_field "repo")
    CURRENT_SINCE=$(read_lock_field "since")
    CURRENT_TASK=$(read_lock_field "task")
    CURRENT_EXPIRES=$(read_lock_field "expires_at")

    if [[ "$CURRENT_AGENT" == "$agent" ]]; then
      warn "Lock already held by you ($agent). Updating task..."
    else
      echo ""
      die "Lock is held by '$CURRENT_AGENT' on '$CURRENT_REPO' since $CURRENT_SINCE.
    Expires at: $CURRENT_EXPIRES
    Task: $CURRENT_TASK
    Wait for the lock to be released or run:
      scripts/agent-lock.sh release"
    fi
  fi

  BRANCH=$(git -C "$PLATFORM_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  EXPIRES_AT="$(compute_expires_at "$NOW" "$LOCK_TTL_SECONDS")"
  PID=$$

  python3 - <<EOF_PY
import json
lock = {
    "agent": "$agent",
    "repo":  "$repo",
    "since": "$NOW",
    "expires_at": "$EXPIRES_AT",
    "task":  "$task",
    "pid":   $PID,
    "branch": "$BRANCH"
}
with open("$LOCK_FILE", "w") as f:
    json.dump(lock, f, indent=2)
print(json.dumps(lock, indent=2))
EOF_PY

  echo ""
  ok "Lock acquired by $agent on $repo"
  info "Task: $task"
  info "TTL: ${LOCK_TTL_SECONDS}s"
  info "Expires at: $EXPIRES_AT"
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

  if purge_expired_lock_if_needed >/dev/null; then
    ok "No active lock — platform is free"
    return
  fi

  AGENT=$(read_lock_field "agent")
  REPO=$(read_lock_field "repo")
  SINCE=$(read_lock_field "since")
  EXPIRES_AT=$(read_lock_field "expires_at")
  TASK=$(read_lock_field "task")
  BRANCH=$(read_lock_field "branch")

  AGE_SECONDS="$(lock_age_seconds)"
  if [[ "$AGE_SECONDS" =~ ^-?[0-9]+$ ]] && [[ "$AGE_SECONDS" -ge 0 ]]; then
    REMAINING="$(( LOCK_TTL_SECONDS - AGE_SECONDS ))"
  else
    REMAINING="-1"
  fi

  echo ""
  echo "  Lock status:"
  echo "  ┌──────────────────────────────────────────"
  echo "  │  Agent:      $AGENT"
  echo "  │  Repo:       $REPO"
  echo "  │  Branch:     $BRANCH"
  echo "  │  Since:      $SINCE"
  echo "  │  Expires at: $EXPIRES_AT"
  if [[ "$REMAINING" -ge 0 ]]; then
    echo "  │  Remaining:  ${REMAINING}s"
  else
    echo "  │  Remaining:  unknown"
  fi
  echo "  │  Task:       $TASK"
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
