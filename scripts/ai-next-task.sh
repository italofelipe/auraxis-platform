#!/usr/bin/env bash
set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQUAD_DIR="${PLATFORM_ROOT}/ai_squad"
PREP_SCRIPT="${PLATFORM_ROOT}/scripts/prepare-repo-for-agent-run.sh"

TARGET_REPO="${1:-all}"
BRIEFING="${2:-Execute a tarefa}"
MODE="${3:-run}"
AUTO_PREP="${AURAXIS_AUTO_PREP_REPOS:-true}"

if [[ ! -d "${SQUAD_DIR}" ]]; then
  echo "ai_squad directory not found at: ${SQUAD_DIR}" >&2
  exit 1
fi

if [[ "${AUTO_PREP}" == "true" ]]; then
  if [[ ! -x "${PREP_SCRIPT}" ]]; then
    echo "repo prep script missing or not executable: ${PREP_SCRIPT}" >&2
    exit 1
  fi
  echo "[ai-next-task] Preparing repository state for autonomous run..."
  "${PREP_SCRIPT}" "${TARGET_REPO}"
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
