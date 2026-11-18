"""Loopback-only COROS MCP consent importer. Tokens and previews stay in memory."""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import duckdb
import httpx
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.auth.exceptions import OAuthFlowError
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
from pydantic import AnyUrl, BaseModel, Field, SecretStr
from garmin_personal import fetch_activities
from normalize import parse_garmin_activities, parse_garmin_csv, parse_coros_hrv
from warehouse_import import import_payloads

BASE = Path(__file__).resolve().parent
DB = BASE / "private_data" / "coros_import.duckdb"
MOCK = os.environ.get("COROS_IMPORT_MOCK") == "1"
ENDPOINTS = {
    "global": "https://mcp.coros.com/mcp",
    "china": "https://mcpcn.coros.com/mcp",
    "europe": "https://mcpeu.coros.com/mcp",
    "us": "https://mcpus.coros.com/mcp",
}
ALLOWED_COROS_HOSTS = {urlsplit(url).hostname for url in ENDPOINTS.values()}
READ_TOOLS = {
    "activities": "querySportRecords",
    "sleep": "querySleepOverview",
    "resting_hr": "queryRestingHeartRate",
    "hrv": "querySleepHRV",
    "training_load": "queryTrainingLoadAssessment",
    "fitness": "queryFitnessAssessmentOverview",
}
FORBIDDEN_KEYS = {"name", "displayname", "nickname", "email", "phone", "birthday", "birthdate", "address", "gps", "latitude", "longitude", "lat", "lon", "lng", "route", "track", "coordinates", "avatar", "photo", "headpic"}
MAX_PAYLOAD_BYTES = 3_000_000
app = FastAPI(title="Local COROS consent importer", docs_url=None, redoc_url=None)


class MemoryTokens(TokenStorage):
    def __init__(self):
        self.tokens: OAuthToken | None = None
        self.client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self.client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self.client_info = client_info


@dataclass
class Visit:
    id: str
    status: str = "ready"
    auth_url: str | None = None
    callback: asyncio.Future | None = None
    categories: list[str] = field(default_factory=list)
    region: str = "global"
    source: str = "coros"
    participant_id: str = ""
    start_date: str = ""
    end_date: str = ""
    alias: str = ""
    preview: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    message: str = ""
    last_import_count: int = 0
    last_participant_id: str = ""
    task: asyncio.Task | None = None


VISITS: dict[str, Visit] = {}


def visit(request: Request) -> Visit:
    sid = request.cookies.get("coros_visit")
    if not sid or sid not in VISITS:
        raise HTTPException(401, "Open the home page to start a new local session")
    return VISITS[sid]


def scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k.lower().replace("_", "") not in FORBIDDEN_KEYS}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def extract(result: Any) -> Any:
    if result.structuredContent is not None:
        return scrub(result.structuredContent)
    blocks = []
    for block in result.content:
        if getattr(block, "type", None) != "text":
            continue  # No FIT binaries, images, or other attachments.
        raw = block.text
        for _ in range(2):
            try:
                raw = json.loads(raw)
            except (ValueError, TypeError):
                break
        blocks.append(scrub(raw))
    return blocks[0] if len(blocks) == 1 else blocks


def args_for(category: str, start: str, end: str, schema: dict) -> dict:
    props = schema.get("properties", {})
    args = {}
    if "startDate" in props:
        args["startDate"] = start.replace("-", "")
    if "endDate" in props:
        args["endDate"] = end.replace("-", "")
    if "days" in props and "startDate" not in props:
        args["days"] = min(30, (date.fromisoformat(end) - date.fromisoformat(start)).days + 1)
    missing = set(schema.get("required", [])) - args.keys()
    if missing:
        raise ValueError("This COROS tool requires additional fields: " + ", ".join(sorted(missing)))
    return args


async def resolve_coros_endpoint(region: str) -> str:
    """Use COROS's canonical regional MCP resource for OAuth validation."""
    requested = ENDPOINTS[region]
    metadata_url = requested.removesuffix("/mcp") + "/.well-known/oauth-protected-resource/mcp"
    async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
        response = await client.get(metadata_url, headers={"Accept": "application/json"})
        response.raise_for_status()
        resource = response.json().get("resource")
    if not isinstance(resource, str):
        raise ValueError("COROS did not provide a regional MCP address.")
    parsed = urlsplit(resource)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_COROS_HOSTS or parsed.path != "/mcp" or parsed.port or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("COROS provided an unexpected MCP address.")
    return resource


def coros_error_message(exc: BaseException) -> str:
    while isinstance(exc, BaseExceptionGroup) and exc.exceptions:
        exc = exc.exceptions[0]
    if isinstance(exc, OAuthFlowError):
        return str(exc).split("?", 1)[0][:220]
    if isinstance(exc, httpx.HTTPStatusError):
        return f"COROS returned HTTP {exc.response.status_code} during connection."
    if isinstance(exc, httpx.RequestError):
        return "Could not reach COROS. Check your connection and selected account region."
    if isinstance(exc, TimeoutError):
        return "COROS did not respond in time. Try connecting again."
    if isinstance(exc, ValueError):
        return str(exc)[:220]
    return f"COROS connection stopped ({type(exc).__name__}). Try again or change the account region."


async def gather(v: Visit) -> None:
    async def redirect(url: str) -> None:
        v.auth_url = url
        v.status = "authorize"

    async def callback() -> tuple[str, str | None]:
        v.callback = asyncio.get_running_loop().create_future()
        return await asyncio.wait_for(v.callback, timeout=300)

    tokens = MemoryTokens()
    try:
        if MOCK:
            v.preview = {c: {"example": "Synthetic preview only", "category": c} for c in v.categories}
            v.status = "preview"
            return
        endpoint = await resolve_coros_endpoint(v.region)
        auth = OAuthClientProvider(
            server_url=endpoint,
            client_metadata=OAuthClientMetadata(
                client_name="Local running data consent demo",
                redirect_uris=[AnyUrl("http://127.0.0.1:8767/oauth/callback")],
                grant_types=["authorization_code", "refresh_token"],
                response_types=["code"],
                token_endpoint_auth_method="none",
            ),
            storage=tokens,
            redirect_handler=redirect,
            callback_handler=callback,
        )
        async with httpx.AsyncClient(auth=auth, timeout=45) as client:
            async with streamable_http_client(endpoint, http_client=client) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    available = {tool.name: tool for tool in (await session.list_tools()).tools}
                    v.status = "reading"
                    for category in v.categories:
                        name = READ_TOOLS[category]
                        if name not in available:
                            v.errors[category] = "COROS did not offer this read tool"
                            continue
                        try:
                            args = args_for(category, v.start_date, v.end_date, available[name].inputSchema)
                            result = await session.call_tool(name, args)
                            if result.isError:
                                raise ValueError("COROS returned a tool error")
                            data = extract(result)
                            if category == "hrv":
                                data = {"rows": parse_coros_hrv(data)}
                            if len(json.dumps(data, ensure_ascii=False).encode()) > MAX_PAYLOAD_BYTES:
                                raise ValueError("Response exceeds the 3 MB local limit")
                            v.preview[category] = data
                        except Exception as exc:
                            v.errors[category] = str(exc)[:200]
        v.status = "preview" if v.preview else "error"
        if not v.preview:
            v.message = "No selected category could be read. Check the category errors below."
    except Exception as exc:
        v.status = "error"
        v.message = "COROS connection failed: " + coros_error_message(exc)
    finally:
        tokens.tokens = None  # No persistent access or refresh token.
        tokens.client_info = None
        v.callback = None


class Consent(BaseModel):
    alias: str = Field(min_length=1, max_length=40)
    categories: list[str] = Field(min_length=1, max_length=6)
    region: str = "global"
    start_date: date
    end_date: date
    agreed: bool
    participant_id: str = ""


class GarminPersonalConsent(BaseModel):
    api_key: SecretStr
    alias: str = Field(min_length=1, max_length=40)
    participant_id: str = ""
    start_date: date
    end_date: date
    agreed: bool


@app.get("/")
async def home(request: Request):
    response = FileResponse(BASE / "static" / "index.html")
    if request.cookies.get("coros_visit") not in VISITS:
        sid = secrets.token_urlsafe(32)
        VISITS[sid] = Visit(id=sid)
        response.set_cookie("coros_visit", sid, httponly=True, samesite="lax")
    return response


@app.get("/lineage")
async def lineage():
    return FileResponse(BASE.parent / "lineage.html", media_type="text/html")


@app.get("/api/state")
async def state(request: Request):
    v = visit(request)
    return {"status": v.status, "source": v.source, "auth_url": v.auth_url if v.status == "authorize" else None, "categories": v.categories, "errors": v.errors, "message": v.message, "last_import_count": v.last_import_count, "last_participant_id": v.last_participant_id, "mock": MOCK, "preview": {k: {"bytes": len(json.dumps(x).encode()), "top_level": list(x.keys())[:8] if isinstance(x, dict) else "list/text", "row_count": len(x.get("rows", [])) if isinstance(x, dict) else None} for k, x in v.preview.items()}}


@app.post("/api/connect")
async def connect(request: Request, consent: Consent):
    v = visit(request)
    if v.status not in {"ready", "error", "saved"}:
        raise HTTPException(409, "A connection is already in progress")
    if not consent.agreed:
        raise HTTPException(400, "Consent is required")
    if consent.region not in ENDPOINTS or not set(consent.categories) <= READ_TOOLS.keys():
        raise HTTPException(400, "Unknown region or data category")
    if consent.end_date > date.today() or consent.end_date < consent.start_date or (consent.end_date - consent.start_date).days > 30:
        raise HTTPException(400, "Choose a date range of 1 to 31 days")
    v.status, v.auth_url, v.preview, v.errors, v.message = "connecting", None, {}, {}, ""
    v.alias, v.categories, v.region = consent.alias, list(dict.fromkeys(consent.categories)), consent.region
    v.source, v.participant_id = "coros", consent.participant_id.strip()
    v.start_date, v.end_date = consent.start_date.isoformat(), consent.end_date.isoformat()
    v.task = asyncio.create_task(gather(v))
    return {"status": v.status}


@app.post("/api/garmin/upload")
async def garmin_upload(request: Request, file: UploadFile = File(...), alias: str = Form(...),
                        distance_unit: str = Form("km"), agreed: bool = Form(False),
                        participant_id: str = Form("")):
    v = visit(request)
    if v.status not in {"ready", "error", "saved"}:
        raise HTTPException(409, "An import is already in progress")
    if not agreed:
        raise HTTPException(400, "Consent is required")
    if not 1 <= len(alias.strip()) <= 40 or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Choose an alias and a Garmin activity CSV")
    data = await file.read(5_000_001)
    try:
        rows = parse_garmin_csv(data, distance_unit)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    v.source, v.participant_id, v.alias = "garmin", participant_id.strip(), alias.strip()
    v.categories, v.start_date, v.end_date = ["activities"], min(r["event_date"] for r in rows), max(r["event_date"] for r in rows)
    v.preview, v.errors, v.message, v.status = {"activities": {"rows": rows}}, {}, "", "preview"
    return {"status": "preview", "activity_count": len(rows)}


@app.post("/api/garmin/personal/preview")
async def garmin_personal_preview(request: Request, consent: GarminPersonalConsent):
    v = visit(request)
    if request.url.hostname not in {"127.0.0.1", "localhost"}:
        raise HTTPException(403, "Open the importer on this computer")
    origin = request.headers.get("origin")
    if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
        raise HTTPException(403, "Open the importer on this computer")
    if v.status not in {"ready", "error", "saved"}:
        raise HTTPException(409, "An import is already in progress")
    if not consent.agreed:
        raise HTTPException(400, "Consent is required")
    key = consent.api_key.get_secret_value().strip()
    if not key or len(key) > 512:
        raise HTTPException(400, "Enter your Garmin Personal API Key")
    if consent.end_date > date.today() or consent.end_date < consent.start_date or (consent.end_date - consent.start_date).days > 30:
        raise HTTPException(400, "Choose a date range of 1 to 31 days")
    v.source, v.status = "garmin", "reading"
    v.preview, v.errors, v.message = {}, {}, ""
    try:
        activities = await fetch_activities(key, consent.start_date, consent.end_date)
        rows = parse_garmin_activities(activities)
        if not rows:
            raise ValueError("No Garmin activities were found in this date range.")
        v.participant_id, v.alias = consent.participant_id.strip(), consent.alias.strip()
        v.categories = ["activities"]
        v.start_date, v.end_date = consent.start_date.isoformat(), consent.end_date.isoformat()
        v.preview, v.status = {"activities": {"rows": rows}}, "preview"
        return {"status": "preview", "activity_count": len(rows)}
    except ValueError as exc:
        v.status = "error"
        v.message = str(exc)
        raise HTTPException(400, v.message) from exc
    finally:
        key = ""  # The API key and bearer token are never put into Visit or disk.


@app.get("/oauth/callback")
async def oauth_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    v = visit(request)
    if not v.callback or v.callback.done():
        raise HTTPException(400, "No pending COROS authorization")
    if error or not code or not state:
        v.callback.set_exception(ValueError("Authorization was cancelled or incomplete"))
    else:
        v.callback.set_result((code, state))
    return RedirectResponse("/", status_code=303)


@app.post("/api/save")
async def save(request: Request):
    v = visit(request)
    if v.status != "preview" or not v.preview:
        raise HTTPException(409, "Nothing is ready to import")
    DB.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB)) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS participants (participant_id VARCHAR PRIMARY KEY, alias VARCHAR, consented_at TIMESTAMP, selected_categories VARCHAR, start_date DATE, end_date DATE)")
        conn.execute("CREATE TABLE IF NOT EXISTS coros_observations (participant_id VARCHAR, category VARCHAR, imported_at TIMESTAMP, payload_json VARCHAR, PRIMARY KEY(participant_id, category))")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        participant_id = v.participant_id or secrets.token_hex(16)
        existing = conn.execute("SELECT alias FROM participants WHERE participant_id=?", [participant_id]).fetchone()
        if v.participant_id and (not existing or existing[0] != v.alias):
            raise HTTPException(400, "Existing participant ID and alias do not match")
        conn.execute("BEGIN TRANSACTION")
        try:
            if not existing:
                conn.execute("INSERT INTO participants VALUES (?, ?, ?, ?, ?, ?)", [participant_id, v.alias, now, json.dumps(v.categories), v.start_date, v.end_date])
            if v.source == "coros":
                for category, payload in v.preview.items():
                    conn.execute("DELETE FROM coros_observations WHERE participant_id=? AND category=?", [participant_id, category])
                    conn.execute("INSERT INTO coros_observations VALUES (?, ?, ?, ?)", [participant_id, category, now, json.dumps(payload, ensure_ascii=False)])
            imported = import_payloads(conn, participant_id, v.source, v.preview, now)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    count = len(v.preview)
    v.preview.clear()
    v.status = "saved"
    v.last_import_count = count
    v.last_participant_id = participant_id
    v.message = f"Imported into private fitness_demo tables. Participant ID: {participant_id}"
    return {"status": v.status, "category_count": count, "participant_id": participant_id, "imported": imported}


@app.post("/api/discard")
async def discard(request: Request):
    v = visit(request)
    if v.task and not v.task.done():
        v.task.cancel()
    v.preview.clear()
    v.status = "ready"
    v.auth_url = None
    v.message = "Preview discarded; nothing was imported."
    return {"status": v.status}
