"""
Auraxis AI Squad — Workspace Orchestrator (backend workflow enabled).

Pipeline:
  PM (plan) → Dev (read) → Dev (write) → Dev (review) → QA (unit test)
  → QA (integration test) → Dev (documentation) → Dev (contract pack)

The 8-task architecture builds on the 5-task pipeline with three new phases:
  - Task 6 (INTEGRATION TEST): makes REAL HTTP requests against the Flask
    app to verify the feature works end-to-end (like Cypress for backend).
  - Task 7 (DOCUMENTATION): auto-updates TASKS.md with status, progress,
    and commit hash for traceability.
  - Task 8 (CONTRACT PACK): publishes backend->frontend handoff artifacts
    under `.context/feature_contracts/` (md + json).

Previous safeguards (still active):
  - Task 2 (READ): prevents blind overwrites by reading files first.
  - Task 4 (REVIEW): catches migration/model inconsistencies before commit.
  - Migration Decision Rules: teaches agents when to rename vs add columns.
  - Alembic history tool: reveals what columns already exist in the database.
  - Validation tool: machine-checks model vs migration consistency.
  - Timeout fix: uses DEFAULT_TIMEOUT (120s) for git commit (pre-commit hooks).

HOW TO USE:
  Set `AURAXIS_TARGET_REPO` and `AURAXIS_BRIEFING`, then run:
    cd ai_squad && python main.py

BRIEFING TIPS:
  - Reference the task ID explicitly (e.g., "B8", "APP10", "WEB11").
  - Name the exact files to touch — the agent reads them before writing.
  - Describe what to ADD, not what the full file should look like.
  - For renames: say RENAME explicitly, not ADD.

References:
- .context/07_operational_cycle.md — full delivery cycle
- .context/04_architecture_snapshot.md — codebase structure
- ai_squad/AGENT_ARCHITECTURE.md — agent registry and tools
"""

import os
import hashlib
import re
import subprocess
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from tools.task_status import (
    append_ledger_entry,
    get_latest_ledger_entry,
    infer_task_id,
    write_status_entry,
)
from tools.tool_security import (
    PLATFORM_ROOT,
    PROJECT_ROOT,
    SQUAD_ROOT,
    TARGET_REPO_NAME,
    get_tool_audit_snapshot,
    reset_tool_audit_snapshot,
)
from tools.project_tools import (
    GetLatestMigrationTool,
    GitOpsTool,
    IntegrationTestTool,
    ListFeatureContractPacksTool,
    ListProjectFilesTool,
    PublishFeatureContractPackTool,
    ReadAlembicHistoryTool,
    ReadContextFileTool,
    ReadFeatureContractPackTool,
    ReadGovernanceFileTool,
    ReadPendingTasksTool,
    ReadProjectFileTool,
    ReadSchemaTool,
    ReadTasksSectionTool,
    RunTestsTool,
    RunRepoQualityGatesTool,
    UpdateTaskStatusTool,
    ValidateMigrationConsistencyTool,
    WriteFileTool,
)

load_dotenv(dotenv_path=SQUAD_ROOT / ".env")

# =========================================================================
# MIGRATION DECISION RULES — injected into agent backstory/task descriptions
# so LLMs know when to use each Alembic operation.
# =========================================================================
MIGRATION_RULES = (
    "MIGRATION DECISION RULES (memorize these):\n"
    "- NEW column that never existed: op.add_column()\n"
    "- RENAME existing column: op.alter_column(new_column_name=) "
    "or raw op.execute('ALTER TABLE x RENAME COLUMN old TO new'). "
    "NEVER use add_column for a rename — it creates a duplicate.\n"
    "- CHANGE type/nullable of existing column: op.alter_column()\n"
    "- REMOVE column: op.drop_column()\n"
    "- To know which columns ALREADY EXIST: call read_alembic_history(table).\n"
    "- If the briefing says 'rename X to Y', the migration MUST use "
    "ALTER COLUMN RENAME, not add_column + drop_column."
)

_STATUS_LINE_TASK_ID_RE = re.compile(r"^task_id:\s*(.+)$", re.IGNORECASE)
_CHECKLIST_RE = re.compile(r"^\s*-\s*\[(?P<status>[ x~!])\]\s+\*\*(?P<id>[A-Z]+-\d+|[A-Z]+\d+)\*\*")
_TABLE_ID_RE = re.compile(r"^[A-Z]+-\d+$|^[A-Z]+\d+$")
_STATUS_VALUES = {"todo", "in progress", "blocked", "done"}
_COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
_QUALITY_GATE_RETURN_CODE_RE = re.compile(r"return_code:\s*(-?\d+)", re.IGNORECASE)
_CRITICAL_AUDIT_TOOLS = {
    "run_repo_quality_gates",
    "run_backend_tests",
    "run_frontend_tests",
    "run_integration_tests",
    "publish_feature_contract_pack",
    "update_task_status",
}
_POLICY_FINGERPRINT_FILES: tuple[Path, ...] = (
    PLATFORM_ROOT / ".context" / "07_steering_global.md",
    PLATFORM_ROOT / ".context" / "08_agent_contract.md",
    PLATFORM_ROOT / "product.md",
)


def _briefing_hash(briefing: str) -> str:
    return hashlib.sha256((briefing or "").strip().encode("utf-8")).hexdigest()[:16]


def _resolve_orchestration_task_id(briefing: str) -> str:
    explicit = infer_task_id(briefing)
    if explicit != "UNSPECIFIED":
        return explicit
    return f"ORCH-{_briefing_hash(briefing).upper()[:8]}"


def _task_board_path(repo: str) -> Path | None:
    candidates = (
        PLATFORM_ROOT / "repos" / repo / "TASKS.md",
        PLATFORM_ROOT / "repos" / repo / "tasks.md",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _resolve_task_id_for_repo(repo: str, briefing: str) -> str:
    explicit = infer_task_id(briefing)
    if explicit != "UNSPECIFIED":
        return explicit

    board = _task_board_path(repo)
    if board is None:
        return "UNSPECIFIED"

    in_progress: list[str] = []
    todo: list[str] = []
    lines = board.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines:
        checklist = _CHECKLIST_RE.match(line)
        if checklist:
            status = checklist.group("status")
            task_id = checklist.group("id")
            if status == "~":
                in_progress.append(task_id)
            elif status == " ":
                todo.append(task_id)
            continue

        if "|" in line and line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not cells:
                continue
            task_id = cells[0]
            if not _TABLE_ID_RE.match(task_id):
                continue
            normalized_cells = [cell.lower() for cell in cells]
            matched_status = next(
                (value for value in normalized_cells if value in _STATUS_VALUES),
                None,
            )
            if matched_status == "in progress":
                in_progress.append(task_id)
            elif matched_status == "todo":
                todo.append(task_id)

    if in_progress:
        return in_progress[0]
    if todo:
        return todo[0]
    return "UNSPECIFIED"


def _compute_policy_fingerprint() -> str:
    digest = hashlib.sha256()
    for file_path in _POLICY_FINGERPRINT_FILES:
        if not file_path.exists():
            continue
        digest.update(file_path.read_bytes())
    return digest.hexdigest()[:16]


def _validate_policy_fingerprint(expected_fingerprint: str) -> tuple[bool, str]:
    expected = (expected_fingerprint or "").strip().lower()
    if not expected:
        return True, ""
    current = _compute_policy_fingerprint().lower()
    if current == expected:
        return True, current
    msg = (
        "policy fingerprint drift detected. "
        f"expected={expected}, current={current}. "
        "Re-run orchestration after syncing context files."
    )
    return False, msg


def _check_repo_worktree_clean(repo: str) -> tuple[bool, str]:
    repo_root = PLATFORM_ROOT / "repos" / repo
    if not repo_root.exists():
        return False, f"repository path not found: {repo_root}"

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        return False, f"unable to inspect worktree: {message}"

    dirty_entries = [line for line in result.stdout.splitlines() if line.strip()]
    if not dirty_entries:
        return True, ""

    preview = "\n".join(dirty_entries[:20])
    return False, (
        "repository has uncommitted changes. "
        "Clean the worktree before autonomous run.\n"
        f"{preview}"
    )


def _resolve_default_branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    candidate = result.stdout.strip().replace("origin/", "")
    if candidate:
        return candidate

    for fallback in ("main", "master"):
        check = subprocess.run(
            ["git", "show-ref", "--verify", f"refs/remotes/origin/{fallback}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if check.returncode == 0:
            return fallback

    return "main"


def _create_execution_worktree(repo: str) -> tuple[Path | None, str]:
    repo_root = PLATFORM_ROOT / "repos" / repo
    if not repo_root.exists():
        return None, f"repository path not found: {repo_root}"

    subprocess.run(
        ["git", "fetch", "origin", "--prune"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    default_branch = _resolve_default_branch(repo_root)
    ref = f"origin/{default_branch}"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    worktree_root = PLATFORM_ROOT / ".tmp" / "agent-worktrees"
    worktree_root.mkdir(parents=True, exist_ok=True)
    worktree_path = worktree_root / f"{repo}-{timestamp}"

    result = subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_path), ref],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown error"
        return None, f"failed to create execution worktree from {ref}: {stderr}"

    source_repo_root = PLATFORM_ROOT / "repos" / repo
    hydration_error = _hydrate_execution_worktree(
        repo=repo,
        source_root=source_repo_root,
        worktree_root=worktree_path,
    )
    if hydration_error:
        _remove_execution_worktree(repo, worktree_path)
        return None, hydration_error

    return worktree_path, ""


def _link_dependency_dir(
    *,
    source_root: Path,
    worktree_root: Path,
    dirname: str,
) -> None:
    source_dir = source_root / dirname
    worktree_dir = worktree_root / dirname
    if not source_dir.exists() or worktree_dir.exists():
        return
    worktree_dir.symlink_to(source_dir, target_is_directory=True)


def _hydrate_execution_worktree(repo: str, source_root: Path, worktree_root: Path) -> str:
    """Attach runtime dependencies to ephemeral worktree when available.

    Worktrees only include tracked files. Runtime dependencies like `.venv`
    and `node_modules` are untracked and therefore absent by default.
    """
    if repo == "auraxis-api":
        try:
            _link_dependency_dir(
                source_root=source_root,
                worktree_root=worktree_root,
                dirname=".venv",
            )
        except OSError as error:
            return f"failed to link backend .venv into worktree: {error}"
        if not (worktree_root / ".venv" / "bin" / "python").exists():
            return (
                "backend runtime prerequisites missing: .venv not available in "
                f"{source_root}. Run project bootstrap first."
            )
        return ""

    if repo in ("auraxis-web", "auraxis-app"):
        try:
            _link_dependency_dir(
                source_root=source_root,
                worktree_root=worktree_root,
                dirname="node_modules",
            )
        except OSError as error:
            return f"failed to link node_modules into worktree: {error}"
        if not (worktree_root / "node_modules").exists():
            return (
                "frontend runtime prerequisites missing: node_modules not available in "
                f"{source_root}. Run dependency install first."
            )
        return ""

    return ""


def _remove_execution_worktree(repo: str, worktree_path: Path) -> None:
    repo_root = PLATFORM_ROOT / "repos" / repo
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree_path)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run(
        ["git", "worktree", "prune"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )


def _rollback_repo_worktree(repo: str) -> None:
    repo_root = PLATFORM_ROOT / "repos" / repo
    subprocess.run(
        ["git", "reset", "--hard", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run(
        ["git", "clean", "-fd"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )


def _rollback_execution_target() -> None:
    explicit_root = os.getenv("AURAXIS_PROJECT_ROOT", "").strip()
    if explicit_root:
        target_root = Path(explicit_root).expanduser().resolve()
    else:
        target_root = PLATFORM_ROOT / "repos" / TARGET_REPO_NAME
    if not target_root.exists():
        return
    subprocess.run(
        ["git", "reset", "--hard", "HEAD"],
        cwd=str(target_root),
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run(
        ["git", "clean", "-fd"],
        cwd=str(target_root),
        capture_output=True,
        text=True,
        check=False,
    )


_QUALITY_GUARD_ENV_KEYS: tuple[str, ...] = (
    "AURAXIS_LAST_FRONTEND_QUALITY_STATUS",
    "AURAXIS_LAST_BACKEND_TESTS_STATUS",
    "AURAXIS_LAST_INTEGRATION_STATUS",
    "AURAXIS_INTEGRATION_REGISTER_AND_LOGIN",
    "AURAXIS_INTEGRATION_FULL_CRUD",
)


def _reset_quality_commit_guard_env(target_env: dict[str, str] | None = None) -> None:
    keys = _QUALITY_GUARD_ENV_KEYS
    if target_env is None:
        for key in keys:
            os.environ.pop(key, None)
        return
    for key in keys:
        target_env.pop(key, None)


def _extract_summary_from_output(
    default_task_id: str,
    stdout_text: str,
    stderr_text: str,
) -> dict[str, object]:
    task_id = default_task_id
    for line in stdout_text.splitlines():
        match = _STATUS_LINE_TASK_ID_RE.match(line.strip())
        if match:
            task_id = match.group(1).strip().upper()
            break

    merged = f"{stdout_text}\n{stderr_text}"
    quality_gate_evidence = "missing"
    branch_guardrail_evidence = "missing"
    hash_candidates: list[str] = []
    for line in merged.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if "tool=run_repo_quality_gates" in lowered:
            status_match = re.search(
                r"tool=run_repo_quality_gates\s*\|\s*status=([a-z]+)",
                stripped,
                re.IGNORECASE,
            )
            return_code_match = _QUALITY_GATE_RETURN_CODE_RE.search(stripped)
            status_label = (
                status_match.group(1).upper() if status_match is not None else "UNKNOWN"
            )
            return_code_label = (
                return_code_match.group(1)
                if return_code_match is not None
                else "unknown"
            )
            quality_gate_evidence = (
                f"status={status_label}, return_code={return_code_label}"
            )
        if "tool=git_operations" in lowered:
            if "branch/task drift detected" in lowered:
                branch_guardrail_evidence = "branch_task_drift_blocked"
            elif (
                "command': 'create_branch'" in lowered
                or 'command": "create_branch"' in lowered
            ) and "status=ok" in lowered:
                branch_guardrail_evidence = "create_branch_ok"
        if (
            "commit" in lowered
            or "committed" in lowered
            or "head is now at" in lowered
            or stripped.startswith("[")
        ):
            hash_candidates.extend(_COMMIT_RE.findall(stripped))

    commit_hashes = sorted(set(hash_candidates))
    if len(commit_hashes) > 10:
        commit_hashes = commit_hashes[-10:]

    merged_lower = merged.lower()
    if "pre-push checks passed" in merged_lower:
        precommit_status = "passed"
    elif "failed" in merged_lower and (
        "pre-commit" in merged_lower
        or "pre-push" in merged_lower
        or "lint" in merged_lower
        or "typecheck" in merged_lower
        or "pytest" in merged_lower
        or "vitest" in merged_lower
        or "jest" in merged_lower
    ):
        precommit_status = "failed"
    else:
        precommit_status = "unknown"

    tech_debt_hints = []
    for line in merged.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        lower = normalized.lower()
        if any(token in lower for token in ("risco residual", "todo", "debt", "pendente")):
            tech_debt_hints.append(normalized)
        if len(tech_debt_hints) >= 5:
            break

    quality_gate_failed = "tool=run_repo_quality_gates | status=error" in merged_lower
    explicit_error_tools = (
        "tool=run_backend_tests | status=error",
        "tool=run_frontend_tests | status=error",
        "tool=run_integration_tests | status=error",
        "tool=run_repo_quality_gates | status=error",
    )
    tool_error_detected = any(marker in merged_lower for marker in explicit_error_tools)

    return {
        "task_id": task_id,
        "commit_hashes": commit_hashes,
        "precommit_status": precommit_status,
        "quality_gate_failed": quality_gate_failed,
        "quality_gate_evidence": quality_gate_evidence,
        "branch_guardrail_evidence": branch_guardrail_evidence,
        "tool_error_detected": tool_error_detected,
        "tech_debt_hints": tech_debt_hints,
    }


def _derive_single_run_status(
    result_text: str,
    *,
    repo_name: str,
    execution_mode: str,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    normalized = result_text.upper()
    if any(marker in normalized for marker in ("FAIL", "ERROR", "BLOCKED", "ISSUES")):
        reasons.append("result_text_markers")

    audit_events = get_tool_audit_snapshot()
    tool_last_status: dict[str, str] = {}
    tool_last_preview: dict[str, str] = {}

    saw_update_task_status_ok = False
    saw_repo_quality_gate_ok = False
    saw_backend_tests_ok = False
    saw_integration_tests_ok = False
    saw_integration_tests_error = False
    saw_contract_pack_ok = False

    for event in audit_events:
        tool = str(event.get("tool", ""))
        status = str(event.get("status", "")).upper()
        preview = str(event.get("result_preview", "")).lower()
        tool_last_status[tool] = status
        tool_last_preview[tool] = preview

        if tool == "update_task_status" and status == "OK":
            saw_update_task_status_ok = True
        if (
            tool == "run_repo_quality_gates"
            and status == "OK"
            and "return_code: 0" in preview
        ):
            saw_repo_quality_gate_ok = True
        if tool == "run_backend_tests" and status == "OK":
            saw_backend_tests_ok = True
        if tool == "run_integration_tests":
            if status == "OK":
                saw_integration_tests_ok = True
            if status == "ERROR":
                saw_integration_tests_error = True
        if tool == "publish_feature_contract_pack" and status == "OK":
            saw_contract_pack_ok = True

    for tool_name in _CRITICAL_AUDIT_TOOLS:
        last_status = tool_last_status.get(tool_name, "")
        if last_status == "ERROR":
            reasons.append(f"audit_error:{tool_name}")

    if (
        tool_last_status.get("run_repo_quality_gates", "") == "ERROR"
        and "return_code: 0" not in tool_last_preview.get("run_repo_quality_gates", "")
    ):
        reasons.append("quality_gate_nonzero")
    if (
        tool_last_status.get("git_operations", "") == "ERROR"
        and "commit error" in tool_last_preview.get("git_operations", "")
    ):
        reasons.append("git_commit_error")

    if execution_mode == "run":
        if not saw_update_task_status_ok:
            reasons.append("missing_task_status_update")
        if repo_name in ("auraxis-web", "auraxis-app") and not saw_repo_quality_gate_ok:
            reasons.append("missing_or_failed_repo_quality_gate")
        if repo_name == "auraxis-api" and not saw_backend_tests_ok:
            reasons.append("missing_or_failed_backend_tests")
        if repo_name == "auraxis-api" and (
            not saw_integration_tests_ok or saw_integration_tests_error
        ):
            reasons.append("missing_or_failed_integration_tests")
        if repo_name == "auraxis-api" and not saw_contract_pack_ok:
            reasons.append("missing_feature_contract_pack")

    deduped = list(dict.fromkeys(reasons))
    return (len(deduped) > 0, deduped)


def _stream_subprocess(
    *,
    repo: str,
    command: list[str],
    env: dict[str, str],
    timeout_seconds: int,
) -> dict[str, object]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    def _drain(stream, bucket: list[str], channel: str) -> None:
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            clean = line.rstrip("\n")
            bucket.append(clean)
            print(f"[{repo}][{channel}] {clean}")
        stream.close()

    stdout_thread = threading.Thread(
        target=_drain,
        args=(process.stdout, stdout_lines, "stdout"),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_drain,
        args=(process.stderr, stderr_lines, "stderr"),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    started_at = monotonic()
    timed_out = False
    try:
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()

    stdout_thread.join(timeout=2)
    stderr_thread.join(timeout=2)
    elapsed = round(monotonic() - started_at, 2)

    return {
        "returncode": 124 if timed_out else process.returncode,
        "timed_out": timed_out,
        "duration_seconds": elapsed,
        "stdout": "\n".join(stdout_lines),
        "stderr": "\n".join(stderr_lines),
    }


class AuraxisSquad:
    def __init__(self):
        # Discovery tools (read-only, no security risk)
        self.rpt = ReadPendingTasksTool()
        self.rts = ReadTasksSectionTool()
        self.rcf = ReadContextFileTool()
        self.rgf = ReadGovernanceFileTool()
        self.rpf = ReadProjectFileTool()
        self.lpf = ListProjectFilesTool()
        self.glm = GetLatestMigrationTool()
        self.rah = ReadAlembicHistoryTool()
        self.rs = ReadSchemaTool()
        self.lfcp = ListFeatureContractPacksTool()
        self.rfcp = ReadFeatureContractPackTool()

        # Validation tools
        self.vmc = ValidateMigrationConsistencyTool()

        # Execution tools
        self.rtst = RunTestsTool()
        self.rqg = RunRepoQualityGatesTool()
        self.rit = IntegrationTestTool()

        # Documentation tools
        self.uts = UpdateTaskStatusTool()
        self.pfcp = PublishFeatureContractPackTool()

        # Write + Git tools
        self.wf = WriteFileTool()
        self.git = GitOpsTool()

    def run_backend_workflow(self, briefing: str, plan_only: bool = False):
        """
        8-task pipeline:
          Plan -> Read -> Write -> Review -> Unit Test
          -> Integration Test -> Documentation -> Contract Pack.

        Task 2 (Read) prevents blind overwrites.
        Task 4 (Review) catches model/migration inconsistencies
        BEFORE committing, so agents self-correct.
        Task 6 (Integration Test) makes real HTTP requests to verify E2E.
        Task 7 (Documentation) auto-updates TASKS.md for traceability.
        Task 8 (Contract Pack) publishes API handoff artifacts for frontend agents.
        """

        # --- AGENTS ---
        manager = Agent(
            role="Gerente de Projeto Auraxis",
            goal=(
                "Produce a CONCRETE implementation plan with exact "
                "file paths, exact code changes, correct migration "
                "operations, and correct migration chain. "
                "Never produce a plan that results in zero code changes."
            ),
            backstory=(
                "Technical lead who reads before planning. "
                "You use read_pending_tasks to see what needs doing, "
                "read_tasks_section to zoom into a task, "
                "read_governance_file for product direction, and "
                "read_alembic_history to check existing DB columns.\n\n"
                + MIGRATION_RULES
            ),
            tools=[
                self.rpt,
                self.rts,
                self.rcf,
                self.rgf,
                self.rah,
                self.rpf,
            ],
            verbose=True,
            allow_delegation=True,
        )

        backend_dev = Agent(
            role="Senior Backend Engineer",
            goal=(
                "Read every existing file before modifying it. "
                "Add new fields/methods to existing code, never replace. "
                "Write complete, working Python following project patterns. "
                "After writing, ALWAYS validate migration consistency."
            ),
            backstory=(
                "Expert in Python, Flask, SQLAlchemy (db.Model style), "
                "Marshmallow, and Graphene (NOT Ariadne). "
                "Your rule: read_project_file BEFORE write_file_content. "
                "You integrate new code into what already exists.\n\n" + MIGRATION_RULES
            ),
            tools=[
                self.rpf,
                self.lpf,
                self.glm,
                self.rah,
                self.rs,
                self.rcf,
                self.vmc,
                self.wf,
                self.git,
                self.uts,
                self.pfcp,
            ],
            verbose=True,
        )

        qa_engineer = Agent(
            role="QA Engineer",
            goal=(
                "Run pytest AND integration tests, report exact "
                "pass/fail counts and coverage. "
                "Flag FAIL if coverage < 85% or any test fails. "
                "Integration tests must verify the feature works "
                "end-to-end with real HTTP requests."
            ),
            backstory=(
                "Rigorous tester who runs the full suite, then "
                "validates with real HTTP requests against a temporary "
                "Flask app (like Cypress for backend). Reports honestly."
            ),
            tools=[self.rtst, self.rit, self.rcf],
            verbose=True,
        )

        # --- TASK 1: PLAN ---
        task_plan = Task(
            description=(
                "BOOTSTRAP (execute in order):\n"
                "1. read_pending_tasks() — focused pending work\n"
                "2. read_tasks_section('<task_id>') — zoom into task\n"
                "3. read_context_file('04_architecture_snapshot.md')\n"
                "4. read_governance_file('product.md')\n"
                "5. read_alembic_history('<table>') — see existing "
                "columns in DB\n\n"
                f'USER BRIEFING: "{briefing}"\n\n'
                "DUPLICATE WORK GUARD (mandatory):\n"
                "After reading the task, CHECK if it is already Done "
                "in TASKS.md or if the code already exists in the "
                "target files. Read the files mentioned in the briefing "
                "using read_project_file. If the task's code is already "
                "present, your plan MUST say: "
                "'ALREADY IMPLEMENTED — no changes needed.' "
                "Do NOT re-implement existing code.\n\n"
                "Produce a CONCRETE plan. Include:\n"
                "- Task ID being implemented\n"
                "- Exact file paths to modify or create\n"
                "- For each file: what to ADD (not replace)\n"
                "- Migration needed? If yes: for EACH column state "
                "the operation: ADD (new), RENAME (existing->new), "
                "ALTER (change type), DROP\n"
                "- Implementation order (dependencies first)\n\n"
                + MIGRATION_RULES
                + "\n\n"
                "CRITICAL: If briefing names a task ID, that task "
                "MUST be implemented UNLESS it is already Done."
            ),
            expected_output=(
                "Numbered list:\n"
                "1. Task ID: <id>\n"
                "2. Already implemented? YES (stop) or NO (continue)\n"
                "3. Files to MODIFY: <path> — <what to add>\n"
                "4. Files to CREATE: <path> — <purpose>\n"
                "5. Migration ops: <column>: <ADD|RENAME|ALTER|DROP>\n"
                "6. Order: <step by step>"
            ),
            agent=manager,
        )

        if plan_only:
            crew = Crew(
                agents=[manager],
                tasks=[task_plan],
                process=Process.sequential,
                verbose=True,
            )
            return crew.kickoff()

        # --- TASK 2: READ (guard against blind overwrites) ---
        task_read = Task(
            description=(
                "READ PHASE — execute before writing anything.\n\n"
                "For every file listed in the plan:\n"
                "1. list_project_files('<dir>') to confirm what exists\n"
                "2. read_project_file('<path>') for FULL current content\n"
                "3. read_schema() to read schema.graphql\n"
                "4. get_latest_migration() for correct down_revision\n"
                "5. read_alembic_history('<table>') for existing columns\n\n"
                "Output a READING REPORT listing:\n"
                "- Each file read: classes, fields, methods found\n"
                "- The latest migration revision ID\n"
                "- Columns that ALREADY EXIST in the database\n"
                "- Conflicts/risks between plan and reality\n"
                "- For each planned migration op, confirm: is this truly "
                "a new column, or does a column with similar name already "
                "exist (suggesting RENAME instead of ADD)?\n\n"
                "DO NOT write any code yet. This task is read-only."
            ),
            expected_output=(
                "Reading report:\n"
                "- File: <path> | Contents: <classes/fields/methods>\n"
                "- Latest migration revision: <id>\n"
                "- Existing DB columns for target table: <list>\n"
                "- Migration op validation: <column>: <confirmed|conflict>\n"
                "- Conflicts/risks: <any issues spotted>"
            ),
            agent=backend_dev,
            context=[task_plan],
        )

        # --- TASK 3: WRITE ---
        task_code = Task(
            description=(
                "WRITE PHASE — implement based on plan + reading report.\n\n"
                "RULES (non-negotiable):\n"
                "1. Use the reading report as your base\n"
                "2. For existing files: take the FULL content you read, "
                "add new fields/methods, write the complete file\n"
                "3. For new files: follow project patterns\n"
                "4. Use db.Model style (NOT declarative Base)\n"
                "5. Use Graphene (NOT Ariadne) for GraphQL\n"
                "6. Set down_revision to revision from reading report\n"
                "7. " + MIGRATION_RULES + "\n"
                "8. After writing ALL files: "
                "git_operations(command='status') to verify\n"
                "9. DO NOT create branch or commit yet — the REVIEW "
                "phase will validate first.\n\n"
                "UTF-8 RULE (critical): This project uses Portuguese. "
                "Files contain accented characters (ã, é, ç, ô, í, ú, "
                "ê, à, ñ). You MUST preserve ALL accented characters "
                "EXACTLY as they appear in the reading report. "
                "Do NOT replace them with ASCII approximations. "
                "The write tool will BLOCK your write if accents are "
                "lost. If blocked, re-read the file and try again.\n\n"
                "NEVER claim a file was written without calling "
                "write_file_content."
            ),
            expected_output=(
                "List of all files written:\n"
                "- <path>: <one-line summary of changes>\n"
                "Git status output showing modified files."
            ),
            agent=backend_dev,
            context=[task_plan, task_read],
        )

        # --- TASK 4: REVIEW (self-check + branch guardrail) ---
        task_review = Task(
            description=(
                "REVIEW PHASE — validate consistency and prepare branch.\n\n"
                "Execute these checks IN ORDER:\n"
                "1. validate_migration_consistency(\n"
                "     model_path='<model file>',\n"
                "     migration_path='<migration file>'\n"
                "   )\n"
                "2. read_project_file('<model file>') — verify all "
                "original fields are still present\n"
                "3. read_project_file('<schema file>') — verify all "
                "original schemas are still present\n"
                "4. read_project_file('<migration file>') — verify "
                "down_revision is correct\n\n"
                "DECISION:\n"
                "- If validate_migration_consistency returns ISSUES: "
                "FIX the files using write_file_content, then re-validate.\n"
                "- If all checks pass: create branch only (NO COMMIT YET).\n"
                "  git_operations(command='create_branch', "
                "branch_name='feat/<task-id>-<description>')\n"
                "  git_operations(command='status')\n\n"
                "Commit is allowed only after unit + integration tests pass.\n\n"
                "This task is the GATEKEEPER. Do not commit if any "
                "check shows ISSUES."
            ),
            expected_output=(
                "Review results:\n"
                "- Migration consistency: CONSISTENT or ISSUES (+ fixes)\n"
                "- Model fields preserved: YES or NO (+ what was lost)\n"
                "- Schema preserved: YES or NO (+ what was lost)\n"
                "- down_revision correct: YES or NO\n"
                "- Branch created: <name>\n"
                "- Ready for tests: YES or NO"
            ),
            agent=backend_dev,
            context=[task_plan, task_read, task_code],
        )

        # --- TASK 5: UNIT TEST ---
        task_test = Task(
            description=(
                "UNIT TEST PHASE — validate the implementation.\n\n"
                "1. run_backend_tests()\n"
                "2. Report exact numbers: X passed, Y failed\n"
                "3. Report coverage percentage\n"
                "4. Status: PASS (coverage >= 85%, 0 failures) or FAIL\n"
                "5. If FAIL: quote the exact error messages\n\n"
                "Consult read_context_file('05_quality_and_gates.md') "
                "for the Definition of Done checklist.\n\n"
                "IMPORTANT: Even if unit tests pass, the next phase "
                "will run integration tests with real HTTP requests. "
                "Report your results and move on."
            ),
            expected_output=(
                "Unit test results:\n"
                "- Passed: X | Failed: Y\n"
                "- Coverage: XX%\n"
                "- Status: PASS or FAIL\n"
                "- Errors (if any): <exact messages>"
            ),
            agent=qa_engineer,
            context=[task_review],
        )

        # --- TASK 6: INTEGRATION TEST (E2E with real HTTP requests) ---
        task_integration = Task(
            description=(
                "INTEGRATION TEST PHASE — verify the feature works "
                "end-to-end with REAL HTTP requests.\n\n"
                "This is like Cypress for the backend. The tool spins up "
                "a temporary Flask app with SQLite, makes actual HTTP "
                "calls, and verifies the full request/response cycle.\n\n"
                "Execute IN ORDER:\n"
                "1. run_integration_tests(scenario='register_and_login')\n"
                "   → Verifies basic auth flow works\n"
                "2. run_integration_tests(scenario='full_crud')\n"
                "   → Verifies register + login + update profile + "
                "read /me + data persistence\n\n"
                "DECISION:\n"
                "- If ALL scenarios PASS: report success and move on "
                "to documentation phase.\n"
                "- If ANY scenario FAILS: report the exact errors. "
                "The feature has a bug that needs fixing.\n\n"
                "IMPORTANT: This tests with real data flowing through "
                "the full stack (routes → controllers → services → "
                "models → database). If it passes here, the feature "
                "is production-ready."
            ),
            expected_output=(
                "Integration test results:\n"
                "- Scenario 'register_and_login': PASS or FAIL\n"
                "- Scenario 'full_crud': PASS or FAIL\n"
                "- Overall: PASS or FAIL\n"
                "- Errors (if any): <exact messages>\n"
                "- Steps executed: <list of HTTP calls and responses>"
            ),
            agent=qa_engineer,
            context=[task_review, task_test],
        )

        # --- TASK 7: COMMIT + DOCUMENTATION (post-gates only) ---
        task_docs = Task(
            description=(
                "COMMIT + DOCUMENTATION PHASE — update traceability records.\n\n"
                "After successful implementation and testing, update "
                "the project records for traceability.\n\n"
                "Execute IN ORDER:\n"
                "1. If BOTH unit and integration tests passed, commit now:\n"
                "   git_operations(command='commit', "
                "message='feat(<scope>): <summary>')\n"
                "2. git_operations(command='status') — capture branch/commit info\n"
                "3. Extract commit hash from git output\n"
                "4. update_task_status(\n"
                "     task_id='<task ID from the plan>',\n"
                "     status='Done',\n"
                "     progress='100%',\n"
                "     commit_hash='<commit hash>'\n"
                "   )\n"
                "5. Verify the update by reading TASKS.md\n\n"
                "RULES:\n"
                "- Only mark as Done if BOTH unit tests and "
                "integration tests passed.\n"
                "- If tests failed, mark as 'In Progress' with the "
                "current progress percentage.\n"
                "- If tests failed, DO NOT commit.\n"
                "- Always include the commit hash for traceability.\n"
                "- The task_id comes from Task 1 (PLAN) output."
            ),
            expected_output=(
                "Documentation results:\n"
                "- Task ID updated: <id>\n"
                "- New status: Done (or In Progress if tests failed)\n"
                "- Commit hash recorded: <hash>\n"
                "- TASKS.md verified: YES"
            ),
            agent=backend_dev,
            context=[task_plan, task_review, task_test, task_integration],
        )

        # --- TASK 8: CONTRACT PACK (backend -> frontend handoff) ---
        task_contract_pack = Task(
            description=(
                "CONTRACT PACK PHASE — publish backend contract artifacts for "
                "frontend agents.\n\n"
                "Execute this phase for every backend run (even if no endpoint "
                "changed, publish an explicit note).\n\n"
                "Steps:\n"
                "1. Build a TOON/1 payload (preferred over JSON for token economy) "
                "with these keys:\n"
                "   - rest_endpoints: [{method, path, description}]\n"
                "   - graphql_endpoints: [{type, name, description}]\n"
                "   - auth: short text about auth/session expectations\n"
                "   - error_contract: list of error semantics/codes\n"
                "   - examples: list of request/response examples (short)\n"
                "   - notes: rollout caveats, feature flags, backward compatibility\n"
                "2. publish_feature_contract_pack(\n"
                "     task_id='<task id>',\n"
                "     feature_name='<feature title>',\n"
                "     summary='<what frontend must implement>',\n"
                "     payload_toon='TOON/1 ...'\n"
                "   )\n"
                "3. Verify by reading read_feature_contract_pack('<task id>', 'toon') "
                "and 'md'.\n\n"
                "Rules:\n"
                "- If no API contract changed, still publish a pack with empty "
                "endpoint lists and a clear `notes` explanation.\n"
                "- Keep fields objective and implementation-ready for frontend squads."
            ),
            expected_output=(
                "Contract pack results:\n"
                "- Published task id: <id>\n"
                "- JSON file path\n"
                "- Markdown file path\n"
                "- Frontend action summary"
            ),
            agent=backend_dev,
            context=[task_plan, task_review, task_test, task_integration, task_docs],
        )

        # --- CREW ---
        crew = Crew(
            agents=[manager, backend_dev, qa_engineer],
            tasks=[
                task_plan,
                task_read,
                task_code,
                task_review,
                task_test,
                task_integration,
                task_docs,
                task_contract_pack,
            ],
            process=Process.sequential,
            verbose=True,
        )

        return crew.kickoff()

    def run_frontend_workflow(self, briefing: str, plan_only: bool = False):
        """
        6-task generic workflow for app/web repositories:
          Plan -> Read -> Write -> Review/Branch -> Quality -> Commit/Docs
        """
        manager = Agent(
            role="Gerente de Projeto Frontend",
            goal=(
                "Select the next pending task, produce a concrete file-level "
                "plan, and avoid duplicate implementation."
            ),
            backstory=(
                "You coordinate feature delivery by reading pending tasks, "
                "governance and current code before planning."
            ),
            tools=[
                self.rpt,
                self.rts,
                self.rcf,
                self.rgf,
                self.rpf,
                self.lfcp,
                self.rfcp,
            ],
            verbose=True,
            allow_delegation=True,
        )

        frontend_dev = Agent(
            role="Senior Frontend Engineer",
            goal=(
                "Implement the planned task with minimal, reversible changes "
                "while preserving existing behavior."
            ),
            backstory=(
                "You always read files before writing, avoid broad rewrites, "
                "and follow repository coding standards."
            ),
            tools=[
                self.rpf,
                self.lpf,
                self.rcf,
                self.rfcp,
                self.wf,
                self.git,
                self.uts,
            ],
            verbose=True,
        )

        qa_engineer = Agent(
            role="Frontend QA Engineer",
            goal=(
                "Run repository quality gates and block completion on failures."
            ),
            backstory=(
                "You execute canonical quality checks and report exact command "
                "outputs and pass/fail status."
            ),
            tools=[self.rqg, self.rcf],
            verbose=True,
        )

        task_plan = Task(
            description=(
                "BOOTSTRAP:\n"
                "1. read_pending_tasks()\n"
                "2. read_tasks_section('<task_id or area>')\n"
                "3. read_governance_file('product.md')\n"
                "4. read_governance_file('steering.md')\n"
                "5. list_feature_contract_packs()\n"
                "6. read_feature_contract_pack('<related backend task id>', 'md') "
                "when a contract pack exists for the feature dependency.\n\n"
                f'USER BRIEFING: "{briefing}"\n\n'
                "DUPLICATE WORK GUARD:\n"
                "If task is already done or code already exists, output "
                "'ALREADY IMPLEMENTED — no changes needed.'\n\n"
                "Produce concrete plan with:\n"
                "- task ID\n"
                "- files to modify/create\n"
                "- expected code additions\n"
                "- implementation order"
            ),
            expected_output=(
                "Numbered plan including task ID, file list, and sequence."
            ),
            agent=manager,
        )

        if plan_only:
            crew = Crew(
                agents=[manager],
                tasks=[task_plan],
                process=Process.sequential,
                verbose=True,
            )
            return crew.kickoff()

        task_read = Task(
            description=(
                "READ PHASE:\n"
                "1. list_project_files('<relevant dir>')\n"
                "2. read_project_file('<each target file>')\n"
                "3. report existing structures and risks.\n"
                "Do not write code in this phase."
            ),
            expected_output=(
                "Reading report with files analyzed and integration risks."
            ),
            agent=frontend_dev,
            context=[task_plan],
        )

        task_code = Task(
            description=(
                "WRITE PHASE:\n"
                "- Implement only planned changes.\n"
                "- Preserve existing code and non-ASCII characters.\n"
                "- Write complete file content when updating files.\n"
                "- Do not commit yet."
            ),
            expected_output="List of changed files and summary of changes.",
            agent=frontend_dev,
            context=[task_plan, task_read],
        )

        task_review = Task(
            description=(
                "REVIEW/BRANCH PHASE:\n"
                "1. git_operations(command='status')\n"
                "2. create conventional branch:\n"
                "   git_operations(command='create_branch', "
                "branch_name='feat/<task-id>-<short-description>')\n"
                "3. git_operations(command='status')\n"
                "Do NOT commit in this phase. Commit is allowed only after "
                "run_repo_quality_gates() passes."
            ),
            expected_output="Branch name and git status on feature branch.",
            agent=frontend_dev,
            context=[task_code],
        )

        task_quality = Task(
            description=(
                "QUALITY PHASE:\n"
                "Run run_repo_quality_gates() and report pass/fail.\n"
                "If failed, include exact stderr/stdout summary."
            ),
            expected_output=(
                "Quality gate command used, result, and failure details if any."
            ),
            agent=qa_engineer,
            context=[task_review],
        )

        task_docs = Task(
            description=(
                "COMMIT + DOCUMENTATION PHASE:\n"
                "If quality passed, commit and then update task status:\n"
                "git_operations(command='commit', message='feat(<scope>): <summary>')\n"
                "update_task_status(task_id='<task_id>', status='Done', "
                "progress='100%', commit_hash='<hash>').\n"
                "If quality failed, do not commit and mark as In Progress with realistic progress."
            ),
            expected_output="Task board update confirmation.",
            agent=frontend_dev,
            context=[task_plan, task_review, task_quality],
        )

        crew = Crew(
            agents=[manager, frontend_dev, qa_engineer],
            tasks=[
                task_plan,
                task_read,
                task_code,
                task_review,
                task_quality,
                task_docs,
            ],
            process=Process.sequential,
            verbose=True,
        )
        return crew.kickoff()


def _render_progress_bar(completed: int, total: int, width: int = 24) -> str:
    if total <= 0:
        total = 1
    ratio = min(max(completed / total, 0.0), 1.0)
    filled = int(ratio * width)
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def _write_multi_run_report(
    *,
    briefing: str,
    briefing_hash: str,
    execution_mode: str,
    policy_fingerprint: str,
    targets: tuple[str, str, str],
    results: dict[str, dict[str, object]],
    done_count: int,
    skipped_count: int,
    blocked_count: int,
    overall_rc: int,
) -> Path:
    report_dir = PLATFORM_ROOT / "tasks_status"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"ORCH-{briefing_hash[:8].upper()}-report.md"

    lines: list[str] = [
        "# AI Squad Orchestration Report",
        "",
        f"- generated_at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- briefing_hash: `{briefing_hash}`",
        f"- execution_mode: `{execution_mode}`",
        f"- policy_fingerprint: `{policy_fingerprint}`",
        f"- overall_status: `{'done' if overall_rc == 0 else 'blocked'}`",
        "",
        "## Briefing",
        "",
        "```text",
        briefing,
        "```",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|:--|:--|",
        f"| repos_done | {done_count} |",
        f"| repos_skipped | {skipped_count} |",
        f"| repos_blocked | {blocked_count} |",
        f"| overall_return_code | {overall_rc} |",
        "",
        "## Per Repository",
        "",
        "| Repo | Task | Status | Return Code | Duration (s) | Precommit | Quality Evidence | Branch Guardrail |",
        "|:--|:--|:--|--:|--:|:--|:--|:--|",
    ]

    for repo in targets:
        result = results.get(repo, {})
        lines.append(
            "| {repo} | {task} | {status} | {rc} | {duration} | {pre} | {quality} | {branch} |".format(
                repo=repo,
                task=result.get("task_id", "UNSPECIFIED"),
                status=result.get("status", "blocked"),
                rc=result.get("returncode", 1),
                duration=result.get("duration_seconds", 0.0),
                pre=result.get("precommit_status", "unknown"),
                quality=str(result.get("quality_gate_evidence", "missing")).replace("|", "/"),
                branch=str(result.get("branch_guardrail_evidence", "missing")).replace("|", "/"),
            )
        )

    lines.extend(["", "## Details", ""])
    for repo in targets:
        result = results.get(repo, {})
        lines.extend(
            [
                f"### {repo}",
                "",
                f"- task_id: `{result.get('task_id', 'UNSPECIFIED')}`",
                f"- status: `{result.get('status', 'blocked')}`",
                f"- return_code: `{result.get('returncode', 1)}`",
                f"- duration_seconds: `{result.get('duration_seconds', 0.0)}`",
                f"- precommit_status: `{result.get('precommit_status', 'unknown')}`",
                f"- quality_gate_evidence: `{result.get('quality_gate_evidence', 'missing')}`",
                f"- branch_guardrail_evidence: `{result.get('branch_guardrail_evidence', 'missing')}`",
            ]
        )
        commits = result.get("commit_hashes") or []
        if isinstance(commits, list) and commits:
            lines.append(f"- commits: `{', '.join(str(c) for c in commits)}`")
        skip_reason = str(result.get("skip_reason", "")).strip()
        if skip_reason:
            lines.append(f"- skip_reason: `{skip_reason}`")
        tech_debt = result.get("tech_debt_hints") or []
        if isinstance(tech_debt, list) and tech_debt:
            lines.append("- possible_tech_debt:")
            for hint in tech_debt:
                lines.append(f"  - {hint}")

        stdout_tail = str(result.get("stdout", "")).strip()
        stderr_tail = str(result.get("stderr", "")).strip()
        if stdout_tail:
            lines.extend(["", "#### stdout_tail", "", "```text"])
            lines.extend(stdout_tail.splitlines()[-40:])
            lines.append("```")
        if stderr_tail:
            lines.extend(["", "#### stderr_tail", "", "```text"])
            lines.extend(stderr_tail.splitlines()[-40:])
            lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def run_multi_repo_orchestration(briefing: str, execution_mode: str) -> tuple[int, Path]:
    """Run one squad execution per product repo in parallel with detailed telemetry."""
    targets = ("auraxis-api", "auraxis-web", "auraxis-app")
    script_path = str((SQUAD_ROOT / "main.py").resolve())
    env_base = os.environ.copy()
    child_timeout_seconds = int(os.getenv("AURAXIS_CHILD_TIMEOUT_SECONDS", "3600"))
    force_rerun = os.getenv("AURAXIS_FORCE_RERUN", "false").strip().lower() == "true"
    allow_dirty_worktree = (
        os.getenv("AURAXIS_ALLOW_DIRTY_WORKTREE", "false").strip().lower() == "true"
    )
    use_worktree_execution = (
        os.getenv("AURAXIS_USE_WORKTREE_EXECUTION", "true").strip().lower() == "true"
    )
    auto_rollback_on_block = (
        os.getenv("AURAXIS_AUTO_ROLLBACK_ON_BLOCK", "true").strip().lower() == "true"
    )
    policy_fingerprint = _compute_policy_fingerprint()
    results: dict[str, dict[str, object]] = {}
    briefing_hash = _briefing_hash(briefing)

    def _run_target(repo: str) -> dict[str, object]:
        inferred_task_id = _resolve_task_id_for_repo(repo, briefing)
        if inferred_task_id == "UNSPECIFIED":
            reason = (
                "preflight blocked: no task ID could be resolved from tasks board. "
                "Set explicit task ID in briefing or fix tasks file markers."
            )
            print(f"[{repo}][orchestrator] {reason}")
            blocked_result = {
                "returncode": 1,
                "timed_out": False,
                "duration_seconds": 0.0,
                "stdout": "",
                "stderr": reason,
                "task_id": "UNRESOLVED",
                "status": "blocked",
                "commit_hashes": [],
                "precommit_status": "failed",
                "tech_debt_hints": [reason],
            }
            append_ledger_entry(
                {
                    "repo": repo,
                    "task_id": blocked_result["task_id"],
                    "briefing_hash": briefing_hash,
                    "execution_mode": execution_mode,
                    "status": "blocked",
                    "returncode": 1,
                    "timed_out": False,
                    "duration_seconds": 0.0,
                    "commit_hashes": [],
                    "precommit_status": "failed",
                    "skip_reason": reason,
                },
                repo=repo,
            )
            return blocked_result

        if not allow_dirty_worktree:
            is_clean, clean_message = _check_repo_worktree_clean(repo)
            if not is_clean:
                reason = f"preflight blocked: {clean_message}"
                print(f"[{repo}][orchestrator] {reason}")
                blocked_result = {
                    "returncode": 1,
                    "timed_out": False,
                    "duration_seconds": 0.0,
                    "stdout": "",
                    "stderr": reason,
                    "task_id": inferred_task_id,
                    "status": "blocked",
                    "commit_hashes": [],
                    "precommit_status": "failed",
                    "tech_debt_hints": [reason],
                }
                append_ledger_entry(
                    {
                        "repo": repo,
                        "task_id": inferred_task_id,
                        "briefing_hash": briefing_hash,
                        "execution_mode": execution_mode,
                        "status": "blocked",
                        "returncode": 1,
                        "timed_out": False,
                        "duration_seconds": 0.0,
                        "commit_hashes": [],
                        "precommit_status": "failed",
                        "skip_reason": reason,
                    },
                    repo=repo,
                )
                return blocked_result

        if not force_rerun and inferred_task_id != "UNSPECIFIED":
            latest = get_latest_ledger_entry(
                repo=repo,
                task_id=inferred_task_id,
                briefing_hash=briefing_hash,
            )
            if latest and latest.get("status") == "done" and latest.get("commit_hashes"):
                reason = (
                    "idempotency skip: task already executed for same briefing hash "
                    f"({briefing_hash}) with commits {latest.get('commit_hashes')}"
                )
                print(f"[{repo}][orchestrator] {reason}")
                skipped_result = {
                    "returncode": 0,
                    "timed_out": False,
                    "duration_seconds": 0.0,
                    "stdout": "",
                    "stderr": "",
                    "task_id": inferred_task_id,
                    "status": "skipped",
                    "commit_hashes": latest.get("commit_hashes", []),
                    "precommit_status": latest.get("precommit_status", "unknown"),
                    "tech_debt_hints": [],
                    "skip_reason": reason,
                }
                append_ledger_entry(
                    {
                        "repo": repo,
                        "task_id": inferred_task_id,
                        "briefing_hash": briefing_hash,
                        "execution_mode": execution_mode,
                        "status": "skipped",
                        "returncode": 0,
                        "timed_out": False,
                        "duration_seconds": 0.0,
                        "commit_hashes": skipped_result["commit_hashes"],
                        "precommit_status": skipped_result["precommit_status"],
                        "skip_reason": reason,
                    },
                    repo=repo,
                )
                return skipped_result

        env = env_base.copy()
        _reset_quality_commit_guard_env(env)
        child_briefing = briefing
        if infer_task_id(briefing) == "UNSPECIFIED" and inferred_task_id != "UNSPECIFIED":
            child_briefing = (
                f"{briefing}\n\n"
                f"Task obrigatoria deste repositorio: {inferred_task_id}.\n"
                "Implemente somente essa task e nao troque para outra."
            )
        env["AURAXIS_TARGET_REPO"] = repo
        env["AURAXIS_BRIEFING"] = child_briefing
        env["AURAXIS_RESOLVED_TASK_ID"] = inferred_task_id
        env["AURAXIS_POLICY_FINGERPRINT"] = policy_fingerprint
        env["AURAXIS_EXECUTION_MODE"] = execution_mode
        env["AURAXIS_MULTI_CHILD"] = "1"

        execution_worktree: Path | None = None
        if use_worktree_execution:
            execution_worktree, worktree_error = _create_execution_worktree(repo)
            if execution_worktree is None:
                reason = f"preflight blocked: {worktree_error}"
                print(f"[{repo}][orchestrator] {reason}")
                blocked_result = {
                    "returncode": 1,
                    "timed_out": False,
                    "duration_seconds": 0.0,
                    "stdout": "",
                    "stderr": reason,
                    "task_id": inferred_task_id,
                    "status": "blocked",
                    "commit_hashes": [],
                    "precommit_status": "failed",
                    "tech_debt_hints": [reason],
                }
                append_ledger_entry(
                    {
                        "repo": repo,
                        "task_id": inferred_task_id,
                        "briefing_hash": briefing_hash,
                        "execution_mode": execution_mode,
                        "status": "blocked",
                        "returncode": 1,
                        "timed_out": False,
                        "duration_seconds": 0.0,
                        "commit_hashes": [],
                        "precommit_status": "failed",
                        "skip_reason": reason,
                    },
                    repo=repo,
                )
                return blocked_result
            env["AURAXIS_PROJECT_ROOT"] = str(execution_worktree)

        try:
            raw = _stream_subprocess(
                repo=repo,
                command=[sys.executable, script_path],
                env=env,
                timeout_seconds=child_timeout_seconds,
            )
        finally:
            if execution_worktree is not None:
                _remove_execution_worktree(repo, execution_worktree)
        extracted = _extract_summary_from_output(
            inferred_task_id,
            raw["stdout"],
            raw["stderr"],
        )
        status = "done"
        if raw["timed_out"]:
            status = "blocked"
        elif raw["returncode"] != 0:
            status = "blocked"
        elif "status: blocked" in raw["stdout"].lower():
            status = "blocked"
        elif extracted.get("precommit_status") == "failed":
            status = "blocked"
        elif extracted.get("quality_gate_failed"):
            status = "blocked"
        elif extracted.get("tool_error_detected"):
            status = "blocked"

        result = {
            **raw,
            **extracted,
            "status": status,
        }
        resolved_task_id = inferred_task_id.upper()
        reported_task_id = str(result.get("task_id", "")).strip().upper()
        if reported_task_id and reported_task_id != resolved_task_id:
            result["status"] = "blocked"
            drift_message = (
                "task_id drift detected: "
                f"resolved={resolved_task_id}, reported={reported_task_id}"
            )
            hints = list(result.get("tech_debt_hints", []))
            hints.append(drift_message)
            result["tech_debt_hints"] = hints[:5]
            stderr = str(result.get("stderr", "")).strip()
            if stderr:
                result["stderr"] = f"{stderr}\n{drift_message}"
            else:
                result["stderr"] = drift_message
            result["task_id"] = resolved_task_id

        if (
            result["status"] == "blocked"
            and execution_worktree is None
            and auto_rollback_on_block
        ):
            _rollback_repo_worktree(repo)

        append_ledger_entry(
            {
                "repo": repo,
                "task_id": result["task_id"],
                "briefing_hash": briefing_hash,
                "execution_mode": execution_mode,
                "status": result["status"],
                "returncode": result["returncode"],
                "timed_out": result["timed_out"],
                "duration_seconds": result["duration_seconds"],
                "commit_hashes": result["commit_hashes"],
                "precommit_status": result["precommit_status"],
                "quality_gate_evidence": result.get("quality_gate_evidence", "missing"),
                "branch_guardrail_evidence": result.get(
                    "branch_guardrail_evidence",
                    "missing",
                ),
            },
            repo=repo,
        )
        return result

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {executor.submit(_run_target, repo): repo for repo in targets}
        pending = set(future_map.keys())
        spinner = ("|", "/", "-", "\\")
        spin_index = 0
        run_started_at = monotonic()
        while pending:
            done, pending = wait(
                pending,
                timeout=1.0,
                return_when=FIRST_COMPLETED,
            )
            if not done:
                completed = len(results)
                total = len(targets)
                elapsed = monotonic() - run_started_at
                bar = _render_progress_bar(completed, total)
                running_repos = sorted(future_map[future] for future in pending)
                running_preview = ", ".join(running_repos) if running_repos else "none"
                print(
                    f"[progress] {spinner[spin_index % len(spinner)]} "
                    f"{bar} {completed}/{total} completed "
                    f"elapsed={elapsed:.1f}s running={running_preview}"
                )
                spin_index += 1
                continue

            for future in done:
                repo = future_map[future]
                try:
                    results[repo] = future.result()
                except Exception as exc:  # pragma: no cover - defensive fallback
                    results[repo] = {
                        "returncode": 1,
                        "stdout": "",
                        "stderr": str(exc),
                        "timed_out": False,
                        "duration_seconds": 0.0,
                        "task_id": "UNSPECIFIED",
                        "status": "blocked",
                        "commit_hashes": [],
                        "precommit_status": "unknown",
                        "tech_debt_hints": [],
                    }
                print(
                    f"[progress] ✔ repo={repo} finished "
                    f"status={results[repo].get('status', 'blocked')} "
                    f"({len(results)}/{len(targets)})"
                )

    print("=== AURAXIS MULTI-REPO ORCHESTRATION SUMMARY (MASTER) ===")
    overall_rc = 0
    done_count = 0
    blocked_count = 0
    skipped_count = 0
    for repo in targets:
        result = results.get(
            repo,
            {
                "returncode": 1,
                "stdout": "",
                "stderr": "missing result",
                "timed_out": False,
                "duration_seconds": 0.0,
                "task_id": "UNSPECIFIED",
                "status": "blocked",
                "commit_hashes": [],
                "precommit_status": "unknown",
                "tech_debt_hints": [],
            },
        )
        if result["status"] == "done":
            done_count += 1
        elif result["status"] == "skipped":
            skipped_count += 1
        else:
            blocked_count += 1
            overall_rc = 1
        print(f"[{repo}] status={result['status']} return_code={result['returncode']}")
        print(f"[{repo}] task_id={result['task_id']} duration={result['duration_seconds']}s")
        print(f"[{repo}] precommit_local={result['precommit_status']}")
        print(
            f"[{repo}] quality_gate_evidence={result.get('quality_gate_evidence', 'missing')}"
        )
        print(
            f"[{repo}] branch_guardrail_evidence="
            f"{result.get('branch_guardrail_evidence', 'missing')}"
        )
        if result.get("timed_out"):
            print(f"[{repo}] timeout=true ({child_timeout_seconds}s)")
        if result.get("commit_hashes"):
            print(f"[{repo}] commits={', '.join(result['commit_hashes'])}")
        if result.get("skip_reason"):
            print(f"[{repo}] skip_reason={result['skip_reason']}")
        if result["stdout"].strip():
            print(f"[{repo}] stdout_tail:")
            print("\n".join(result["stdout"].strip().splitlines()[-20:]))
        if result["stderr"].strip():
            print(f"[{repo}] stderr_tail:")
            print("\n".join(result["stderr"].strip().splitlines()[-20:]))
        if result.get("tech_debt_hints"):
            print(f"[{repo}] possible_tech_debt:")
            for hint in result["tech_debt_hints"]:
                print(f"  - {hint}")
    print("=== MASTER CONSOLIDATED SUMMARY ===")
    print(f"briefing_hash: {briefing_hash}")
    print(f"policy_fingerprint: {policy_fingerprint}")
    print(f"execution_mode: {execution_mode}")
    print(f"repos_done: {done_count}")
    print(f"repos_skipped: {skipped_count}")
    print(f"repos_blocked: {blocked_count}")
    print(
        "local_pipe_status: "
        + ", ".join(
            f"{repo}={results[repo].get('precommit_status', 'unknown')}"
            for repo in targets
            if repo in results
        )
    )
    next_action = (
        "advance to next tasks (all repositories completed/skipped)."
        if overall_rc == 0
        else "resolve blocked repositories and rerun with same briefing (use AURAXIS_FORCE_RERUN=true only if necessary)."
    )
    print(
        "next_action: "
        + next_action
    )
    report_path = _write_multi_run_report(
        briefing=briefing,
        briefing_hash=briefing_hash,
        execution_mode=execution_mode,
        policy_fingerprint=policy_fingerprint,
        targets=targets,
        results=results,
        done_count=done_count,
        skipped_count=skipped_count,
        blocked_count=blocked_count,
        overall_rc=overall_rc,
    )
    print(f"report_path: {report_path}")
    return overall_rc, report_path


# =================================================================
# BRIEFING — Edit this to tell the squad what to implement.
#
# Be specific:
#   - Task ID from TASKS.md (e.g., "B8")
#   - Exact fields/behavior expected
#   - Files to touch (the agent will read them before writing)
#   - For column renames: say RENAME explicitly
# =================================================================

if __name__ == "__main__":
    reset_tool_audit_snapshot()
    target_env = os.getenv("AURAXIS_TARGET_REPO", "all").strip()
    execution_mode = os.getenv("AURAXIS_EXECUTION_MODE", "run").strip().lower()
    plan_only = execution_mode == "plan_only"
    print("### Auraxis AI Squad — Workspace Orchestrator ###")
    print(f"Platform root: {PLATFORM_ROOT}")
    print(f"Target repo: {target_env}")
    if target_env.lower() in ("all", "auraxis-all", "*"):
        print("Target project root: multi-repo mode (api/web/app)")
    else:
        print(f"Target project root: {PROJECT_ROOT}")
    print(f"Execution mode: {execution_mode}")
    print()

    briefing = os.getenv(
        "AURAXIS_BRIEFING",
        "Execute a tarefa",
    )
    task_id = infer_task_id(briefing)
    task_id_hint = os.getenv("AURAXIS_RESOLVED_TASK_ID", "").strip().upper()
    if task_id == "UNSPECIFIED" and _TABLE_ID_RE.match(task_id_hint):
        task_id = task_id_hint
    if task_id == "UNSPECIFIED" and target_env.lower() not in ("all", "auraxis-all", "*"):
        task_id = _resolve_task_id_for_repo(TARGET_REPO_NAME, briefing)

    def _exit_preflight_block(blocked_task_id: str, details: str) -> None:
        safe_task_id = blocked_task_id
        if safe_task_id == "UNSPECIFIED":
            safe_task_id = f"UNRESOLVED-{TARGET_REPO_NAME.upper()}"
        status_file = write_status_entry(
            task_id=safe_task_id,
            status="blocked",
            phase="preflight-blocked",
            implemented="Preflight validation blocked execution before Crew kickoff.",
            next_task_suggestion="Fix preflight blockers and rerun with the same briefing.",
            details=details,
            notify_manager=True,
            notify_parallel_agents=True,
        )
        print("=== AI_SQUAD RUN SUMMARY ===")
        print(f"task_id: {safe_task_id}")
        print("status: blocked")
        print("implemented: preflight validation gate.")
        print(
            "next_task_suggestion: fix preflight blockers and rerun with the same briefing."
        )
        print(f"status_file: {status_file}")
        print("[NOTIFY_MANAGER] Preflight blocker detected. Check tasks_status file.")
        print(
            "[NOTIFY_PARALLEL_AGENTS] Hold dependent tasks until preflight blockers are resolved."
        )
        sys.exit(1)

    if target_env.lower() in ("all", "auraxis-all", "*"):
        task_id = _resolve_orchestration_task_id(briefing)
        planned_task_ids = {
            repo: _resolve_task_id_for_repo(repo, briefing)
            for repo in ("auraxis-api", "auraxis-web", "auraxis-app")
        }
        planned_details = (
            f"Briefing: {briefing}\n\n"
            "Resolved per-repo task IDs:\n"
            f"- auraxis-api: {planned_task_ids['auraxis-api']}\n"
            f"- auraxis-web: {planned_task_ids['auraxis-web']}\n"
            f"- auraxis-app: {planned_task_ids['auraxis-app']}"
        )
        write_status_entry(
            task_id=task_id,
            status="in_progress",
            phase="multi-run-start",
            implemented="Multi-repo orchestration requested.",
            next_task_suggestion="Wait for per-repo execution summary.",
            details=planned_details,
        )
        rc, report_path = run_multi_repo_orchestration(briefing, execution_mode)
        final_status = "done" if rc == 0 else "blocked"
        status_file = write_status_entry(
            task_id=task_id,
            status=final_status,
            phase="multi-run-end",
            implemented="Parallel execution triggered for api/web/app repositories.",
            next_task_suggestion=(
                "Advance to next orchestration block."
                if rc == 0
                else "Fix blockers in failed repository run(s) and retry."
            ),
            details=(
                f"overall_return_code={rc}\n\n"
                f"report_path={report_path}\n\n"
                "Resolved per-repo task IDs:\n"
                f"- auraxis-api: {planned_task_ids['auraxis-api']}\n"
                f"- auraxis-web: {planned_task_ids['auraxis-web']}\n"
                f"- auraxis-app: {planned_task_ids['auraxis-app']}"
            ),
            notify_manager=True,
            notify_parallel_agents=True,
        )
        print("=== AI_SQUAD MULTI-RUN SUMMARY ===")
        print(f"task_id: {task_id}")
        print(f"status: {final_status}")
        print(
            "implemented: parallel dispatch to auraxis-api, auraxis-web, auraxis-app"
        )
        print(f"status_file: {status_file}")
        print(f"report_path: {report_path}")
        sys.exit(rc)

    policy_expected = os.getenv("AURAXIS_POLICY_FINGERPRINT", "").strip()
    policy_ok, policy_details = _validate_policy_fingerprint(policy_expected)
    if not policy_ok:
        _exit_preflight_block(
            task_id,
            (
                f"repo={TARGET_REPO_NAME}\n"
                f"briefing={briefing}\n"
                f"error={policy_details}"
            ),
        )

    if task_id == "UNSPECIFIED":
        _exit_preflight_block(
            task_id,
            (
                f"repo={TARGET_REPO_NAME}\n"
                f"briefing={briefing}\n"
                "error=unable to resolve task id from briefing/tasks board."
            ),
        )

    allow_dirty_worktree = (
        os.getenv("AURAXIS_ALLOW_DIRTY_WORKTREE", "false").strip().lower() == "true"
    )
    if not allow_dirty_worktree:
        is_clean, clean_message = _check_repo_worktree_clean(TARGET_REPO_NAME)
        if not is_clean:
            _exit_preflight_block(
                task_id,
                (
                    f"repo={TARGET_REPO_NAME}\n"
                    f"briefing={briefing}\n"
                    f"error={clean_message}"
                ),
            )

    write_status_entry(
        task_id=task_id,
        status="in_progress",
        phase="run-start",
        implemented="Crew kickoff initialized.",
        next_task_suggestion="Complete planning, implementation, tests and documentation phases.",
        details=f"Briefing received for repo `{TARGET_REPO_NAME}`:\n\n{briefing}",
    )

    squad = AuraxisSquad()
    _reset_quality_commit_guard_env()
    try:
        if TARGET_REPO_NAME == "auraxis-api":
            result = squad.run_backend_workflow(briefing, plan_only=plan_only)
        else:
            result = squad.run_frontend_workflow(briefing, plan_only=plan_only)
        result_text = str(result)
        is_blocked, block_reasons = _derive_single_run_status(
            result_text,
            repo_name=TARGET_REPO_NAME,
            execution_mode=execution_mode,
        )
        final_status = "blocked" if is_blocked else "done"
        next_task = (
            "Resolve blockers and dependencies before retrying."
            if is_blocked
            else "Advance to the next pending task in tasks.md/TASKS.md."
        )
        auto_rollback_on_block = (
            os.getenv("AURAXIS_AUTO_ROLLBACK_ON_BLOCK", "true").strip().lower()
            == "true"
        )
        is_multi_child = os.getenv("AURAXIS_MULTI_CHILD", "0").strip() == "1"
        if final_status == "blocked" and auto_rollback_on_block and not is_multi_child:
            _rollback_execution_target()
            result_text = (
                f"{result_text}\n\n[orchestrator] auto rollback applied to execution target."
            )
        details = result_text
        if block_reasons:
            details = f"block_reasons={', '.join(block_reasons)}\n\n{result_text}"
        status_file = write_status_entry(
            task_id=task_id,
            status=final_status,
            phase="run-end",
            implemented=(
                "PM->Dev->QA workflow executed with planning, code review and validation phases."
            ),
            next_task_suggestion=next_task,
            details=details,
            notify_manager=True,
            notify_parallel_agents=True,
        )
        print("=== AI_SQUAD RUN SUMMARY ===")
        print(f"task_id: {task_id}")
        print(f"status: {final_status}")
        print(
            "implemented: "
            + (
                "planning-only workflow."
                if plan_only
                else "PM->Dev->QA workflow with planning, implementation, quality and docs phases."
            )
        )
        print(f"next_task_suggestion: {next_task}")
        print(f"status_file: {status_file}")
        if is_blocked:
            print(
                "[NOTIFY_MANAGER] Workflow ended with blockers. Check tasks_status file."
            )
            print(
                "[NOTIFY_PARALLEL_AGENTS] Dependent work may be blocked; sync on dependencies."
            )
    except Exception:
        stack_trace = traceback.format_exc()
        status_file = write_status_entry(
            task_id=task_id,
            status="blocked",
            phase="run-exception",
            implemented="Workflow aborted before completion.",
            next_task_suggestion="Fix runtime/configuration issue and rerun the same task.",
            details=stack_trace,
            notify_manager=True,
            notify_parallel_agents=True,
        )
        print("=== AI_SQUAD RUN SUMMARY ===")
        print(f"task_id: {task_id}")
        print("status: blocked")
        print("implemented: workflow interrupted by runtime exception.")
        print(
            "next_task_suggestion: fix setup/runtime issue and retry with the same briefing."
        )
        print(f"status_file: {status_file}")
        print(
            "[NOTIFY_MANAGER] Runtime failure recorded in tasks_status. Immediate review required."
        )
        print(
            "[NOTIFY_PARALLEL_AGENTS] Hold dependent tasks until blocker resolution."
        )
        raise
