#!/usr/bin/env bash
set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS_DIR="${PLATFORM_ROOT}/repos"

TARGET="${1:-all}"

resolve_default_branch() {
  local repo_path="$1"
  local default_branch
  default_branch="$(git -C "$repo_path" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)"
  default_branch="${default_branch#origin/}"
  if [[ -n "$default_branch" ]]; then
    printf "%s" "$default_branch"
    return 0
  fi
  for candidate in main master; do
    if git -C "$repo_path" show-ref --verify --quiet "refs/remotes/origin/${candidate}"; then
      printf "%s" "$candidate"
      return 0
    fi
  done
  printf ""
}

prepare_repo() {
  local repo_name="$1"
  local repo_path="${REPOS_DIR}/${repo_name}"
  if [[ ! -d "$repo_path" ]]; then
    echo "[prepare] SKIP ${repo_name}: path not found (${repo_path})"
    return 0
  fi

  echo "[prepare] ${repo_name}: fetching remotes..."
  git -C "$repo_path" fetch origin --prune >/dev/null 2>&1 || true

  local current_branch
  current_branch="$(git -C "$repo_path" rev-parse --abbrev-ref HEAD)"
  local default_branch
  default_branch="$(resolve_default_branch "$repo_path")"

  if [[ "$current_branch" == "HEAD" ]]; then
    if [[ -z "$default_branch" ]]; then
      echo "[prepare] WARN ${repo_name}: detached HEAD and could not resolve default branch."
      return 0
    fi
    echo "[prepare] ${repo_name}: detached HEAD -> checkout ${default_branch}"
    git -C "$repo_path" checkout "$default_branch" >/dev/null
    current_branch="$default_branch"
  fi

  if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
    echo "[prepare] ${repo_name}: syncing ${current_branch} with origin/${current_branch}"
    git -C "$repo_path" pull --rebase origin "$current_branch" >/dev/null
  else
    echo "[prepare] ${repo_name}: on ${current_branch} (no base-branch auto-pull)."
  fi
}

if [[ "$TARGET" == "all" || "$TARGET" == "auraxis-all" || "$TARGET" == "*" ]]; then
  prepare_repo "auraxis-api"
  prepare_repo "auraxis-web"
  prepare_repo "auraxis-app"
else
  prepare_repo "$TARGET"
fi
