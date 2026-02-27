#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="${AURAXIS_API_DIR:-$ROOT_DIR/repos/auraxis-api}"
API_PYTHON="${AURAXIS_API_PYTHON:-$API_DIR/.venv/bin/python}"
OUTPUT_PATH="${AURAXIS_OPENAPI_OUT:-$ROOT_DIR/.context/openapi/openapi.snapshot.json}"
TEMP_DB_PATH="${AURAXIS_OPENAPI_TEMP_DB:-$API_DIR/tmp-openapi-export.sqlite3}"

if [[ ! -d "$API_DIR" ]]; then
  echo "[openapi-export] API repo not found: $API_DIR" >&2
  exit 1
fi

if [[ ! -x "$API_PYTHON" ]]; then
  echo "[openapi-export] Python executable not found: $API_PYTHON" >&2
  echo "[openapi-export] Run setup in auraxis-api (.venv) or set AURAXIS_API_PYTHON." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"

echo "[openapi-export] generating snapshot from $API_DIR"
(
  cd "$API_DIR"
  FLASK_TESTING=true \
  SECURITY_ENFORCE_STRONG_SECRETS=false \
  DOCS_EXPOSURE_POLICY=public \
  DATABASE_URL="sqlite:///$TEMP_DB_PATH" \
  "$API_PYTHON" - <<'PY' "$OUTPUT_PATH"
import json
import sys

from app import create_app
from app.extensions.database import db

output_path = sys.argv[1]

app = create_app()
app.config["TESTING"] = True

with app.app_context():
    db.drop_all()
    db.create_all()

with app.test_client() as client:
    response = client.get("/docs/swagger/")
    if response.status_code != 200:
        raise RuntimeError(f"Swagger endpoint returned {response.status_code}")
    payload = response.get_json() or {}

with open(output_path, "w", encoding="utf-8") as target:
    json.dump(payload, target, ensure_ascii=False, indent=2, sort_keys=True)
    target.write("\n")
PY
)

echo "[openapi-export] snapshot written to $OUTPUT_PATH"
