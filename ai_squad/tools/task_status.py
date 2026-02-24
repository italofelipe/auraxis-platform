"""Runtime task status reporting for multi-agent coordination.

This module writes local markdown run logs to `<platform>/tasks_status/`.
These files are operational telemetry only and are intentionally excluded from git.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from .tool_security import PLATFORM_ROOT, TARGET_REPO_NAME

TASK_STATUS_DIR: Path = PLATFORM_ROOT / "tasks_status"
_TASK_ID_RE = re.compile(r"\b([A-Z]+-\d+|[A-Z]\d+)\b")


def infer_task_id(text: str) -> str:
    match = _TASK_ID_RE.search(text or "")
    if not match:
        return "UNSPECIFIED"
    return match.group(1)


def _safe_task_filename(task_id: str) -> str:
    normalized = (task_id or "UNSPECIFIED").strip().upper()
    normalized = re.sub(r"[^A-Z0-9_-]", "-", normalized)
    return f"{normalized}.md"


def write_status_entry(
    *,
    task_id: str,
    status: str,
    phase: str,
    implemented: str,
    next_task_suggestion: str,
    details: str,
    notify_manager: bool = True,
    notify_parallel_agents: bool = True,
) -> Path:
    TASK_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    entry_file = TASK_STATUS_DIR / _safe_task_filename(task_id)
    timestamp = datetime.now(UTC).isoformat()
    content = (
        f"## {timestamp}\n"
        f"- repo: `{TARGET_REPO_NAME}`\n"
        f"- task_id: `{task_id}`\n"
        f"- phase: `{phase}`\n"
        f"- status: `{status}`\n"
        f"- notify_manager: `{str(notify_manager).lower()}`\n"
        f"- notify_parallel_agents: `{str(notify_parallel_agents).lower()}`\n"
        f"- implemented: {implemented}\n"
        f"- next_task_suggestion: {next_task_suggestion}\n"
        f"- details:\n\n{details.strip()}\n\n"
    )
    with entry_file.open("a", encoding="utf-8") as file:
        file.write(content)
    return entry_file

