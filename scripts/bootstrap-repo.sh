#!/usr/bin/env bash
# scripts/bootstrap-repo.sh
# Bootstraps a new product repo inside repos/ with baseline governance files.
#
# Usage:
#   ./scripts/bootstrap-repo.sh <repo-name> [--submodule <git-url>]
#
# Examples:
#   ./scripts/bootstrap-repo.sh auraxis-web
#   ./scripts/bootstrap-repo.sh auraxis-web --submodule git@github.com:org/auraxis-web.git
#
# Without --submodule: creates a local git repo (for development before remote exists).
# With --submodule:    registers the remote as a git submodule in auraxis-platform.

set -euo pipefail

PLATFORM_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS_DIR="$PLATFORM_ROOT/repos"
TEMPLATES_DIR="$PLATFORM_ROOT/.context/templates"

# ── Argument parsing ───────────────────────────────────────────────────────────

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <repo-name> [--submodule <git-url>]"
  echo ""
  echo "Examples:"
  echo "  $0 auraxis-web"
  echo "  $0 auraxis-web --submodule git@github.com:org/auraxis-web.git"
  exit 1
fi

REPO_NAME="$1"
SUBMODULE_URL=""

if [[ $# -ge 3 && "$2" == "--submodule" ]]; then
  SUBMODULE_URL="$3"
fi

REPO_PATH="$REPOS_DIR/$REPO_NAME"

# ── Guards ─────────────────────────────────────────────────────────────────────

if [[ -d "$REPO_PATH" ]]; then
  echo "❌  Directory already exists: $REPO_PATH"
  echo "    Remove it first or choose a different name."
  exit 1
fi

if [[ ! -d "$TEMPLATES_DIR" ]]; then
  echo "❌  Templates directory not found: $TEMPLATES_DIR"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Auraxis Platform — Bootstrap: $REPO_NAME"
echo "════════════════════════════════════════════════════════"
echo ""

# ── Submodule mode ─────────────────────────────────────────────────────────────

if [[ -n "$SUBMODULE_URL" ]]; then
  echo "📦  Registering submodule from $SUBMODULE_URL ..."
  cd "$PLATFORM_ROOT"
  git submodule add "$SUBMODULE_URL" "repos/$REPO_NAME"
  git submodule update --init --recursive
  echo "✅  Submodule added. Committing pointer..."
  git add .gitmodules "repos/$REPO_NAME"
  git commit -m "chore(submodule): add $REPO_NAME as git submodule"
  echo ""
  echo "✅  Submodule registered. Navigate to repos/$REPO_NAME to apply templates."
  echo "    Run: cd repos/$REPO_NAME && ../../scripts/apply-templates.sh"
  exit 0
fi

# ── Local repo mode ────────────────────────────────────────────────────────────

echo "📁  Creating local repo at: $REPO_PATH"
mkdir -p "$REPO_PATH"
cd "$REPO_PATH"

# Init git
git init -b master
mkdir -p docs/adr .context

# ── Apply templates ────────────────────────────────────────────────────────────

echo "📄  Applying governance templates..."

# README
cat > README.md <<EOF
# $REPO_NAME

> Brief description of this repository.

## Stack

<!-- e.g. Nuxt.js / React Native / Python+Flask -->

## Bootstrap

1. Read \`.context/\` for context and governance.
2. Read \`steering.md\` for local execution rules.
3. Read \`tasks.md\` for current status and backlog.
4. Read \`AGENTS.md\` for agent-specific directives.
EOF

# AGENTS.md
cp "$TEMPLATES_DIR/AGENTS_TEMPLATE.md" ./AGENTS.md

# tasks.md
cp "$TEMPLATES_DIR/TASKS_TEMPLATE.md" ./tasks.md
# Stamp current date
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" ./tasks.md 2>/dev/null || true

# steering.md
cp "$TEMPLATES_DIR/REPO_STEERING_TEMPLATE.md" ./steering.md

# ADR template
cp "$TEMPLATES_DIR/ADR_TEMPLATE.md" ./docs/adr/ADR-000-template.md

# .gitignore minimal
cat > .gitignore <<'EOF'
# OS / editor
.DS_Store
.idea/
.vscode/

# Environment
.env
.env.*
*.local

# Logs
*.log
logs/

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build
dist/
build/
.nuxt/
.output/
EOF

# .context local placeholder
cat > .context/README.md <<EOF
# .context — Local Knowledge Base

This directory holds the local context for \`$REPO_NAME\`.

## Files

- This directory is pre-populated by the platform bootstrap.
- Add architecture snapshots, quality gates, backlog, and handoffs here.

## Reference

For global context, see the platform's \`.context/\` at:
\`../../.context/\` (relative to this repo)
EOF

# ── Initial commit ─────────────────────────────────────────────────────────────

echo "💾  Creating initial commit..."
git add .
git commit -m "docs: bootstrap repository governance and templates"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅  $REPO_NAME bootstrapped successfully"
echo "════════════════════════════════════════════════════════"
echo ""
echo "  Location:  repos/$REPO_NAME"
echo ""
echo "  Next steps:"
echo "  1. Edit README.md — describe the repo"
echo "  2. Edit steering.md — adapt local rules for this stack"
echo "  3. Edit tasks.md — add the first backlog items"
echo "  4. Create a remote repo and add it as origin:"
echo "     cd repos/$REPO_NAME"
echo "     git remote add origin <git-url>"
echo "  5. Register as submodule in auraxis-platform (when ready):"
echo "     cd $PLATFORM_ROOT"
echo "     git submodule add <git-url> repos/$REPO_NAME"
echo ""
