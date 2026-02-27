"""
Auraxis AI Squad — Workspace Orchestrator (backend workflow enabled).

Pipeline:
  PM (plan) → Dev (read) → Dev (write) → Dev (review) → QA (unit test)
  → QA (integration test) → Dev (documentation)

The 7-task architecture builds on the 5-task pipeline with two new phases:
  - Task 6 (INTEGRATION TEST): makes REAL HTTP requests against the Flask
    app to verify the feature works end-to-end (like Cypress for backend).
  - Task 7 (DOCUMENTATION): auto-updates TASKS.md with status, progress,
    and commit hash for traceability.

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
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from tools.task_status import infer_task_id, write_status_entry
from tools.tool_security import PLATFORM_ROOT, PROJECT_ROOT, SQUAD_ROOT, TARGET_REPO_NAME
from tools.project_tools import (
    GetLatestMigrationTool,
    GitOpsTool,
    IntegrationTestTool,
    ListProjectFilesTool,
    ReadAlembicHistoryTool,
    ReadContextFileTool,
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

        # Validation tools
        self.vmc = ValidateMigrationConsistencyTool()

        # Execution tools
        self.rtst = RunTestsTool()
        self.rqg = RunRepoQualityGatesTool()
        self.rit = IntegrationTestTool()

        # Documentation tools
        self.uts = UpdateTaskStatusTool()

        # Write + Git tools
        self.wf = WriteFileTool()
        self.git = GitOpsTool()

    def run_backend_workflow(self, briefing: str, plan_only: bool = False):
        """
        7-task pipeline:
          Plan -> Read -> Write -> Review -> Unit Test
          -> Integration Test -> Documentation.

        Task 2 (Read) prevents blind overwrites.
        Task 4 (Review) catches model/migration inconsistencies
        BEFORE committing, so agents self-correct.
        Task 6 (Integration Test) makes real HTTP requests to verify E2E.
        Task 7 (Documentation) auto-updates TASKS.md for traceability.
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

        # --- TASK 4: REVIEW (self-check before commit) ---
        task_review = Task(
            description=(
                "REVIEW PHASE — validate consistency before committing.\n\n"
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
                "- If all checks pass: proceed to create branch and commit.\n"
                "  git_operations(command='create_branch', "
                "branch_name='feat/<task-id>-<description>')\n"
                "  git_operations(command='commit', "
                "message='feat(<scope>): <description>')\n\n"
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
                "- Commit: <hash or 'blocked — issues found'>"
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

        # --- TASK 7: DOCUMENTATION (auto-update TASKS.md) ---
        task_docs = Task(
            description=(
                "DOCUMENTATION PHASE — update traceability records.\n\n"
                "After successful implementation and testing, update "
                "the project records for traceability.\n\n"
                "Execute IN ORDER:\n"
                "1. git_operations(command='status') — get the current "
                "branch and last commit info\n"
                "2. Extract the commit hash from the git status/log\n"
                "3. update_task_status(\n"
                "     task_id='<task ID from the plan>',\n"
                "     status='Done',\n"
                "     progress='100%',\n"
                "     commit_hash='<commit hash>'\n"
                "   )\n"
                "4. Verify the update by reading TASKS.md\n\n"
                "RULES:\n"
                "- Only mark as Done if BOTH unit tests and "
                "integration tests passed.\n"
                "- If tests failed, mark as 'In Progress' with the "
                "current progress percentage.\n"
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
            ],
            process=Process.sequential,
            verbose=True,
        )

        return crew.kickoff()

    def run_frontend_workflow(self, briefing: str, plan_only: bool = False):
        """
        6-task generic workflow for app/web repositories:
          Plan -> Read -> Write -> Review/Commit -> Quality -> Docs
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
            tools=[self.rpt, self.rts, self.rcf, self.rgf, self.rpf],
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
            tools=[self.rpf, self.lpf, self.rcf, self.wf, self.git, self.uts],
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
                "4. read_governance_file('steering.md')\n\n"
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
                "REVIEW/COMMIT PHASE:\n"
                "1. git_operations(command='status')\n"
                "2. create conventional branch:\n"
                "   git_operations(command='create_branch', "
                "branch_name='feat/<task-id>-<short-description>')\n"
                "3. commit with conventional commit message:\n"
                "   git_operations(command='commit', "
                "message='feat(<scope>): <summary>')\n"
                "Block completion if commit cannot be created."
            ),
            expected_output="Branch name, commit result, and git status.",
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
                "DOCUMENTATION PHASE:\n"
                "If quality passed, update task status using:\n"
                "update_task_status(task_id='<task_id>', status='Done', "
                "progress='100%', commit_hash='<hash>').\n"
                "If quality failed, mark as In Progress with realistic progress."
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


def run_multi_repo_orchestration(briefing: str, execution_mode: str) -> int:
    """Run one squad execution per product repo in parallel."""
    targets = ("auraxis-api", "auraxis-web", "auraxis-app")
    script_path = str((SQUAD_ROOT / "main.py").resolve())
    env_base = os.environ.copy()
    results: dict[str, tuple[int, str, str]] = {}

    def _run_target(repo: str) -> tuple[int, str, str]:
        env = env_base.copy()
        env["AURAXIS_TARGET_REPO"] = repo
        env["AURAXIS_BRIEFING"] = briefing
        env["AURAXIS_EXECUTION_MODE"] = execution_mode
        env["AURAXIS_MULTI_CHILD"] = "1"
        completed = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
        )
        return completed.returncode, completed.stdout, completed.stderr

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {executor.submit(_run_target, repo): repo for repo in targets}
        for future in as_completed(future_map):
            repo = future_map[future]
            try:
                results[repo] = future.result()
            except Exception as exc:  # pragma: no cover - defensive fallback
                results[repo] = (1, "", str(exc))

    print("=== AURAXIS MULTI-REPO ORCHESTRATION SUMMARY ===")
    overall_rc = 0
    for repo in targets:
        rc, out, err = results.get(repo, (1, "", "missing result"))
        if rc != 0:
            overall_rc = 1
        print(f"[{repo}] return_code={rc}")
        if out.strip():
            print(f"[{repo}] stdout (tail):")
            print("\n".join(out.strip().splitlines()[-20:]))
        if err.strip():
            print(f"[{repo}] stderr (tail):")
            print("\n".join(err.strip().splitlines()[-20:]))
    return overall_rc


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

    if target_env.lower() in ("all", "auraxis-all", "*"):
        write_status_entry(
            task_id=task_id,
            status="in_progress",
            phase="multi-run-start",
            implemented="Multi-repo orchestration requested.",
            next_task_suggestion="Wait for per-repo execution summary.",
            details=f"Briefing: {briefing}",
        )
        rc = run_multi_repo_orchestration(briefing, execution_mode)
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
            details=f"overall_return_code={rc}",
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
        sys.exit(rc)

    write_status_entry(
        task_id=task_id,
        status="in_progress",
        phase="run-start",
        implemented="Crew kickoff initialized.",
        next_task_suggestion="Complete planning, implementation, tests and documentation phases.",
        details=f"Briefing received for repo `{TARGET_REPO_NAME}`:\n\n{briefing}",
    )

    squad = AuraxisSquad()
    try:
        if TARGET_REPO_NAME == "auraxis-api":
            result = squad.run_backend_workflow(briefing, plan_only=plan_only)
        else:
            result = squad.run_frontend_workflow(briefing, plan_only=plan_only)
        result_text = str(result)
        normalized = result_text.upper()
        is_blocked = any(
            marker in normalized for marker in ("FAIL", "ERROR", "BLOCKED", "ISSUES")
        )
        final_status = "blocked" if is_blocked else "done"
        next_task = (
            "Resolve blockers and dependencies before retrying."
            if is_blocked
            else "Advance to the next pending task in tasks.md/TASKS.md."
        )
        status_file = write_status_entry(
            task_id=task_id,
            status=final_status,
            phase="run-end",
            implemented=(
                "PM->Dev->QA workflow executed with planning, code review and validation phases."
            ),
            next_task_suggestion=next_task,
            details=result_text,
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
