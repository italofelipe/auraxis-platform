#!/usr/bin/env bash
set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQUAD_DIR="${PLATFORM_ROOT}/ai_squad"
API_DIR="${PLATFORM_ROOT}/repos/auraxis-api"
WEB_DIR="${PLATFORM_ROOT}/repos/auraxis-web"
APP_DIR="${PLATFORM_ROOT}/repos/auraxis-app"

NODE_MAJOR_REQUIRED="${AURAXIS_NODE_MAJOR_REQUIRED:-25}"
AUTO_USE_NVM="${AURAXIS_AUTO_USE_NVM:-true}"
WEB_FROZEN_LOCKFILE="${AURAXIS_WEB_FROZEN_LOCKFILE:-false}"
APP_USE_CI_INSTALL="${AURAXIS_APP_USE_CI_INSTALL:-false}"

log() {
  echo "[runtime-setup] $*"
}

fail() {
  echo "[runtime-setup] ERROR: $*" >&2
  exit 1
}

ensure_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || fail "directory not found: $dir"
}

resolve_node_major() {
  local version
  version="$(node -v 2>/dev/null || true)"
  if [[ -z "$version" ]]; then
    echo ""
    return
  fi
  version="${version#v}"
  echo "${version%%.*}"
}

source_nvm() {
  if [[ -n "${NVM_DIR:-}" && -s "${NVM_DIR}/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NVM_DIR}/nvm.sh"
    return 0
  fi

  if [[ -s "${HOME}/.nvm/nvm.sh" ]]; then
    export NVM_DIR="${HOME}/.nvm"
    # shellcheck source=/dev/null
    source "${NVM_DIR}/nvm.sh"
    return 0
  fi

  if [[ -s "/opt/homebrew/opt/nvm/nvm.sh" ]]; then
    export NVM_DIR="${HOME}/.nvm"
    # shellcheck source=/dev/null
    source "/opt/homebrew/opt/nvm/nvm.sh"
    return 0
  fi

  return 1
}

ensure_node_runtime() {
  local current_major
  current_major="$(resolve_node_major)"
  if [[ "$current_major" == "$NODE_MAJOR_REQUIRED" ]]; then
    log "Node runtime OK (major ${NODE_MAJOR_REQUIRED})."
    return
  fi

  if [[ "$AUTO_USE_NVM" != "true" ]]; then
    fail "expected Node ${NODE_MAJOR_REQUIRED}.x, found $(node -v 2>/dev/null || echo 'none')."
  fi

  source_nvm || fail "nvm not found. Install nvm or set AUTO_USE_NVM=false and configure Node ${NODE_MAJOR_REQUIRED}.x manually."

  log "Switching Node runtime via nvm -> ${NODE_MAJOR_REQUIRED}.x ..."
  nvm install "${NODE_MAJOR_REQUIRED}" >/dev/null
  nvm use "${NODE_MAJOR_REQUIRED}" >/dev/null

  current_major="$(resolve_node_major)"
  if [[ "$current_major" != "$NODE_MAJOR_REQUIRED" ]]; then
    fail "failed to activate Node ${NODE_MAJOR_REQUIRED}.x (current: $(node -v 2>/dev/null || echo 'none'))."
  fi

  log "Node runtime active: $(node -v)."
}

ensure_python_venv() {
  local target_dir="$1"
  local requirements_file="$2"
  local requirements_dev_file="${3:-}"

  if [[ ! -d "${target_dir}/.venv" ]]; then
    log "Creating virtualenv in ${target_dir}/.venv ..."
    (cd "$target_dir" && python3 -m venv .venv)
  fi

  log "Installing Python dependencies in ${target_dir} ..."
  (
    cd "$target_dir"
    # shellcheck source=/dev/null
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r "$requirements_file"
    if [[ -n "$requirements_dev_file" && -f "$requirements_dev_file" ]]; then
      python -m pip install -r "$requirements_dev_file"
    fi
  )
}

ensure_pnpm() {
  if command -v pnpm >/dev/null 2>&1; then
    return
  fi
  if ! command -v corepack >/dev/null 2>&1; then
    fail "pnpm not found and corepack unavailable."
  fi
  log "Enabling pnpm via corepack ..."
  corepack enable >/dev/null
}

resolve_web_pnpm_version() {
  if ! command -v node >/dev/null 2>&1; then
    echo "pnpm@10.30.1"
    return
  fi
  node -p "require('${WEB_DIR}/package.json').packageManager || 'pnpm@10.30.1'" 2>/dev/null || echo "pnpm@10.30.1"
}

install_web_dependencies() {
  ensure_pnpm
  local pnpm_version
  pnpm_version="$(resolve_web_pnpm_version)"
  if command -v corepack >/dev/null 2>&1; then
    corepack prepare "${pnpm_version}" --activate >/dev/null
  fi
  log "Installing web dependencies (${pnpm_version}) ..."
  if [[ "$WEB_FROZEN_LOCKFILE" == "true" ]]; then
    (cd "$WEB_DIR" && pnpm install --frozen-lockfile)
  else
    (cd "$WEB_DIR" && pnpm install)
  fi
}

install_app_dependencies() {
  log "Installing app dependencies ..."
  if [[ "$APP_USE_CI_INSTALL" == "true" ]]; then
    (cd "$APP_DIR" && npm ci)
  else
    (cd "$APP_DIR" && npm install)
  fi
}

main() {
  ensure_dir "$PLATFORM_ROOT"
  ensure_dir "$SQUAD_DIR"
  ensure_dir "$API_DIR"
  ensure_dir "$WEB_DIR"
  ensure_dir "$APP_DIR"

  log "Platform root: ${PLATFORM_ROOT}"
  ensure_node_runtime

  ensure_python_venv "$SQUAD_DIR" "requirements.txt"
  ensure_python_venv "$API_DIR" "requirements.txt" "requirements-dev.txt"
  install_web_dependencies
  install_app_dependencies

  log "Runtime setup completed."
  log "Node: $(node -v)"
  log "Python: $(python3 --version)"
}

main "$@"
