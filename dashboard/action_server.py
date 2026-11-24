"""Serve the local dashboard and record athlete-approved requests for an Agent.

The server never edits an approved plan. A connected Agent must verify evidence,
apply a requested change to a versioned local plan, and acknowledge completion.
"""

from __future__ import annotations

import argparse
import json
import secrets
from datetime import date, datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from build import render_dashboard

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "dashboard" / "private_data"
QUEUE = DATA_DIR / "approved_actions.jsonl"
RESULTS = DATA_DIR / "agent_results.jsonl"
def current_rules() -> dict:
    return yaml.safe_load((ROOT / "fitness_ontology.yaml").read_text(encoding="utf-8"))["ai_context"]["ai_context"]["ai_context"]["x_coaching_knowledge"]
HOST = "127.0.0.1"
PORT = 8768
SESSION = secrets.token_urlsafe(32)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        # URLs and headers are intentionally absent from the log.
        print("dashboard:", fmt % args)

    def send_json(self, code: int, value: dict) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except Exception:
            return False
        return cookie.get("runner_session") is not None and secrets.compare_digest(cookie["runner_session"].value, SESSION)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/ontology-rules" and self.authorized():
            self.send_json(HTTPStatus.OK, current_rules())
            return
        if path in ("/", "/dashboard", "/demo"):
            try:
                if path == "/demo":
                    body = (ROOT / "dashboard" / "index.html").read_bytes()
                else:
                    # A refresh re-reads the latest DuckDB rows and ontology rules.
                    body = render_dashboard(personal=True)[0].encode("utf-8")
            except Exception as exc:
                print(f"dashboard: refresh failed: {type(exc).__name__}: {exc}")
                self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Dashboard data unavailable"})
                return
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", f"runner_session={SESSION}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/action-session" and self.authorized():
            self.send_json(HTTPStatus.OK, {"available": True, "token": SESSION})
            return
        if path == "/api/approved-actions" and self.authorized():
            rows = [json.loads(line) for line in QUEUE.read_text(encoding="utf-8").splitlines()] if QUEUE.exists() else []
            results = {row["request_id"]: row for row in (json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines())} if RESULTS.exists() else {}
            for row in rows:
                if row["id"] in results:
                    row["agent_result"] = results[row["id"]]
            self.send_json(HTTPStatus.OK, {"actions": rows[-50:]})
            return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/approved-actions":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        expected_origin = f"http://{HOST}:{PORT}"
        if (not self.authorized() or self.headers.get("Origin") != expected_origin
                or self.headers.get("X-Action-Token") != SESSION
                or self.headers.get("Content-Type", "").split(";")[0] != "application/json"):
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Open the local dashboard first"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("Invalid request size")
            value = json.loads(self.rfile.read(length))
            rule = value["rule_code"]
            action = value["action_code"]
            athlete = value["athlete_id"]
            observed = value["observation_date"]
            proposed_change = value.get("proposed_change", "")
            date.fromisoformat(observed)
            if not all(isinstance(v, str) and 0 < len(v) <= 100 for v in (rule, action, athlete, observed)):
                raise ValueError("Invalid fields")
            if not isinstance(proposed_change, str) or len(proposed_change) > 1000:
                raise ValueError("Invalid proposed change")
            allowed_actions = {r["code"]: set(r.get("recommendation_options", [])) for r in current_rules()["inference_states"]}
            if action not in allowed_actions.get(rule, set()):
                raise ValueError("Action is not defined for that ontology rule")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        DATA_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        request = {
            "id": secrets.token_urlsafe(16),
            "status": "approved_waiting_for_agent",
            "approved_at_utc": datetime.now(timezone.utc).isoformat(),
            "athlete_id": athlete,
            "rule_code": rule,
            "action_code": action,
            "observation_date": observed,
            "proposed_change": proposed_change,
            "ontology_file": "fitness_ontology.yaml",
            "ontology_extension": "ai_context.x_coaching_knowledge",
            "note": "Agent must recheck evidence and target plan before making a versioned change.",
        }
        with QUEUE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(request, ensure_ascii=False) + "\n")
        QUEUE.chmod(0o600)
        self.send_json(HTTPStatus.ACCEPTED, {"id": request["id"], "status": request["status"]})


def main() -> None:
    global PORT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    PORT = args.port
    with ThreadingHTTPServer((HOST, PORT), Handler) as server:
        print(f"Open http://{HOST}:{PORT}/dashboard (or /demo)")
        server.serve_forever()


if __name__ == "__main__":
    main()
