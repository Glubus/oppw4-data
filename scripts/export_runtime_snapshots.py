#!/usr/bin/env python3
"""Export sdk.runtime snapshot logs into mission evidence notes.

This tool is intentionally offline and read-only with respect to the game. It
parses copied/runtime log files, groups evidence by mission id, and appends a
compact audit section to `oppw4-data/missions/mission_XXXX/evidence.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


MISSION_RE = re.compile(r"\bmission(?:_id)?=(\d+)\b")
MODE_RE = re.compile(r"\bmode=([a-zA-Z0-9_+-]+)\b")
DIFFICULTY_RE = re.compile(r"\bdifficulty=([a-zA-Z0-9_+-]+)\b")
RANK_RE = re.compile(r"\brank=([a-zA-Z0-9_+-]+)\b")
ROW_RE = re.compile(r"\b(?:row_id|row)=([a-zA-Z0-9_x+-]+)\b")
REWARD_RE = re.compile(r"\b(?:berry|amount|reward)=([a-zA-Z0-9_x+-]+)\b")
FIXED_ID_RE = re.compile(r"\b(?:fixed_id|logical_id)=([a-zA-Z0-9_x+-]+)\b")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
RUNTIME_LINES = (
    "difficulty_probe",
    "difficulty_event",
    "rank_threshold_probe",
    "rank_helper_",
    "rank_event",
    "reward_event",
    "reward_probe",
    "result_state",
    "fixed_data_probe",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "logs",
        nargs="+",
        type=Path,
        help="Runtime log file(s) or directories containing .log files.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="oppw4-data root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print grouped evidence without writing evidence.md files.",
    )
    parser.add_argument(
        "--mission-id",
        type=int,
        action="append",
        default=[],
        help="Only export one mission id. Can be passed more than once.",
    )
    parser.add_argument(
        "--event-kind",
        action="append",
        default=[],
        choices=[
            "difficulty",
            "rank",
            "reward",
            "result",
            "fixed",
        ],
        help="Only export one event family. Can be passed more than once.",
    )
    parser.add_argument(
        "--date",
        action="append",
        default=[],
        help="Only export logs whose file name contains YYYY-MM-DD. Can be passed more than once.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON instead of evidence markdown in dry-run mode.",
    )
    return parser.parse_args()


def log_files(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(sorted(item.glob("*.log")))
        elif item.is_file():
            files.append(item)
    return files


def collect(
    files: list[Path],
    mission_ids: set[int],
    event_kinds: set[str],
    dates: set[str],
) -> dict[int, list[dict[str, object]]]:
    grouped: dict[int, list[dict[str, object]]] = {}
    for path in files:
        if dates and log_date(path) not in dates:
            continue
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not any(marker in raw for marker in RUNTIME_LINES):
                continue
            match = MISSION_RE.search(raw)
            if not match:
                continue
            mission_id = int(match.group(1))
            if mission_ids and mission_id not in mission_ids:
                continue
            entry = structured_entry(path, raw.strip(), mission_id)
            if event_kinds and entry["event_kind"] not in event_kinds:
                continue
            grouped.setdefault(mission_id, []).append(entry)
    return grouped


def log_date(path: Path) -> str:
    match = DATE_RE.search(path.name)
    return match.group(1) if match else ""


def structured_entry(path: Path, line: str, mission_id: int) -> dict[str, object]:
    return {
        "log_file": path.name,
        "log_date": log_date(path),
        "event_kind": event_kind(line),
        "mission_id": mission_id,
        "mode": first_match(MODE_RE, line),
        "difficulty": first_match(DIFFICULTY_RE, line),
        "rank": first_match(RANK_RE, line),
        "rank_rows": all_matches(ROW_RE, line) if "rank" in line else [],
        "reward_rows": all_matches(ROW_RE, line) if "reward" in line else [],
        "reward_values": all_matches(REWARD_RE, line),
        "fixed_ids": all_matches(FIXED_ID_RE, line),
        "line": line,
    }


def event_kind(line: str) -> str:
    if "fixed_data" in line:
        return "fixed"
    if "reward" in line:
        return "reward"
    if "rank_" in line or "rank=" in line:
        return "rank"
    if "difficulty" in line:
        return "difficulty"
    return "result"


def first_match(pattern: re.Pattern[str], line: str) -> str | None:
    match = pattern.search(line)
    return match.group(1) if match else None


def all_matches(pattern: re.Pattern[str], line: str) -> list[str]:
    return pattern.findall(line)


def append_evidence(
    data_root: Path,
    mission_id: int,
    entries: list[dict[str, object]],
    dry_run: bool,
) -> None:
    mission_dir = data_root / "missions" / f"mission_{mission_id:04d}"
    if dry_run:
        print(f"mission_{mission_id:04d}")
        for entry in entries:
            print(f"- {entry['log_file']}: {entry['line']}")
        return

    mission_dir.mkdir(parents=True, exist_ok=True)
    evidence = mission_dir / "evidence.md"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    block = [f"\n## Runtime Snapshot Export - {stamp}\n"]
    block.extend(f"- `{entry['log_file']}: {entry['line']}`\n" for entry in entries)
    with evidence.open("a", encoding="utf-8") as handle:
        handle.writelines(block)


def main() -> int:
    args = parse_args()
    files = log_files(args.logs)
    grouped = collect(files, set(args.mission_id), set(args.event_kind), set(args.date))
    if args.json:
        print(json.dumps(grouped, indent=2, sort_keys=True))
    else:
        for mission_id, entries in sorted(grouped.items()):
            append_evidence(args.data_root, mission_id, entries, args.dry_run)
    print(f"exported_missions={len(grouped)} log_files={len(files)} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
