#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bootstrap-feature-flag-provider.sh [options]

Options:
  --environment <development|staging|production>   Runtime environment (default: development)
  --provider <local|unleash>                       Provider override (default by environment)
  --unleash-url <url>                              Unleash base URL override
  --format <shell|env>                             Output format (default: shell)
  --help                                           Show this help

Examples:
  ./scripts/bootstrap-feature-flag-provider.sh --environment development
  ./scripts/bootstrap-feature-flag-provider.sh --environment staging --provider unleash --format env
USAGE
}

ENVIRONMENT="${AURAXIS_FEATURE_FLAGS_ENV:-development}"
PROVIDER_OVERRIDE="${AURAXIS_FEATURE_FLAGS_PROVIDER:-}"
UNLEASH_URL_OVERRIDE="${AURAXIS_UNLEASH_URL:-}"
OUTPUT_FORMAT="shell"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --provider)
      PROVIDER_OVERRIDE="$2"
      shift 2
      ;;
    --unleash-url)
      UNLEASH_URL_OVERRIDE="$2"
      shift 2
      ;;
    --format)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "$ENVIRONMENT" in
  development|staging|production) ;;
  *)
    echo "Invalid environment: ${ENVIRONMENT}" >&2
    exit 1
    ;;
esac

if [[ -n "$PROVIDER_OVERRIDE" ]]; then
  PROVIDER="$PROVIDER_OVERRIDE"
else
  if [[ "$ENVIRONMENT" == "development" ]]; then
    PROVIDER="local"
  else
    PROVIDER="unleash"
  fi
fi

if [[ "$PROVIDER" != "local" && "$PROVIDER" != "unleash" ]]; then
  echo "Invalid provider: ${PROVIDER}. Use local|unleash." >&2
  exit 1
fi

UNLEASH_URL="$UNLEASH_URL_OVERRIDE"
if [[ -z "$UNLEASH_URL" && "$PROVIDER" == "unleash" ]]; then
  UNLEASH_URL="https://unleash.sensoriumit.internal"
fi

UNLEASH_ENVIRONMENT="$ENVIRONMENT"
CACHE_TTL_MS="${AURAXIS_UNLEASH_CACHE_TTL_MS:-30000}"

emit_line() {
  local key="$1"
  local value="$2"
  if [[ "$OUTPUT_FORMAT" == "env" ]]; then
    printf '%s=%s\n' "$key" "$value"
  else
    printf 'export %s=%q\n' "$key" "$value"
  fi
}

if [[ "$OUTPUT_FORMAT" != "shell" && "$OUTPUT_FORMAT" != "env" ]]; then
  echo "Invalid format: ${OUTPUT_FORMAT}. Use shell|env." >&2
  exit 1
fi

# Canonical namespace (cross-repo).
emit_line "AURAXIS_RUNTIME_ENV" "$ENVIRONMENT"
emit_line "AURAXIS_FLAG_PROVIDER" "$PROVIDER"
emit_line "AURAXIS_UNLEASH_URL" "$UNLEASH_URL"
emit_line "AURAXIS_UNLEASH_ENVIRONMENT" "$UNLEASH_ENVIRONMENT"
emit_line "AURAXIS_UNLEASH_CACHE_TTL_MS" "$CACHE_TTL_MS"

# API namespace.
emit_line "AURAXIS_UNLEASH_APP_NAME" "auraxis-api"
emit_line "AURAXIS_UNLEASH_INSTANCE_ID" "auraxis-api"

# Web namespace.
emit_line "NUXT_PUBLIC_FLAG_PROVIDER" "$PROVIDER"
emit_line "NUXT_PUBLIC_UNLEASH_PROXY_URL" "$UNLEASH_URL"
emit_line "NUXT_PUBLIC_UNLEASH_ENVIRONMENT" "$UNLEASH_ENVIRONMENT"
emit_line "NUXT_PUBLIC_UNLEASH_CACHE_TTL_MS" "$CACHE_TTL_MS"
emit_line "NUXT_PUBLIC_UNLEASH_APP_NAME" "auraxis-web"
emit_line "NUXT_PUBLIC_UNLEASH_INSTANCE_ID" "auraxis-web"

# App namespace.
emit_line "EXPO_PUBLIC_FLAG_PROVIDER" "$PROVIDER"
emit_line "EXPO_PUBLIC_UNLEASH_PROXY_URL" "$UNLEASH_URL"
emit_line "EXPO_PUBLIC_UNLEASH_ENVIRONMENT" "$UNLEASH_ENVIRONMENT"
emit_line "EXPO_PUBLIC_UNLEASH_CACHE_TTL_MS" "$CACHE_TTL_MS"
emit_line "EXPO_PUBLIC_UNLEASH_APP_NAME" "auraxis-app"
emit_line "EXPO_PUBLIC_UNLEASH_INSTANCE_ID" "auraxis-app"
