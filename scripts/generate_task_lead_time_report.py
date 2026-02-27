#!/usr/bin/env python3
"""Generate lead-time metrics (task -> PR -> merge) across Auraxis repos."""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TASK_ID_PATTERN = re.compile(r"\b(?:APP|WEB|PLT|B|A|C|D|E|F|G|H|I|J|X)\d+\b")
DEFAULT_OWNER = "italofelipe"
DEFAULT_REPOS = ("auraxis-api", "auraxis-web", "auraxis-app")


@dataclass(frozen=True)
class PullRequestLeadTime:
    repo: str
    task_id: str
    pr_number: int
    pr_title: str
    pr_url: str
    head_ref: str
    created_at: str
    merged_at: str
    lead_time_hours: float


def _parse_iso_datetime(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(UTC)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * percentile))
    return float(ordered[index])


def _github_get(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "auraxis-lead-time-metrics",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url=url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"GitHub API error {error.code} for {url}") from error
    except URLError as error:
        raise RuntimeError(f"GitHub API network error for {url}: {error}") from error


def _extract_task_ids(pr_payload: dict[str, Any]) -> list[str]:
    candidates = [
        str(pr_payload.get("title", "")),
        str(pr_payload.get("body", "")),
        str(pr_payload.get("head", {}).get("ref", "")),
    ]
    found: set[str] = set()
    for candidate in candidates:
        for match in TASK_ID_PATTERN.findall(candidate.upper()):
            found.add(match)
    if not found:
        return ["UNSPECIFIED"]
    return sorted(found)


def _collect_repo_pull_requests(
    owner: str,
    repo: str,
    token: str | None,
    cutoff: datetime,
    max_prs: int,
) -> list[dict[str, Any]]:
    merged_pull_requests: list[dict[str, Any]] = []
    page = 1

    while len(merged_pull_requests) < max_prs:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/pulls"
            f"?state=closed&sort=updated&direction=desc&per_page=100&page={page}"
        )
        payload = _github_get(url, token)
        if not isinstance(payload, list) or not payload:
            break

        stop_pagination = False
        for pull_request in payload:
            merged_at_raw = pull_request.get("merged_at")
            if not merged_at_raw:
                continue

            merged_at = _parse_iso_datetime(str(merged_at_raw))
            if merged_at < cutoff:
                stop_pagination = True
                continue

            merged_pull_requests.append(pull_request)
            if len(merged_pull_requests) >= max_prs:
                break

        if stop_pagination:
            break

        page += 1

    return merged_pull_requests


def _build_lead_time_records(
    owner: str,
    repos: list[str],
    token: str | None,
    window_days: int,
    max_prs: int,
) -> list[PullRequestLeadTime]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=window_days)
    records: list[PullRequestLeadTime] = []

    for repo in repos:
        pull_requests = _collect_repo_pull_requests(
            owner=owner,
            repo=repo,
            token=token,
            cutoff=cutoff,
            max_prs=max_prs,
        )

        for pull_request in pull_requests:
            created_at = _parse_iso_datetime(str(pull_request["created_at"]))
            merged_at = _parse_iso_datetime(str(pull_request["merged_at"]))
            lead_hours = max((merged_at - created_at).total_seconds() / 3600.0, 0.0)

            for task_id in _extract_task_ids(pull_request):
                records.append(
                    PullRequestLeadTime(
                        repo=repo,
                        task_id=task_id,
                        pr_number=int(pull_request["number"]),
                        pr_title=str(pull_request.get("title", "")),
                        pr_url=str(pull_request.get("html_url", "")),
                        head_ref=str(pull_request.get("head", {}).get("ref", "")),
                        created_at=created_at.isoformat(),
                        merged_at=merged_at.isoformat(),
                        lead_time_hours=round(lead_hours, 2),
                    )
                )

    records.sort(key=lambda item: item.merged_at, reverse=True)
    return records


def _build_markdown_report(
    owner: str,
    repos: list[str],
    window_days: int,
    records: list[PullRequestLeadTime],
) -> str:
    generated_at = datetime.now(tz=UTC).isoformat()
    lines = [
        "# Task Lead Time Report",
        "",
        f"- Generated at (UTC): `{generated_at}`",
        f"- GitHub owner: `{owner}`",
        f"- Repositories: `{', '.join(repos)}`",
        f"- Window: last `{window_days}` days",
        "",
    ]

    if not records:
        lines.extend(
            [
                "No merged pull requests were found in the configured window.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "## Summary by Repository",
            "",
            "| Repository | PRs | Mean (h) | Median (h) | P90 (h) |",
            "|:-----------|----:|---------:|-----------:|--------:|",
        ]
    )

    for repo in repos:
        repo_records = [record for record in records if record.repo == repo]
        lead_times = [record.lead_time_hours for record in repo_records]
        if not lead_times:
            lines.append(f"| {repo} | 0 | 0.00 | 0.00 | 0.00 |")
            continue

        mean_hours = statistics.fmean(lead_times)
        median_hours = statistics.median(lead_times)
        p90_hours = _percentile(lead_times, 0.90)
        lines.append(
            f"| {repo} | {len(repo_records)} | {mean_hours:.2f} | {median_hours:.2f} | {p90_hours:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Recent Task Lead Times",
            "",
            "| Task | Repo | PR | Lead Time (h) | Created | Merged |",
            "|:-----|:-----|:---|--------------:|:--------|:-------|",
        ]
    )

    for record in records[:80]:
        pr_label = f"[#{record.pr_number}]({record.pr_url})"
        created = record.created_at.replace("+00:00", "Z")
        merged = record.merged_at.replace("+00:00", "Z")
        lines.append(
            f"| `{record.task_id}` | {record.repo} | {pr_label} | {record.lead_time_hours:.2f} | `{created}` | `{merged}` |"
        )

    longest_records = sorted(
        records,
        key=lambda item: item.lead_time_hours,
        reverse=True,
    )[:10]
    lines.extend(
        [
            "",
            "## Top 10 Longest Lead Times",
            "",
            "| Task | Repo | PR | Lead Time (h) |",
            "|:-----|:-----|:---|--------------:|",
        ]
    )

    for record in longest_records:
        pr_label = f"[#{record.pr_number}]({record.pr_url})"
        lines.append(
            f"| `{record.task_id}` | {record.repo} | {pr_label} | {record.lead_time_hours:.2f} |"
        )

    lines.append("")
    return "\n".join(lines)


def _write_report(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate task lead-time report from merged GitHub pull requests."
    )
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument(
        "--repos",
        default=",".join(DEFAULT_REPOS),
        help="Comma-separated list of repositories.",
    )
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--max-prs", type=int, default=300)
    parser.add_argument(
        "--output-md",
        default=".context/reports/task_lead_time_latest.md",
    )
    parser.add_argument(
        "--output-json",
        default=".context/reports/task_lead_time_latest.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    owner = str(args.owner).strip()
    repos = [repo.strip() for repo in str(args.repos).split(",") if repo.strip()]
    token = os.getenv("GITHUB_TOKEN", "").strip() or None

    records = _build_lead_time_records(
        owner=owner,
        repos=repos,
        token=token,
        window_days=int(args.window_days),
        max_prs=int(args.max_prs),
    )

    markdown_report = _build_markdown_report(
        owner=owner,
        repos=repos,
        window_days=int(args.window_days),
        records=records,
    )

    output_md = Path(args.output_md).resolve()
    output_json = Path(args.output_json).resolve()

    _write_report(output_md, markdown_report)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(tz=UTC).isoformat(),
                "owner": owner,
                "repos": repos,
                "window_days": int(args.window_days),
                "records": [asdict(record) for record in records],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"[lead-time] markdown: {output_md}")
    print(f"[lead-time] json: {output_json}")
    print(f"[lead-time] records: {len(records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
