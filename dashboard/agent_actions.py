"""Inspect approved dashboard requests and record a local Agent's actual outcome."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "dashboard" / "private_data"
QUEUE = DATA_DIR / "approved_actions.jsonl"
RESULTS = DATA_DIR / "agent_results.jsonl"


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="Show requests and Agent outcomes")
    for name in ("complete", "blocked"):
        command = sub.add_parser(name)
        command.add_argument("request_id")
        command.add_argument("--summary", required=True)
        if name == "complete":
            command.add_argument("--plan-file", type=Path, required=True, help="Existing local draft or versioned plan artifact")
    args = parser.parse_args()
    requests = read_rows(QUEUE)
    results = read_rows(RESULTS)
    if args.command == "list":
        for request in requests:
            outcome = next((r for r in reversed(results) if r["request_id"] == request["id"]), None)
            print(json.dumps({**request, "agent_result": outcome}, ensure_ascii=False))
        return
    request = next((r for r in requests if r["id"] == args.request_id), None)
    if request is None:
        parser.error("Request not found")
    if any(r["request_id"] == args.request_id for r in results):
        parser.error("Request already has an Agent result")
    outcome = {"request_id": args.request_id, "status": args.command, "summary": args.summary,
               "recorded_at_utc": datetime.now(timezone.utc).isoformat()}
    if args.command == "complete":
        plan_file = args.plan_file.expanduser().resolve()
        if not plan_file.is_relative_to(DATA_DIR.resolve()) or not plan_file.is_file():
            parser.error("Plan artifact must exist inside dashboard/private_data/")
        try:
            plan = json.loads(plan_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parser.error("Plan artifact must be readable JSON")
        required = {"request_id": args.request_id, "athlete_id": request["athlete_id"],
                    "source_rule": request["rule_code"], "approved_action": request["action_code"],
                    "status": "draft"}
        if any(plan.get(key) != value for key, value in required.items()):
            parser.error("Plan draft must match the approved request and have draft status")
        if not isinstance(plan.get("plan_id"), str) or not isinstance(plan.get("version"), int) or plan["version"] < 1:
            parser.error("Plan draft needs a plan_id and positive integer version")
        if not isinstance(plan.get("actions"), list) or not plan["actions"]:
            parser.error("Plan draft needs at least one dated proposed action")
        if not all(isinstance(item, dict) and item.get("date") and item.get("kind") for item in plan["actions"]):
            parser.error("Each proposed action needs a date and kind")
        if not isinstance(plan.get("evidence"), list) or not plan["evidence"]:
            parser.error("Plan draft must cite checked evidence")
        outcome["plan_file"] = str(plan_file.relative_to(ROOT))
    DATA_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    with RESULTS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(outcome, ensure_ascii=False) + "\n")
    RESULTS.chmod(0o600)
    print(json.dumps(outcome, ensure_ascii=False))


if __name__ == "__main__":
    main()
