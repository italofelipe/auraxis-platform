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

  local default_branch
  default_branch="$(resolve_default_branch "$repo_path")"
  if [[ -z "$default_branch" ]]; then
    echo "[prepare] ERROR ${repo_name}: could not resolve default branch (origin/HEAD)."
    return 1
  fi

  local current_branch
  current_branch="$(git -C "$repo_path" rev-parse --abbrev-ref HEAD)"

  if [[ "$current_branch" == "HEAD" ]]; then
    echo "[prepare] ${repo_name}: detached HEAD -> checkout ${default_branch}"
    if git -C "$repo_path" show-ref --verify --quiet "refs/heads/${default_branch}"; then
      git -C "$repo_path" checkout "$default_branch" >/dev/null
    else
      git -C "$repo_path" checkout -b "$default_branch" --track "origin/${default_branch}" >/dev/null
    fi
    current_branch="$default_branch"
  fi

  if [[ "$current_branch" != "$default_branch" ]]; then
    local dirty
    dirty="$(git -C "$repo_path" status --porcelain)"
    if [[ -n "$dirty" ]]; then
      echo "[prepare] ERROR ${repo_name}: cannot switch ${current_branch} -> ${default_branch} because worktree is dirty."
      return 1
    fi
    echo "[prepare] ${repo_name}: normalizing branch ${current_branch} -> ${default_branch}"
    if git -C "$repo_path" show-ref --verify --quiet "refs/heads/${default_branch}"; then
      git -C "$repo_path" checkout "$default_branch" >/dev/null
    else
      git -C "$repo_path" checkout -b "$default_branch" --track "origin/${default_branch}" >/dev/null
    fi
  fi

  echo "[prepare] ${repo_name}: syncing ${default_branch} with origin/${default_branch}"
  if ! git -C "$repo_path" pull --rebase origin "$default_branch" >/dev/null; then
    echo "[prepare] ERROR ${repo_name}: failed to rebase ${default_branch} from origin/${default_branch}."
    return 1
  fi
}

if [[ "$TARGET" == "all" || "$TARGET" == "auraxis-all" || "$TARGET" == "*" ]]; then
  prepare_repo "auraxis-api"
  prepare_repo "auraxis-web"
  prepare_repo "auraxis-app"
else
  prepare_repo "$TARGET"
fi
