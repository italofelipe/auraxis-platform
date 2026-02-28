#!/usr/bin/env bash
set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQUAD_DIR="${PLATFORM_ROOT}/ai_squad"
PREP_SCRIPT="${PLATFORM_ROOT}/scripts/prepare-repo-for-agent-run.sh"
FLAG_BOOTSTRAP_SCRIPT="${PLATFORM_ROOT}/scripts/bootstrap-feature-flag-provider.sh"

TARGET_REPO="${1:-all}"
BRIEFING="${2:-Execute a tarefa}"
MODE="${3:-run}"
AUTO_PREP="${AURAXIS_AUTO_PREP_REPOS:-true}"
FLAG_BOOTSTRAP="${AURAXIS_FEATURE_FLAGS_BOOTSTRAP:-true}"
FLAG_BOOTSTRAP_ENV="${AURAXIS_FEATURE_FLAGS_ENV:-development}"
FLAG_BOOTSTRAP_PROVIDER="${AURAXIS_FEATURE_FLAGS_PROVIDER:-}"
SKIP_LLM_PREFLIGHT="${AURAXIS_SKIP_LLM_PREFLIGHT:-false}"
SKIP_NODE_PREFLIGHT="${AURAXIS_SKIP_NODE_PREFLIGHT:-false}"
AUTO_USE_NVM="${AURAXIS_AUTO_USE_NVM:-true}"
NODE_MAJOR_REQUIRED="${AURAXIS_NODE_MAJOR_REQUIRED:-22}"
ENV_FILES=("${SQUAD_DIR}/.env" "${PLATFORM_ROOT}/.env")

if [[ ! -d "${SQUAD_DIR}" ]]; then
  echo "ai_squad directory not found at: ${SQUAD_DIR}" >&2
  exit 1
fi

resolve_env_value() {
  local key="$1"
  local raw=""

  if [[ -n "${!key:-}" ]]; then
    echo "${!key}"
    return 0
  fi

  for env_file in "${ENV_FILES[@]}"; do
    if [[ -f "${env_file}" ]]; then
      raw="$(grep -E "^${key}=" "${env_file}" 2>/dev/null | tail -n 1 | cut -d '=' -f2- || true)"
      if [[ -n "${raw}" ]]; then
        raw="${raw%\"}"
        raw="${raw#\"}"
        raw="${raw%\'}"
        raw="${raw#\'}"
        echo "${raw}"
        return 0
      fi
    fi
  done

  return 1
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

if [[ "${SKIP_LLM_PREFLIGHT}" != "true" ]]; then
  has_openai="false"
  has_ollama="false"
  resolved_openai="$(resolve_env_value "OPENAI_API_KEY" || true)"
  resolved_ollama="$(resolve_env_value "OLLAMA_BASE_URL" || true)"
  if [[ -n "${resolved_openai}" ]]; then
    export OPENAI_API_KEY="${resolved_openai}"
    has_openai="true"
  fi
  if [[ -n "${resolved_ollama}" ]]; then
    export OLLAMA_BASE_URL="${resolved_ollama}"
    has_ollama="true"
  fi
  if [[ "${has_openai}" != "true" && "${has_ollama}" != "true" ]]; then
    echo "[ai-next-task] LLM preflight failed: configure OPENAI_API_KEY or OLLAMA_BASE_URL in ${SQUAD_DIR}/.env, ${PLATFORM_ROOT}/.env, or env vars." >&2
    echo "[ai-next-task] Set AURAXIS_SKIP_LLM_PREFLIGHT=true only for diagnostics." >&2
    exit 1
  fi
fi

if [[ "${FLAG_BOOTSTRAP}" == "true" ]]; then
  if [[ ! -x "${FLAG_BOOTSTRAP_SCRIPT}" ]]; then
    echo "feature flag bootstrap script missing or not executable: ${FLAG_BOOTSTRAP_SCRIPT}" >&2
    exit 1
  fi
  echo "[ai-next-task] Bootstrapping feature flag provider env (${FLAG_BOOTSTRAP_ENV})..."
  if [[ -n "${FLAG_BOOTSTRAP_PROVIDER}" ]]; then
    eval "$("${FLAG_BOOTSTRAP_SCRIPT}" \
      --environment "${FLAG_BOOTSTRAP_ENV}" \
      --provider "${FLAG_BOOTSTRAP_PROVIDER}" \
      --format shell)"
  else
    eval "$("${FLAG_BOOTSTRAP_SCRIPT}" \
      --environment "${FLAG_BOOTSTRAP_ENV}" \
      --format shell)"
  fi
fi

if [[ "${AUTO_PREP}" == "true" ]]; then
  if [[ ! -x "${PREP_SCRIPT}" ]]; then
    echo "repo prep script missing or not executable: ${PREP_SCRIPT}" >&2
    exit 1
  fi
  echo "[ai-next-task] Preparing repository state for autonomous run..."
  "${PREP_SCRIPT}" "${TARGET_REPO}"
fi

requires_node_22="false"
case "${TARGET_REPO}" in
  all|auraxis-all|auraxis-web|auraxis-app)
    requires_node_22="true"
    ;;
esac

if [[ "${requires_node_22}" == "true" && "${SKIP_NODE_PREFLIGHT}" != "true" ]]; then
  if ! command -v node >/dev/null 2>&1; then
    if [[ "${AUTO_USE_NVM}" == "true" ]] && source_nvm; then
      nvm install "${NODE_MAJOR_REQUIRED}" >/dev/null
      nvm use "${NODE_MAJOR_REQUIRED}" >/dev/null
    fi
  fi

  if ! command -v node >/dev/null 2>&1; then
    echo "[ai-next-task] Node preflight failed: node runtime is required for auraxis-web/auraxis-app." >&2
    echo "[ai-next-task] Install/use Node ${NODE_MAJOR_REQUIRED}.x and rerun." >&2
    exit 1
  fi

  node_major="$(resolve_node_major)"
  if [[ "${node_major}" != "${NODE_MAJOR_REQUIRED}" ]]; then
    if [[ "${AUTO_USE_NVM}" == "true" ]]; then
      if source_nvm; then
        echo "[ai-next-task] Node mismatch detected (current $(node -v)); trying nvm use ${NODE_MAJOR_REQUIRED}..."
        nvm install "${NODE_MAJOR_REQUIRED}" >/dev/null
        nvm use "${NODE_MAJOR_REQUIRED}" >/dev/null
        node_major="$(resolve_node_major)"
      fi
    fi
  fi

  if [[ "${node_major}" != "${NODE_MAJOR_REQUIRED}" ]]; then
    node_version="$(node -v 2>/dev/null || true)"
    echo "[ai-next-task] Node preflight failed: expected Node ${NODE_MAJOR_REQUIRED}.x, current ${node_version}." >&2
    echo "[ai-next-task] Run 'nvm use ${NODE_MAJOR_REQUIRED}' (or equivalente) e tente novamente." >&2
    echo "[ai-next-task] Set AURAXIS_SKIP_NODE_PREFLIGHT=true only for diagnostics." >&2
    exit 1
  fi
fi

if [[ ! -d "${SQUAD_DIR}/.venv" ]]; then
  echo "ai_squad virtualenv missing. Bootstrapping automatically..."
  cd "${SQUAD_DIR}"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
fi

cd "${SQUAD_DIR}"
source .venv/bin/activate

export AURAXIS_TARGET_REPO="${TARGET_REPO}"
export AURAXIS_BRIEFING="${BRIEFING}"

if [[ "${MODE}" == "plan" ]]; then
  export AURAXIS_EXECUTION_MODE="plan_only"
else
  export AURAXIS_EXECUTION_MODE="run"
fi

LOCK_REPO="${TARGET_REPO}"
if [[ "${TARGET_REPO}" == "all" ]]; then
  LOCK_REPO="auraxis-all"
fi
(
  cd "${PLATFORM_ROOT}"
  ./scripts/agent-lock.sh acquire crewai "${LOCK_REPO}" "AI Squad run: ${BRIEFING}"
)
trap 'cd "${PLATFORM_ROOT}" && ./scripts/agent-lock.sh release crewai >/dev/null 2>&1 || true' EXIT

python3 main.py
