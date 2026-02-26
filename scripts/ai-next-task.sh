#!/usr/bin/env bash
set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQUAD_DIR="${PLATFORM_ROOT}/ai_squad"

TARGET_REPO="${1:-all}"
BRIEFING="${2:-Execute a próxima tarefa}"

if [[ ! -d "${SQUAD_DIR}" ]]; then
  echo "ai_squad directory not found at: ${SQUAD_DIR}" >&2
  exit 1
fi

if [[ ! -d "${SQUAD_DIR}/.venv" ]]; then
  echo "Missing ai_squad virtualenv at ${SQUAD_DIR}/.venv" >&2
  echo "Run: make squad-setup" >&2
  exit 1
fi

cd "${SQUAD_DIR}"
source .venv/bin/activate

export AURAXIS_TARGET_REPO="${TARGET_REPO}"
export AURAXIS_BRIEFING="${BRIEFING}"

python3 main.py
