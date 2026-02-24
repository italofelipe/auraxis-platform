#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${1:-$ROOT_DIR/governance/github/branch-protection-config.json}"
API_URL="${GITHUB_API_URL:-https://api.github.com}"
TOKEN="${GITHUB_ADMIN_TOKEN:-${GH_ADMIN_TOKEN:-${GITHUB_TOKEN:-}}}"
DRY_RUN="${DRY_RUN:-false}"

if ! command -v jq >/dev/null 2>&1; then
  echo "Erro: jq nao encontrado no PATH." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Erro: curl nao encontrado no PATH." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Erro: arquivo de config nao encontrado: $CONFIG_FILE" >&2
  exit 1
fi

if [[ -z "$TOKEN" && "$DRY_RUN" != "true" ]]; then
  echo "Erro: token GitHub ausente." >&2
  echo "Defina GITHUB_ADMIN_TOKEN com permissao de administracao de repositorio." >&2
  exit 1
fi

OWNER="$(jq -r '.owner' "$CONFIG_FILE")"

build_payload() {
  local checks_json="$1"
  jq -n \
    --argjson checks "$checks_json" \
    --argjson strict "$(jq '.rules.required_status_checks_strict' "$CONFIG_FILE")" \
    --argjson enforce_admins "$(jq '.rules.enforce_admins' "$CONFIG_FILE")" \
    --argjson dismiss_stale_reviews "$(jq '.rules.required_pull_request_reviews.dismiss_stale_reviews' "$CONFIG_FILE")" \
    --argjson require_code_owner_reviews "$(jq '.rules.required_pull_request_reviews.require_code_owner_reviews' "$CONFIG_FILE")" \
    --argjson required_approving_review_count "$(jq '.rules.required_pull_request_reviews.required_approving_review_count' "$CONFIG_FILE")" \
    --argjson require_last_push_approval "$(jq '.rules.required_pull_request_reviews.require_last_push_approval' "$CONFIG_FILE")" \
    --argjson required_conversation_resolution "$(jq '.rules.required_conversation_resolution' "$CONFIG_FILE")" \
    --argjson required_linear_history "$(jq '.rules.required_linear_history' "$CONFIG_FILE")" \
    --argjson allow_force_pushes "$(jq '.rules.allow_force_pushes' "$CONFIG_FILE")" \
    --argjson allow_deletions "$(jq '.rules.allow_deletions' "$CONFIG_FILE")" \
    --argjson block_creations "$(jq '.rules.block_creations' "$CONFIG_FILE")" \
    --argjson lock_branch "$(jq '.rules.lock_branch' "$CONFIG_FILE")" \
    --argjson allow_fork_syncing "$(jq '.rules.allow_fork_syncing' "$CONFIG_FILE")" \
    '{
      required_status_checks: {
        strict: $strict,
        contexts: $checks
      },
      enforce_admins: $enforce_admins,
      required_pull_request_reviews: {
        dismiss_stale_reviews: $dismiss_stale_reviews,
        require_code_owner_reviews: $require_code_owner_reviews,
        required_approving_review_count: $required_approving_review_count,
        require_last_push_approval: $require_last_push_approval
      },
      restrictions: null,
      required_linear_history: $required_linear_history,
      allow_force_pushes: $allow_force_pushes,
      allow_deletions: $allow_deletions,
      block_creations: $block_creations,
      required_conversation_resolution: $required_conversation_resolution,
      lock_branch: $lock_branch,
      allow_fork_syncing: $allow_fork_syncing
    }'
}

branch_exists() {
  local repo="$1"
  local branch="$2"

  if [[ -z "$TOKEN" ]]; then
    return 0
  fi

  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$API_URL/repos/$OWNER/$repo/branches/$branch")"

  [[ "$code" == "200" ]]
}

apply_protection() {
  local repo="$1"
  local branch="$2"
  local checks_json="$3"

  local payload
  payload="$(build_payload "$checks_json")"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "DRY_RUN repo=$repo branch=$branch"
    echo "$payload" | jq .
    return 0
  fi

  local resp_file
  resp_file="$(mktemp)"

  local code
  code="$(curl -sS -o "$resp_file" -w "%{http_code}" \
    -X PUT \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$API_URL/repos/$OWNER/$repo/branches/$branch/protection" \
    -d "$payload")"

  if [[ "$code" != "200" ]]; then
    echo "Falha ao aplicar branch protection em $repo:$branch (HTTP $code)" >&2
    cat "$resp_file" >&2
    rm -f "$resp_file"
    exit 1
  fi

  rm -f "$resp_file"
  echo "OK: branch protection aplicada em $repo:$branch"
}

while IFS= read -r repo_cfg; do
  REPO_NAME="$(jq -r '.name' <<<"$repo_cfg")"
  CHECKS_JSON="$(jq -c '.required_checks' <<<"$repo_cfg")"

  while IFS= read -r branch; do
    if branch_exists "$REPO_NAME" "$branch"; then
      apply_protection "$REPO_NAME" "$branch" "$CHECKS_JSON"
    else
      echo "SKIP: branch inexistente $REPO_NAME:$branch"
    fi
  done < <(jq -r '.branches[]' <<<"$repo_cfg")
done < <(jq -c '.repositories[]' "$CONFIG_FILE")

echo "Concluido."
