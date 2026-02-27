"""
Auraxis AI Squad — CrewAI Tools (BaseTool).

All tools use the security primitives from tool_security.py:
- validate_write_path() for file writes
- safe_subprocess() for subprocess calls
- audit_log() for structured audit logging

References:
- ai_squad/tools/tool_security.py — security module
- ai_squad/AGENT_ARCHITECTURE.md — tools registry
- .context/05_quality_and_gates.md — quality gates
"""

import fnmatch
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

from crewai.tools import BaseTool

from .tool_security import (
    CONVENTIONAL_BRANCH_PREFIXES,
    DEFAULT_TIMEOUT_SECONDS,
    GIT_STAGE_BLOCKLIST,
    SHARED_CONTRACTS_DIR,
    PROJECT_ROOT,
    TARGET_REPO_NAME,
    audit_log,
    safe_subprocess,
    validate_shared_contract_path,
    validate_write_path,
)

TASKS_FILE_CANDIDATES: tuple[str, ...] = ("TASKS.md", "tasks.md")


def _resolve_tasks_file() -> Path:
    """Resolve task board filename across repositories."""
    for filename in TASKS_FILE_CANDIDATES:
        candidate = PROJECT_ROOT / filename
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / "TASKS.md"

# ---------------------------------------------------------------------------
# GOVERNANCE_ALLOWLIST — files that read_governance_file can access.
# ---------------------------------------------------------------------------
GOVERNANCE_ALLOWLIST: list[str] = ["product.md", "steering.md"]

# ---------------------------------------------------------------------------
# Read-only tools
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Helpers for ReadPendingTasksTool (extracted to keep cyclomatic complexity low)
# ---------------------------------------------------------------------------

_PENDING_STATUSES = ("| Todo", "| In Progress", "| Blocked")
_PENDING_CHECKLIST_MARKERS = ("- [ ]", "- [~]", "- [!]")
_ORDERED_LIST_PREFIXES = ("1.", "2.", "3.", "4.", "5.")
_PENDING_BLOCK_MARKER = "Pendencias de execucao imediata"
_TASK_ID_PATTERN = re.compile(r"^[A-Z]+-\d+$|^[A-Z]+\d+$")


def _extract_pending_rows(lines: list[str]) -> list[str]:
    """Return table rows whose status is Todo, In Progress, or Blocked."""
    return [
        line
        for line in lines
        if line.startswith("|") and any(s in line for s in _PENDING_STATUSES)
    ]


def _extract_pending_checklist(lines: list[str]) -> list[str]:
    """Return checklist tasks marked as todo/in-progress/blocked."""
    extracted: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not any(stripped.startswith(prefix) for prefix in _PENDING_CHECKLIST_MARKERS):
            continue
        extracted.append(line)
    return extracted


def _extract_pending_block(lines: list[str]) -> list[str]:
    """Return the 'Pendencias de execucao imediata' ordered-list block."""
    block: list[str] = []
    in_block = False
    for line in lines:
        if _PENDING_BLOCK_MARKER in line:
            in_block = True
            block.append(line)
            continue
        if in_block:
            if line.strip() == "" and any(
                item.startswith(_ORDERED_LIST_PREFIXES) for item in block
            ):
                break
            block.append(line)
    return block


class ReadTasksTool(BaseTool):
    name: str = "read_tasks"
    description: str = (
        "Reads TASKS.md to understand current project status, "
        "backlog, and priorities."
    )

    def _run(self, query: str = None) -> str:
        path = _resolve_tasks_file()
        audit_log("read_tasks", {"path": str(path)}, "reading", status="OK")
        if not path.exists():
            return f"Error: tasks file not found at {path}"
        return path.read_text(encoding="utf-8")


class ReadPendingTasksTool(BaseTool):
    name: str = "read_pending_tasks"
    description: str = (
        "Reads TASKS.md and returns ONLY tasks with status Todo or In Progress. "
        "Use this instead of read_tasks to avoid the 'lost in the middle' problem "
        "with large files. Returns a focused view of what needs to be done."
    )

    def _run(self, query: str = None) -> str:
        path = _resolve_tasks_file()
        if not path.exists():
            return f"Error: tasks file not found at {path}"

        lines = path.read_text(encoding="utf-8").splitlines()
        pending_lines = _extract_pending_rows(lines)
        pending_checklist = _extract_pending_checklist(lines)
        pending_block = _extract_pending_block(lines)

        result_parts: list[str] = [
            f"# {path.name} — Pending Tasks Only (Todo / In Progress / Blocked)",
            "",
        ]
        if pending_block:
            result_parts.extend(pending_block)
            result_parts.append("")
        if pending_lines:
            result_parts.append("| ID | Area | Tarefa | Status | Progresso | Risco |")
            result_parts.append("|---|---|---|---|---|---|")
            result_parts.extend(pending_lines)
        if pending_checklist:
            if pending_lines:
                result_parts.append("")
            result_parts.append("Checklist pending tasks:")
            result_parts.extend(pending_checklist)
        if not pending_lines and not pending_checklist:
            result_parts.append("No pending tasks found — all tasks are Done.")

        output = "\n".join(result_parts)
        audit_log(
            "read_pending_tasks",
            {
                "pending_table_count": len(pending_lines),
                "pending_checklist_count": len(pending_checklist),
            },
            (
                "returned pending tasks: "
                f"table={len(pending_lines)} checklist={len(pending_checklist)}"
            ),
            status="OK",
        )
        return output


class ReadTasksSectionTool(BaseTool):
    name: str = "read_tasks_section"
    description: str = (
        "Reads a specific section of TASKS.md by heading keyword. "
        "Use this to read only the relevant part of the file. "
        "Example: section_keyword='Ciclo B' or 'B8' or 'Autenticacao'. "
        "Returns the matching section and up to 40 lines of context."
    )

    def _run(self, section_keyword: str) -> str:
        path = _resolve_tasks_file()
        if not path.exists():
            return f"Error: tasks file not found at {path}"

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Find lines containing the keyword
        matches: list[tuple[int, str]] = [
            (i, line)
            for i, line in enumerate(lines)
            if section_keyword.lower() in line.lower()
        ]

        if not matches:
            return (
                f"No section found matching '{section_keyword}' in {path.name}. "
                f"Try a broader keyword."
            )

        # Return context around the first match: up to 40 lines after
        first_idx = matches[0][0]
        start = max(0, first_idx - 2)
        end = min(len(lines), first_idx + 40)
        excerpt = "\n".join(lines[start:end])

        audit_log(
            "read_tasks_section",
            {"section_keyword": section_keyword, "line": first_idx},
            f"returned lines {start}-{end}",
            status="OK",
        )
        return (
            f"# {path.name} — Section: '{section_keyword}' "
            f"(lines {start + 1}-{end})\n\n{excerpt}"
        )


class ReadProjectFileTool(BaseTool):
    name: str = "read_project_file"
    description: str = (
        "Reads ANY existing file from the project. "
        "Path must be relative to project root "
        "(e.g., 'app/models/user.py', 'app/schemas/user_schemas.py'). "
        "ALWAYS use this before writing to a file that may already exist. "
        "This is the primary tool for reading source code."
    )

    def _run(self, path: str) -> str:
        resolved = (PROJECT_ROOT / path).resolve()

        if not resolved.is_relative_to(PROJECT_ROOT):
            msg = f"BLOCKED: '{path}' escapes project root."
            audit_log("read_project_file", {"path": path}, msg, status="BLOCKED")
            return msg

        audit_log("read_project_file", {"path": path}, "reading", status="OK")
        if not resolved.exists():
            return f"FILE_NOT_FOUND: '{path}' does not exist yet."
        return resolved.read_text(encoding="utf-8")


class ListProjectFilesTool(BaseTool):
    name: str = "list_project_files"
    description: str = (
        "Lists files inside a project directory. "
        "Path must be relative to project root "
        "(e.g., 'app/models', 'app/graphql/mutations', 'migrations/versions'). "
        "Use this to discover what files already exist before creating new ones."
    )

    def _run(self, directory: str) -> str:
        resolved = (PROJECT_ROOT / directory).resolve()

        if not resolved.is_relative_to(PROJECT_ROOT):
            return f"BLOCKED: '{directory}' escapes project root."

        if not resolved.exists():
            return f"DIRECTORY_NOT_FOUND: '{directory}' does not exist."

        files = sorted(
            str(f.relative_to(PROJECT_ROOT))
            for f in resolved.rglob("*")
            if f.is_file() and "__pycache__" not in str(f)
        )
        audit_log(
            "list_project_files",
            {"directory": directory},
            f"listed {len(files)} files",
            status="OK",
        )
        return f"Files in '{directory}':\n" + "\n".join(files)


class GetLatestMigrationTool(BaseTool):
    name: str = "get_latest_migration"
    description: str = (
        "Returns the revision ID and filename of the latest Alembic migration. "
        "ALWAYS call this before creating a new migration to get the correct "
        "down_revision value. Without this, the migration chain breaks."
    )

    def _run(self, query: str = None) -> str:
        versions_dir = PROJECT_ROOT / "migrations" / "versions"
        if not versions_dir.exists():
            return "Error: migrations/versions/ directory not found."

        migration_files = sorted(
            f
            for f in versions_dir.iterdir()
            if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
        )

        if not migration_files:
            return "No migrations found. Use down_revision = None for the first one."

        latest = migration_files[-1]
        content = latest.read_text(encoding="utf-8")

        # Extract revision ID
        revision_id = "unknown"
        for line in content.splitlines():
            if line.strip().startswith("revision"):
                revision_id = line.split("=")[1].strip().strip('"').strip("'")
                break

        audit_log(
            "get_latest_migration",
            {"file": latest.name},
            f"revision={revision_id}",
            status="OK",
        )
        return (
            f"Latest migration:\n"
            f"  File: migrations/versions/{latest.name}\n"
            f"  Revision ID: {revision_id}\n\n"
            f"Use this as down_revision in your new migration."
        )


class ReadAlembicHistoryTool(BaseTool):
    name: str = "read_alembic_history"
    description: str = (
        "Reads ALL Alembic migrations and returns a summary of every "
        "column operation (add, drop, rename, alter) ever applied to a table. "
        "Use this to know which columns ALREADY EXIST in the database "
        "before writing a migration. This prevents writing add_column "
        "for a column that should be renamed, or adding a duplicate column."
    )

    def _run(self, table_name: str = "users") -> str:
        versions_dir = PROJECT_ROOT / "migrations" / "versions"
        if not versions_dir.exists():
            return "Error: migrations/versions/ directory not found."

        migration_files = sorted(
            f
            for f in versions_dir.iterdir()
            if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
        )

        if not migration_files:
            return f"No migrations found for table '{table_name}'."

        ops: list[str] = []
        for mf in migration_files:
            content = mf.read_text(encoding="utf-8")
            if table_name not in content:
                continue
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("op.") and table_name in stripped:
                    ops.append(f"  {mf.name}: {stripped}")

        if not ops:
            return f"No operations found for table '{table_name}'."

        audit_log(
            "read_alembic_history",
            {"table_name": table_name},
            f"found {len(ops)} operations",
            status="OK",
        )
        return (
            f"Alembic history for table '{table_name}' "
            f"({len(ops)} operations):\n" + "\n".join(ops)
        )


# ---------------------------------------------------------------------------
# Helpers for ValidateMigrationConsistencyTool (extracted for low complexity)
# ---------------------------------------------------------------------------


def _extract_model_columns(content: str) -> list[str]:
    """Extract db.Column attribute names from a model file."""
    cols: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if "db.Column(" in stripped and "=" in stripped:
            cols.append(stripped.split("=")[0].strip())
    return cols


def _extract_sa_column_name(line: str) -> str | None:
    """Extract the column name from a sa.Column('name', ...) call."""
    for quote in ['"', "'"]:
        marker = f"sa.Column({quote}"
        if marker in line:
            return line.split(marker)[1].split(quote)[0]
    return None


def _extract_migration_ops(content: str) -> tuple[list[str], list[str]]:
    """Return (add_columns, alter_lines) from a migration file."""
    add_cols: list[str] = []
    alter_lines: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if "op.add_column" in stripped:
            col = _extract_sa_column_name(stripped)
            if col:
                add_cols.append(col)
        if "op.alter_column" in stripped:
            alter_lines.append(stripped)
    return add_cols, alter_lines


def _collect_existing_columns(versions_dir: Path, exclude_file: Path) -> set[str]:
    """Scan previous migrations for column names already in the DB."""
    existing: set[str] = set()
    for mf in sorted(versions_dir.iterdir()):
        if mf == exclude_file or mf.suffix != ".py":
            continue
        if mf.name == "__init__.py":
            continue
        for line in mf.read_text(encoding="utf-8").splitlines():
            col = _extract_sa_column_name(line.strip())
            if col and "sa.Column(" in line:
                existing.add(col)
    return existing


def _build_consistency_report(
    mig_add_cols: list[str],
    model_cols: list[str],
    existing_cols: set[str],
) -> tuple[list[str], list[str]]:
    """Return (issues, warnings) comparing migration ops vs model/DB."""
    issues: list[str] = []
    warnings: list[str] = []
    for col in mig_add_cols:
        if col in existing_cols:
            issues.append(
                f"CONFLICT: add_column('{col}') but column already "
                f"exists in a previous migration. "
                f"Use op.alter_column() to rename instead."
            )
        if col not in model_cols:
            warnings.append(
                f"WARNING: migration adds '{col}' but model has no "
                f"matching db.Column attribute."
            )
    return issues, warnings


class ValidateMigrationConsistencyTool(BaseTool):
    name: str = "validate_migration_consistency"
    description: str = (
        "Compares a model file against a migration file to check consistency. "
        "Detects: (1) columns in migration that do not match model, "
        "(2) model columns that have no migration, "
        "(3) add_column for a column that already exists in a previous migration "
        "(should be alter_column/rename instead). "
        "Run this AFTER writing model and migration, BEFORE committing."
    )

    def _run(self, model_path: str, migration_path: str) -> str:
        model_file = PROJECT_ROOT / model_path
        migration_file = PROJECT_ROOT / migration_path

        if not model_file.exists():
            return f"Error: model file not found: {model_path}"
        if not migration_file.exists():
            return f"Error: migration file not found: {migration_path}"

        model_cols = _extract_model_columns(model_file.read_text(encoding="utf-8"))
        mig_add_cols, _ = _extract_migration_ops(
            migration_file.read_text(encoding="utf-8")
        )

        versions_dir = PROJECT_ROOT / "migrations" / "versions"
        existing_cols = _collect_existing_columns(
            versions_dir, migration_file.resolve()
        )

        issues, warnings = _build_consistency_report(
            mig_add_cols, model_cols, existing_cols
        )

        if not issues and not warnings:
            result = "CONSISTENT: model and migration are aligned."
        else:
            parts = []
            if issues:
                parts.append("ISSUES (must fix):\n" + "\n".join(issues))
            if warnings:
                parts.append("WARNINGS:\n" + "\n".join(warnings))
            result = "\n\n".join(parts)

        audit_log(
            "validate_migration_consistency",
            {"model": model_path, "migration": migration_path},
            result[:200],
            status="OK" if not issues else "ERROR",
        )
        return result


class ReadSchemaTool(BaseTool):
    name: str = "read_schema"
    description: str = "Reads schema.graphql to understand GraphQL API contracts."

    def _run(self, query: str = None) -> str:
        path = PROJECT_ROOT / "schema.graphql"
        audit_log("read_schema", {"path": str(path)}, "reading", status="OK")
        if not path.exists():
            return f"Error: schema.graphql not found at {path}"
        return path.read_text(encoding="utf-8")


class ReadContextFileTool(BaseTool):
    name: str = "read_context_file"
    description: str = (
        "Reads a file from the .context/ knowledge base. "
        "Provide the filename relative to .context/ "
        "(e.g., 'README.md', '04_architecture_snapshot.md')."
    )

    def _run(self, filename: str) -> str:
        context_dir = PROJECT_ROOT / ".context"
        resolved = (context_dir / filename).resolve()

        # Anti-escape: must stay inside .context/
        if not resolved.is_relative_to(context_dir):
            msg = f"BLOCKED: '{filename}' escapes .context/ directory."
            audit_log(
                "read_context_file",
                {"filename": filename},
                msg,
                status="BLOCKED",
            )
            return msg

        audit_log(
            "read_context_file",
            {"filename": filename},
            "reading",
            status="OK",
        )
        if not resolved.exists():
            return f"Error: File not found: .context/{filename}"
        return resolved.read_text(encoding="utf-8")


class ReadGovernanceFileTool(BaseTool):
    name: str = "read_governance_file"
    description: str = (
        "Reads a governance file (product.md or steering.md) " "from the project root."
    )

    def _run(self, filename: str) -> str:
        if filename not in GOVERNANCE_ALLOWLIST:
            msg = (
                f"BLOCKED: '{filename}' is not a governance file. "
                f"Allowed: {GOVERNANCE_ALLOWLIST}"
            )
            audit_log(
                "read_governance_file",
                {"filename": filename},
                msg,
                status="BLOCKED",
            )
            return msg

        path = PROJECT_ROOT / filename
        audit_log(
            "read_governance_file",
            {"filename": filename},
            "reading",
            status="OK",
        )
        if not path.exists():
            return f"Error: {filename} not found at project root."
        return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Shared feature contract pack tools (backend -> frontend handoff)
# ---------------------------------------------------------------------------


def _normalize_contract_task_id(task_id: str) -> str:
    normalized = (task_id or "").strip().upper()
    if not _TASK_ID_PATTERN.match(normalized):
        raise ValueError(
            "invalid task_id format. Expected pattern like 'B11', 'WEB4', 'APP19'."
        )
    return normalized


def _render_contract_markdown(pack: dict[str, object]) -> str:
    task_id = str(pack.get("task_id", "")).strip().upper()
    feature_name = str(pack.get("feature_name", "")).strip()
    summary = str(pack.get("summary", "")).strip()
    generated_at = str(pack.get("generated_at", "")).strip()
    rest_endpoints = pack.get("rest_endpoints", [])
    graphql_endpoints = pack.get("graphql_endpoints", [])
    auth = str(pack.get("auth", "")).strip()
    errors = pack.get("error_contract", [])
    examples = pack.get("examples", [])
    notes = str(pack.get("notes", "")).strip()

    lines: list[str] = [
        f"# Feature Contract Pack — {task_id}",
        "",
        f"- Feature: {feature_name or 'n/a'}",
        f"- Generated at (UTC): {generated_at or 'n/a'}",
        f"- Producer repo: {TARGET_REPO_NAME}",
    ]
    if summary:
        lines.extend(["", "## Summary", "", summary])

    lines.extend(["", "## Auth", "", auth or "n/a"])

    lines.extend(["", "## REST Endpoints", ""])
    if isinstance(rest_endpoints, list) and rest_endpoints:
        for endpoint in rest_endpoints:
            if not isinstance(endpoint, dict):
                continue
            method = str(endpoint.get("method", "")).upper()
            path = str(endpoint.get("path", ""))
            description = str(endpoint.get("description", ""))
            lines.append(f"- `{method} {path}` — {description}".rstrip())
    else:
        lines.append("- none")

    lines.extend(["", "## GraphQL Endpoints", ""])
    if isinstance(graphql_endpoints, list) and graphql_endpoints:
        for endpoint in graphql_endpoints:
            if not isinstance(endpoint, dict):
                continue
            name = str(endpoint.get("name", ""))
            endpoint_type = str(endpoint.get("type", ""))
            description = str(endpoint.get("description", ""))
            lines.append(f"- `{endpoint_type}:{name}` — {description}".rstrip())
    else:
        lines.append("- none")

    lines.extend(["", "## Error Contract", ""])
    if isinstance(errors, list) and errors:
        for error in errors:
            lines.append(f"- {error}")
    else:
        lines.append("- n/a")

    lines.extend(["", "## Request/Response Examples", ""])
    if isinstance(examples, list) and examples:
        for index, example in enumerate(examples, start=1):
            lines.append(f"- Example {index}: {example}")
    else:
        lines.append("- n/a")

    if notes:
        lines.extend(["", "## Notes", "", notes])

    return "\n".join(lines).strip() + "\n"


class PublishFeatureContractPackTool(BaseTool):
    name: str = "publish_feature_contract_pack"
    description: str = (
        "Publishes a backend->frontend handoff contract pack in the shared "
        "platform directory `.context/feature_contracts/`.\n"
        "Use this at the end of backend feature delivery.\n"
        "Arguments:\n"
        "- task_id: backlog task id (e.g., B11)\n"
        "- feature_name: short feature title\n"
        "- summary: functional summary for frontend agents\n"
        "- payload_json: JSON object string with keys: rest_endpoints, "
        "graphql_endpoints, auth, error_contract, examples, notes\n"
    )

    def _run(
        self,
        task_id: str,
        feature_name: str,
        summary: str,
        payload_json: str,
    ) -> str:
        if TARGET_REPO_NAME != "auraxis-api":
            msg = (
                "BLOCKED: publish_feature_contract_pack is allowed only for "
                "auraxis-api runs."
            )
            audit_log(
                "publish_feature_contract_pack",
                {"task_id": task_id},
                msg,
                status="BLOCKED",
            )
            return msg

        try:
            normalized_task_id = _normalize_contract_task_id(task_id)
        except ValueError as error:
            msg = f"Error: {error}"
            audit_log(
                "publish_feature_contract_pack",
                {"task_id": task_id},
                msg,
                status="ERROR",
            )
            return msg

        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as error:
            msg = f"Error: payload_json is not valid JSON ({error})"
            audit_log(
                "publish_feature_contract_pack",
                {"task_id": normalized_task_id},
                msg,
                status="ERROR",
            )
            return msg

        if not isinstance(payload, dict):
            msg = "Error: payload_json must be a JSON object."
            audit_log(
                "publish_feature_contract_pack",
                {"task_id": normalized_task_id},
                msg,
                status="ERROR",
            )
            return msg

        pack = {
            "task_id": normalized_task_id,
            "feature_name": feature_name.strip(),
            "summary": summary.strip(),
            "generated_at": datetime.now(UTC).isoformat(),
            "producer_repo": TARGET_REPO_NAME,
            "rest_endpoints": payload.get("rest_endpoints", []),
            "graphql_endpoints": payload.get("graphql_endpoints", []),
            "auth": payload.get("auth", ""),
            "error_contract": payload.get("error_contract", []),
            "examples": payload.get("examples", []),
            "notes": payload.get("notes", ""),
        }

        SHARED_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
        json_path = validate_shared_contract_path(f"{normalized_task_id}.json")
        md_path = validate_shared_contract_path(f"{normalized_task_id}.md")

        json_path.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_render_contract_markdown(pack), encoding="utf-8")

        result = (
            "Feature contract pack published:\n"
            f"- {json_path}\n"
            f"- {md_path}"
        )
        audit_log(
            "publish_feature_contract_pack",
            {"task_id": normalized_task_id, "feature_name": feature_name},
            result,
            status="OK",
        )
        return result


class ListFeatureContractPacksTool(BaseTool):
    name: str = "list_feature_contract_packs"
    description: str = (
        "Lists available shared feature contract packs published by backend "
        "agents under `.context/feature_contracts`."
    )

    def _run(self, query: str = None) -> str:
        SHARED_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(
            (path for path in SHARED_CONTRACTS_DIR.glob("*.json")),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not files:
            result = "No feature contract packs found."
            audit_log("list_feature_contract_packs", {}, result, status="OK")
            return result

        lines = ["Available feature contract packs (newest first):"]
        for file_path in files[:30]:
            lines.append(f"- {file_path.stem}")
        result = "\n".join(lines)
        audit_log(
            "list_feature_contract_packs",
            {"count": len(files)},
            result[:200],
            status="OK",
        )
        return result


class ReadFeatureContractPackTool(BaseTool):
    name: str = "read_feature_contract_pack"
    description: str = (
        "Reads a shared feature contract pack by task ID. "
        "Parameters: task_id (e.g., B11), format ('json'|'md', default 'md')."
    )

    def _run(self, task_id: str, format: str = "md") -> str:
        try:
            normalized_task_id = _normalize_contract_task_id(task_id)
        except ValueError as error:
            msg = f"Error: {error}"
            audit_log(
                "read_feature_contract_pack",
                {"task_id": task_id},
                msg,
                status="ERROR",
            )
            return msg

        target_format = format.strip().lower()
        if target_format not in {"json", "md"}:
            msg = "Error: format must be 'json' or 'md'."
            audit_log(
                "read_feature_contract_pack",
                {"task_id": normalized_task_id, "format": format},
                msg,
                status="ERROR",
            )
            return msg

        path = validate_shared_contract_path(f"{normalized_task_id}.{target_format}")
        if not path.exists():
            msg = (
                f"Error: contract pack not found for {normalized_task_id} "
                f"({target_format})."
            )
            audit_log(
                "read_feature_contract_pack",
                {"task_id": normalized_task_id, "format": target_format},
                msg,
                status="ERROR",
            )
            return msg

        result = path.read_text(encoding="utf-8")
        audit_log(
            "read_feature_contract_pack",
            {"task_id": normalized_task_id, "format": target_format},
            "read",
            status="OK",
        )
        return result


# ---------------------------------------------------------------------------
# Execution tools
# ---------------------------------------------------------------------------


class RunTestsTool(BaseTool):
    name: str = "run_backend_tests"
    description: str = (
        "Runs the pytest test suite with timeout protection. "
        "Returns stdout and stderr."
    )

    def _run(self, query: str = None) -> str:
        pytest_path = str(PROJECT_ROOT / ".venv" / "bin" / "pytest")
        import os

        if not os.path.exists(pytest_path):
            pytest_path = "pytest"

        result = safe_subprocess(
            [pytest_path, "--tb=short", "-q"],
            timeout=300,
            cwd=str(PROJECT_ROOT),
        )
        output = f"STDOUT: {result['stdout']}\nSTDERR: {result['stderr']}"
        audit_log(
            "run_backend_tests",
            {"pytest_path": pytest_path},
            output[:200],
            status="OK" if result["returncode"] == 0 else "ERROR",
        )
        return output


class RunRepoQualityGatesTool(BaseTool):
    name: str = "run_repo_quality_gates"
    description: str = (
        "Runs the canonical quality gates for the target repository.\n"
        "- auraxis-api: pytest --tb=short -q\n"
        "- auraxis-web: pnpm quality-check\n"
        "- auraxis-app: npm run quality-check\n"
        "Returns stdout/stderr and command used."
    )

    def _run(self, query: str = None) -> str:
        repo_name = PROJECT_ROOT.name
        command: list[str]
        if repo_name == "auraxis-web":
            command = ["pnpm", "quality-check"]
        elif repo_name == "auraxis-app":
            command = ["npm", "run", "quality-check"]
        else:
            pytest_path = str(PROJECT_ROOT / ".venv" / "bin" / "pytest")
            import os

            if not os.path.exists(pytest_path):
                pytest_path = "pytest"
            command = [pytest_path, "--tb=short", "-q"]

        result = safe_subprocess(
            command,
            timeout=600,
            cwd=str(PROJECT_ROOT),
        )
        output = (
            f"COMMAND: {' '.join(command)}\n"
            f"RETURN_CODE: {result['returncode']}\n"
            f"STDOUT:\n{result['stdout']}\n"
            f"STDERR:\n{result['stderr']}"
        )
        audit_log(
            "run_repo_quality_gates",
            {"repo": repo_name, "command": command},
            output[:200],
            status="OK" if result["returncode"] == 0 else "ERROR",
        )
        return output


# ---------------------------------------------------------------------------
# Integration test tool — E2E testing with real HTTP requests
#
# The IntegrationTestTool invokes a standalone Python script
# (integration_test_runner.py) using the PROJECT venv (which has Flask),
# not the ai_squad venv (which has CrewAI). This avoids dependency
# conflicts between the two environments.
# ---------------------------------------------------------------------------


class IntegrationTestTool(BaseTool):
    name: str = "run_integration_tests"
    description: str = (
        "Runs integration tests using REAL HTTP requests against the Flask app. "
        "Spins up a temporary Flask app with SQLite, makes actual API calls "
        "(register, login, CRUD), and verifies responses. "
        "Like Cypress for backend — tests the full stack end-to-end.\n\n"
        "Available scenarios:\n"
        "- 'register_and_login': Register user + login + verify token\n"
        "- 'update_profile': Register + login + update profile fields\n"
        "- 'full_crud': Register + login + update profile + read /me + verify data\n\n"
        "Returns PASS/FAIL with step-by-step results."
    )

    def _run(self, scenario: str = "full_crud") -> str:
        import json
        import os

        valid_scenarios = ("register_and_login", "update_profile", "full_crud")
        if scenario not in valid_scenarios:
            return (
                f"Invalid scenario '{scenario}'. "
                f"Valid: {', '.join(valid_scenarios)}"
            )

        # Locate the project venv Python (not the ai_squad venv)
        project_python = str(PROJECT_ROOT / ".venv" / "bin" / "python")
        if not os.path.exists(project_python):
            project_python = "python"

        # Locate the runner script
        runner_script = str(
            Path(__file__).resolve().parent / "integration_test_runner.py"
        )

        result = safe_subprocess(
            [project_python, runner_script, scenario],
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )

        # Parse JSON output from the runner
        try:
            data = json.loads(result["stdout"].strip())
        except (json.JSONDecodeError, ValueError):
            msg = (
                f"EXECUTION FAILED: Could not parse runner output.\n"
                f"STDOUT: {result['stdout'][:500]}\n"
                f"STDERR: {result['stderr'][:500]}"
            )
            audit_log(
                "run_integration_tests",
                {"scenario": scenario},
                msg[:200],
                status="ERROR",
            )
            return msg

        # Format output
        lines = [
            f"# Integration Test Results — Scenario: {scenario}",
            f"Overall: {'PASS' if data['passed'] else 'FAIL'}",
            "",
            "Steps:",
        ]
        for step in data.get("steps", []):
            status = "PASS" if step.get("passed") else "FAIL"
            lines.append(
                f"  [{status}] {step.get('action', '?')} "
                f"-> HTTP {step.get('status', '?')}"
            )

        if data.get("errors"):
            lines.append("")
            lines.append("Errors:")
            for err in data["errors"]:
                lines.append(f"  - {err}")

        output = "\n".join(lines)
        audit_log(
            "run_integration_tests",
            {"scenario": scenario},
            output[:200],
            status="OK" if data["passed"] else "ERROR",
        )
        return output


# ---------------------------------------------------------------------------
# Documentation tool — auto-update TASKS.md
# ---------------------------------------------------------------------------


def _parse_task_row(line: str) -> dict | None:
    """Parse a TASKS.md table row into a dict of columns."""
    if not line.startswith("|"):
        return None
    cells = [c.strip() for c in line.split("|")]
    # cells[0] is empty (before first |), cells[-1] is empty (after last |)
    cells = cells[1:-1]
    if len(cells) < 8:
        return None
    return {
        "id": cells[0].strip(),
        "area": cells[1].strip(),
        "tarefa": cells[2].strip(),
        "status": cells[3].strip(),
        "progresso": cells[4].strip(),
        "risco": cells[5].strip(),
        "commit": cells[6].strip(),
        "data": cells[7].strip(),
        "raw_cells": cells,
    }


def _rebuild_task_row(cells: list[str]) -> str:
    """Rebuild a TASKS.md table row from a list of cell values."""
    return "| " + " | ".join(cells) + " |"


def _status_to_check_marker(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in ("done", "completed"):
        return "x"
    if normalized in ("in progress", "in_progress", "progress"):
        return "~"
    if normalized in ("blocked", "block"):
        return "!"
    return " "


def _update_checklist_task_line(line: str, task_id: str, status: str) -> tuple[str, bool]:
    """Update checklist marker for a specific task ID line."""
    marker = _status_to_check_marker(status)
    pattern = re.compile(
        rf"^(\s*-\s*\[)([ x~!])(\]\s+\*\*{re.escape(task_id)}\b.*)$"
    )
    match = pattern.match(line)
    if not match:
        return line, False
    return f"{match.group(1)}{marker}{match.group(3)}", True


class UpdateTaskStatusTool(BaseTool):
    name: str = "update_task_status"
    description: str = (
        "Updates a task in TASKS.md to mark it as Done with commit hash.\n\n"
        "Parameters:\n"
        "- task_id: The task ID (e.g., 'B8', 'B9')\n"
        "- status: New status ('Done', 'In Progress', 'Todo', 'Blocked')\n"
        "- progress: Progress percentage (e.g., '100%')\n"
        "- commit_hash: Git commit hash(es) to record for traceability\n\n"
        "This tool reads TASKS.md, finds the row matching task_id, "
        "updates status/progress/commit/date, and writes back.\n"
        "It also updates the 'Ultima atualizacao' header date."
    )

    def _run(
        self,
        task_id: str,
        status: str = "Done",
        progress: str = "100%",
        commit_hash: str = "",
    ) -> str:
        import os
        import re
        from datetime import date

        expected_task_id = os.getenv("AURAXIS_RESOLVED_TASK_ID", "").strip().upper()
        normalized_task_id = (task_id or "").strip().upper()
        if expected_task_id and normalized_task_id != expected_task_id:
            msg = (
                f"BLOCKED: task_id drift detected. "
                f"Expected '{expected_task_id}' but got '{normalized_task_id}'."
            )
            audit_log(
                "update_task_status",
                {"task_id": task_id, "expected_task_id": expected_task_id},
                msg,
                status="ERROR",
            )
            return msg

        tasks_path = _resolve_tasks_file()
        if not tasks_path.exists():
            return "Error: tasks file not found."

        content = tasks_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Find table row format (backend TASKS.md)
        updated = False
        for i, line in enumerate(lines):
            if not line.startswith("|"):
                continue
            parsed = _parse_task_row(line)
            if not parsed or parsed["id"] != task_id:
                continue

            # Update the fields
            cells = parsed["raw_cells"]
            cells[3] = f" {status} "  # Status column
            cells[4] = f" {progress} "  # Progress column
            if commit_hash:
                cells[6] = f" {commit_hash} "  # Commit column
            cells[7] = f" {date.today().isoformat()} "  # Date column

            lines[i] = _rebuild_task_row(cells)
            updated = True
            break

        # Fallback: checklist format (app/web tasks.md)
        if not updated:
            for i, line in enumerate(lines):
                new_line, line_updated = _update_checklist_task_line(
                    line=line,
                    task_id=task_id,
                    status=status,
                )
                if line_updated:
                    lines[i] = new_line
                    updated = True
                    break

        if not updated:
            msg = f"Task '{task_id}' not found in {tasks_path.name}."
            audit_log(
                "update_task_status",
                {"task_id": task_id},
                msg,
                status="ERROR",
            )
            return msg

        # Update the header date
        today_str = date.today().isoformat()
        for i, line in enumerate(lines):
            if line.startswith("Ultima atualizacao:"):
                lines[i] = re.sub(
                    r"Ultima atualizacao: [\d-]+",
                    f"Ultima atualizacao: {today_str}",
                    line,
                )
                break
            if line.startswith("Última atualização:"):
                lines[i] = re.sub(
                    r"Última atualização: [\d-]+",
                    f"Última atualização: {today_str}",
                    line,
                )
                break

        # Write back — tasks file is in project root, use direct write
        # (not validate_write_path since TASKS.md is not in a writable dir)
        tasks_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        msg = (
            f"{tasks_path.name} updated: {task_id} → "
            f"Status={status}, Progress={progress}, "
            f"Commit={commit_hash or 'n/a'}, Date={today_str}"
        )
        audit_log(
            "update_task_status",
            {"task_id": task_id, "status": status, "commit": commit_hash},
            msg,
            status="OK",
        )
        return msg


# ---------------------------------------------------------------------------
# Write tools
# ---------------------------------------------------------------------------

_FRONTEND_SOURCE_EXTENSIONS = {
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
}

_FRONTEND_TS_ONLY_BLOCKED_EXTENSIONS = {".js", ".jsx"}

_WEB_RAW_HTML_TAG_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"<\s*p\b", re.IGNORECASE),
    re.compile(r"<\s*input\b", re.IGNORECASE),
    re.compile(r"<\s*label\b", re.IGNORECASE),
    re.compile(r"<\s*textarea\b", re.IGNORECASE),
    re.compile(r"<\s*select\b", re.IGNORECASE),
    re.compile(r"<\s*button\b", re.IGNORECASE),
)

_MISSING_RETURN_TYPE_FUNCTION_DECL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+[A-Za-z_]\w*\s*\([^)]*\)\s*\{"
)
_MISSING_RETURN_TYPE_ARROW_RE = re.compile(
    r"^\s*(?:export\s+)?const\s+[A-Za-z_]\w*\s*=\s*(?:async\s+)?\([^)]*\)\s*=>"
)
_MISSING_RETURN_TYPE_ARROW_SINGLE_ARG_RE = re.compile(
    r"^\s*(?:export\s+)?const\s+[A-Za-z_]\w*\s*=\s*(?:async\s+)?[A-Za-z_]\w*\s*=>"
)

_WEB_TOKEN_POLICY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bfont-size\s*:\s*[0-9.]+(?:px|rem|em)\b", re.IGNORECASE),
    re.compile(r"\bfont-weight\s*:\s*[1-9]00\b", re.IGNORECASE),
    re.compile(r"\bborder-radius\s*:\s*[0-9.]+(?:px|rem|em)\b", re.IGNORECASE),
    re.compile(r"\b(?:padding|margin|gap)[-\w]*\s*:\s*[0-9.]+(?:px|rem|em)\b", re.IGNORECASE),
    re.compile(r"\bborder(?:-(?:top|right|bottom|left))?\s*:\s*[0-9.]+px\b", re.IGNORECASE),
    re.compile(r"\b(?:color|background(?:-color)?|border-color)\s*:\s*#[0-9a-fA-F]{3,8}\b", re.IGNORECASE),
)

_APP_TOKEN_POLICY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bfontSize\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\bfontWeight\s*:\s*['\"]?[1-9]00['\"]?\b"),
    re.compile(r"\blineHeight\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\bborderRadius\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\bborderWidth\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\b(?:padding|paddingTop|paddingBottom|paddingLeft|paddingRight|paddingHorizontal|paddingVertical)\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\b(?:margin|marginTop|marginBottom|marginLeft|marginRight|marginHorizontal|marginVertical)\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\bgap\s*:\s*\d+(?:\.\d+)?\b"),
    re.compile(r"\b(?:color|backgroundColor|borderColor)\s*:\s*['\"]#[0-9a-fA-F]{3,8}['\"]\b"),
)


def _is_theme_or_token_file(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    token_indicators = (
        "/theme/",
        "/tokens/",
        "design-tokens",
        "styles/variables",
        "styles/theme",
        "theme.ts",
        "theme.js",
        "theme.css",
        "tokens.ts",
        "tokens.js",
        "tokens.css",
    )
    return any(indicator in normalized for indicator in token_indicators)


def _is_frontend_source_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip().lower()
    if TARGET_REPO_NAME == "auraxis-web":
        prefixes = (
            "app/",
            "components/",
            "composables/",
            "layouts/",
            "pages/",
            "plugins/",
            "stores/",
            "shared/",
            "types/",
            "utils/",
            "services/",
        )
    elif TARGET_REPO_NAME == "auraxis-app":
        prefixes = (
            "app/",
            "src/",
            "components/",
            "hooks/",
            "providers/",
            "store/",
            "stores/",
            "shared/",
            "types/",
            "utils/",
            "services/",
            "config/",
        )
    else:
        return False
    return normalized.startswith(prefixes)


def _has_jsdoc_block(lines: list[str], line_index: int) -> bool:
    cursor = line_index - 1
    while cursor >= 0 and not lines[cursor].strip():
        cursor -= 1
    if cursor < 0:
        return False
    if lines[cursor].strip().startswith("/**") and lines[cursor].strip().endswith("*/"):
        return True
    if not lines[cursor].strip().endswith("*/"):
        return False
    while cursor >= 0:
        stripped = lines[cursor].strip()
        if stripped.startswith("/**"):
            return True
        if stripped.startswith("/*") and not stripped.startswith("/**"):
            return False
        cursor -= 1
    return False


def _detect_frontend_language_policy_violation(path: str, content: str) -> str | None:
    if TARGET_REPO_NAME not in {"auraxis-web", "auraxis-app"}:
        return None
    if not _is_frontend_source_path(path):
        return None

    suffix = Path(path).suffix.lower()

    if suffix in _FRONTEND_TS_ONLY_BLOCKED_EXTENSIONS:
        return (
            "BLOCKED: JavaScript source files are forbidden in frontend code. "
            "Use TypeScript only (`.ts`/`.tsx`)."
        )

    violations: list[str] = []
    lines = content.splitlines()

    if TARGET_REPO_NAME == "auraxis-web" and suffix == ".vue":
        for line_no, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            for pattern in _WEB_RAW_HTML_TAG_PATTERNS:
                if pattern.search(stripped):
                    violations.append(
                        f"L{line_no}: raw HTML tag found (`{stripped[:120]}`)"
                    )
                    break

    if suffix in {".ts", ".tsx", ".vue"} and not _is_theme_or_token_file(path):
        for index, raw_line in enumerate(lines):
            stripped = raw_line.strip()
            if (
                not stripped
                or stripped.startswith("//")
                or stripped.startswith("*")
                or stripped.startswith("/*")
            ):
                continue

            missing_return_type = (
                _MISSING_RETURN_TYPE_FUNCTION_DECL_RE.match(stripped)
                or _MISSING_RETURN_TYPE_ARROW_RE.match(stripped)
                or _MISSING_RETURN_TYPE_ARROW_SINGLE_ARG_RE.match(stripped)
            )
            if missing_return_type:
                line_no = index + 1
                violations.append(
                    f"L{line_no}: function without explicit return type (`{stripped[:120]}`)"
                )
                continue

            has_function_signature = (
                "function " in stripped
                or "=> {" in stripped
                or stripped.endswith("=>")
            )
            if has_function_signature and not _has_jsdoc_block(lines, index):
                if re.search(r"\bfunction\b", stripped) or re.search(
                    r"\bconst\s+[A-Za-z_]\w+\b", stripped
                ):
                    line_no = index + 1
                    violations.append(
                        f"L{line_no}: missing JSDoc block for function (`{stripped[:120]}`)"
                    )

    if not violations:
        return None

    preview = "\n".join(f"- {item}" for item in violations[:8])
    return (
        "BLOCKED: frontend language/component policy violation detected.\n"
        "- TypeScript-only frontend source (`.ts`/`.tsx`).\n"
        "- Explicit function return types (no implicit inference).\n"
        "- JSDoc required for every function.\n"
        "- Web templates must use Chakra UI components (no raw HTML controls).\n"
        f"Detected lines:\n{preview}"
    )


def _detect_frontend_token_policy_violation(path: str, content: str) -> str | None:
    if TARGET_REPO_NAME not in {"auraxis-web", "auraxis-app"}:
        return None

    suffix = Path(path).suffix.lower()
    if suffix not in _FRONTEND_SOURCE_EXTENSIONS:
        return None

    if _is_theme_or_token_file(path):
        return None

    patterns = (
        _WEB_TOKEN_POLICY_PATTERNS
        if TARGET_REPO_NAME == "auraxis-web"
        else _APP_TOKEN_POLICY_PATTERNS
    )
    violations: list[str] = []
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            continue
        for pattern in patterns:
            if pattern.search(line):
                violations.append(f"L{line_no}: {line[:140]}")
                break

    if not violations:
        return None

    preview = "\n".join(f"- {item}" for item in violations[:5])
    return (
        "BLOCKED: front-end token policy violation detected.\n"
        "Use theme/tokens and UI-library props (Chakra UI / RN Paper) instead of raw style literals.\n"
        "Allowed exception: files under theme/tokens for token definition.\n"
        f"Detected lines:\n{preview}"
    )


def _detect_encoding_corruption(existing_path: Path, new_content: str) -> str | None:
    """Detect if a write would corrupt non-ASCII characters.

    Compares non-ASCII characters in the existing file vs the new content.
    If the existing file has accented characters (e.g., Portuguese) but
    the new content has significantly fewer, the LLM likely corrupted them.

    Returns a warning message if corruption is detected, None if safe.
    """
    if not existing_path.exists():
        return None

    try:
        old_content = existing_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    old_non_ascii = sum(1 for ch in old_content if ord(ch) > 127)
    new_non_ascii = sum(1 for ch in new_content if ord(ch) > 127)

    # If old file had accented chars and new content lost >50% of them
    if old_non_ascii > 5 and new_non_ascii < old_non_ascii * 0.5:
        return (
            f"BLOCKED: encoding corruption detected. "
            f"Existing file has {old_non_ascii} non-ASCII chars "
            f"(accents, special chars) but new content has only "
            f"{new_non_ascii}. The LLM likely corrupted accented "
            f"characters. To fix: read the file again and preserve "
            f"ALL original characters exactly as they are."
        )
    return None


class WriteFileTool(BaseTool):
    name: str = "write_file_content"
    description: str = (
        "Writes content to a file. Path must be relative to project root. "
        "Enforces security: only writable dirs, no protected files, "
        "no blocked extensions. "
        "IMPORTANT: This tool will BLOCK writes that corrupt non-ASCII "
        "characters (accents like ã, é, ç, ô). If blocked, re-read the "
        "original file and preserve all characters exactly."
    )

    def _run(self, path: str, content: str) -> str:
        try:
            validated = validate_write_path(path)
        except PermissionError as e:
            msg = f"BLOCKED: {e}"
            audit_log(
                "write_file_content",
                {"path": path},
                msg,
                status="BLOCKED",
            )
            return msg

        language_policy_msg = _detect_frontend_language_policy_violation(path, content)
        if language_policy_msg:
            audit_log(
                "write_file_content",
                {"path": path},
                language_policy_msg,
                status="BLOCKED",
            )
            return language_policy_msg

        token_policy_msg = _detect_frontend_token_policy_violation(path, content)
        if token_policy_msg:
            audit_log(
                "write_file_content",
                {"path": path},
                token_policy_msg,
                status="BLOCKED",
            )
            return token_policy_msg

        # Guard: detect encoding corruption before writing
        corruption_msg = _detect_encoding_corruption(validated, content)
        if corruption_msg:
            audit_log(
                "write_file_content",
                {"path": path},
                corruption_msg,
                status="BLOCKED",
            )
            return corruption_msg

        validated.parent.mkdir(parents=True, exist_ok=True)
        validated.write_text(content, encoding="utf-8")

        msg = f"File {path} written successfully."
        audit_log(
            "write_file_content",
            {"path": path, "size": len(content)},
            msg,
            status="OK",
        )
        return msg


# ---------------------------------------------------------------------------
# Infrastructure tools
# ---------------------------------------------------------------------------


class AWSStatusTool(BaseTool):
    name: str = "check_aws_status"
    description: str = "Checks basic AWS EC2 infrastructure status (read-only)."

    def _run(self, query: str = None) -> str:
        result = safe_subprocess(
            [
                "aws",
                "ec2",
                "describe-instances",
                "--query",
                "Reservations[*].Instances[*]."
                "[InstanceId,State.Name,PublicIpAddress]",
            ],
            timeout=30,
        )
        output = f"AWS Status: {result['stdout']}"
        audit_log(
            "check_aws_status",
            {},
            output[:200],
            status="OK" if result["returncode"] == 0 else "ERROR",
        )
        return output


# ---------------------------------------------------------------------------
# Git tools — extracted helpers to keep cyclomatic complexity low.
# ---------------------------------------------------------------------------


def _git_create_branch(branch_name: str) -> str:
    """Create a branch with conventional prefix validation."""
    if not branch_name:
        return "Error: branch_name is required."

    if not branch_name.startswith(CONVENTIONAL_BRANCH_PREFIXES):
        allowed = ", ".join(CONVENTIONAL_BRANCH_PREFIXES)
        return (
            f"BLOCKED: Branch '{branch_name}' does not use a conventional "
            f"prefix. Allowed prefixes: {allowed}"
        )

    expected_task_id = os.getenv("AURAXIS_RESOLVED_TASK_ID", "").strip().upper()
    normalized_branch = branch_name.upper()
    if expected_task_id and expected_task_id not in normalized_branch:
        return (
            "BLOCKED: branch/task drift detected. "
            f"Branch '{branch_name}' must contain task ID '{expected_task_id}'."
        )

    result = safe_subprocess(["git", "checkout", "-b", branch_name], timeout=15)
    if result["returncode"] != 0:
        return f"Error creating branch: {result['stderr']}"
    return f"Branch '{branch_name}' created."


def _git_collect_changed_files() -> list[str]:
    """Get list of changed files (staged + unstaged + untracked)."""
    # Staged and modified
    diff_result = safe_subprocess(["git", "diff", "--name-only", "HEAD"], timeout=15)
    # Untracked
    untracked_result = safe_subprocess(
        ["git", "ls-files", "--others", "--exclude-standard"], timeout=15
    )

    files: list[str] = []
    for output in [diff_result["stdout"], untracked_result["stdout"]]:
        files.extend(line.strip() for line in output.splitlines() if line.strip())
    return list(set(files))


def _git_filter_safe_files(files: list[str]) -> list[str]:
    """Filter files against GIT_STAGE_BLOCKLIST using fnmatch."""
    safe_files: list[str] = []
    for f in files:
        blocked = any(fnmatch.fnmatch(f, pattern) for pattern in GIT_STAGE_BLOCKLIST)
        if not blocked:
            safe_files.append(f)
    return safe_files


def _git_commit(message: str) -> str:
    """Selective staging + commit. Never uses 'git add .'."""
    # Detect current branch — block commits to master/main
    branch_result = safe_subprocess(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=10
    )
    current_branch = branch_result["stdout"].strip()
    if current_branch in ("master", "main"):
        return (
            "BLOCKED: Direct commits to 'master'/'main' are not allowed. "
            "Create a feature branch first."
        )

    if not message:
        return "Error: commit message is required."

    changed = _git_collect_changed_files()
    if not changed:
        return "Nothing to commit — no changed files detected."

    safe = _git_filter_safe_files(changed)
    if not safe:
        blocked_count = len(changed)
        return (
            f"Nothing to commit — all {blocked_count} changed file(s) "
            f"are in GIT_STAGE_BLOCKLIST."
        )

    # Selective staging (never 'git add .')
    safe_subprocess(["git", "add"] + safe, timeout=DEFAULT_TIMEOUT_SECONDS)

    # Commit (uses DEFAULT_TIMEOUT to accommodate pre-commit hooks)
    result = safe_subprocess(
        ["git", "commit", "-m", message], timeout=DEFAULT_TIMEOUT_SECONDS
    )
    if result["returncode"] != 0:
        return f"Commit error: {result['stderr']}"

    return f"Committed {len(safe)} file(s): {message}\n" f"Staged: {safe}"


def _git_status() -> str:
    """Return git status output."""
    result = safe_subprocess(["git", "status"], timeout=15)
    return result["stdout"]


class GitOpsTool(BaseTool):
    name: str = "git_operations"
    description: str = (
        "Git operations: create_branch (with conventional prefix), "
        "commit (selective staging, blocks master/main), "
        "status. Never uses 'git add .'."
    )

    def _run(
        self,
        command: str,
        branch_name: str = None,
        message: str = None,
    ) -> str:
        if command == "create_branch":
            result = _git_create_branch(branch_name)
        elif command == "commit":
            result = _git_commit(message)
        elif command == "status":
            result = _git_status()
        else:
            result = (
                f"Invalid command: '{command}'. "
                f"Valid commands: create_branch, commit, status."
            )

        audit_log(
            "git_operations",
            {"command": command, "branch_name": branch_name, "message": message},
            result[:200],
            status=("OK" if "blocked" not in result.lower() and "error" not in result.lower() else "ERROR"),
        )
        return result
