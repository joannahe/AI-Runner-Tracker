"""Conservative, source-aware parsing into the public fitness_demo grain.

Missing measurements remain NULL. Unknown input formats raise a useful error
instead of silently inventing pace, training zones, or race status.
"""

from __future__ import annotations

import csv
from datetime import datetime
from hashlib import sha256
from io import StringIO
import re
from typing import Any


def fingerprint(*parts: Any) -> str:
    return sha256("|".join(str(x) for x in parts).encode()).hexdigest()[:24]


def number(text: str | None) -> float | None:
    if text is None or str(text).strip() in {"", "--", "-", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(text).replace(",", ""))
    return float(match.group()) if match else None


def seconds(text: str | None) -> int | None:
    if not text:
        return None
    value = str(text).strip()
    match = re.search(r"(?<!\d)(\d{1,3}:\d{2}(?::\d{2})?)(?!\d)", value)
    if not match:
        return None
    pieces = [int(x) for x in match.group(1).split(":")]
    if len(pieces) == 2:
        return pieces[0] * 60 + pieces[1]
    return pieces[0] * 3600 + pieces[1] * 60 + pieces[2]


def minutes(text: str | None) -> int | None:
    if not text:
        return None
    h = re.search(r"(\d+)\s*h", text, re.I)
    m = re.search(r"(\d+)\s*m(?:in)?\b", text, re.I)
    if h or m:
        return (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)
    return None


def labeled(line: str, key: str) -> str | None:
    match = re.search(r"(?:^|\|)\s*" + re.escape(key) + r":\s*([^|\n]+)", line, re.I | re.M)
    return match.group(1).strip() if match else None


def parse_coros_activities(text: str) -> list[dict[str, Any]]:
    blocks = re.split(r"(?m)^\s*\d+\.\s+([^\n]+?)\s+[—–-]\s+(\d{4}-\d{2}-\d{2})\s*$", text)
    rows = []
    for i in range(1, len(blocks), 3):
        title, event_date, body = blocks[i:i+3]
        duration = seconds(labeled(body, "Duration"))
        km = number(labeled(body, "Distance"))
        if duration is None or km is None:
            continue  # No reliable run duration/distance means no semantic run fact.
        label_id = labeled(body, "LabelId")
        start = re.search(r"startTimestamp=(\d{10,13})", body)
        source_id = label_id or fingerprint(event_date, title, duration, km, start.group(1) if start else "")
        avg_hr = number(labeled(body, "Avg HR"))
        cadence = number(labeled(body, "Avg Cadence"))
        power = number(labeled(body, "Avg Power"))
        rows.append({
            "source": "coros", "source_activity_id": str(source_id),
            "event_date": event_date, "sport_code": "running" if "run" in title.lower() else "other",
            "duration_s": duration, "distance_m": round(km * 1000),
            "avg_hr_bpm": round(avg_hr) if avg_hr is not None else None,
            "avg_cadence_spm": round(cadence) if cadence is not None else None,
            "avg_power_w": round(power) if power is not None else None,
            "calories_kcal": round(number(labeled(body, "Calories"))) if number(labeled(body, "Calories")) is not None else None,
            "started_at_utc": datetime.utcfromtimestamp(int(start.group(1)[:10])) if start else None,
        })
    return rows


def parse_coros_training_load(text: str) -> list[dict[str, Any]]:
    chunks = re.split(r"(?m)^(\d{4}-\d{2}-\d{2})\s*$", text)
    rows = []
    for i in range(1, len(chunks), 2):
        day, body = chunks[i:i+2]
        short, long = number(labeled(body, "Short-Term Load")), number(labeled(body, "Long-Term Load"))
        if short is None and long is None:
            continue
        rows.append({"local_date": day, "short_term_load": round(short) if short is not None else None,
                     "long_term_load": round(long) if long is not None else None,
                     "load_ratio": number(labeled(body, "Load Ratio")),
                     "provider_status": labeled(body, "Comment")})
    return rows


def parse_coros_sleep(text: str) -> list[dict[str, Any]]:
    chunks = re.split(r"(?m)^(\d{4}-\d{2}-\d{2})\s*$", text)
    rows = []
    for i in range(1, len(chunks), 2):
        day, body = chunks[i:i+2]
        score, daily, main = number(labeled(body, "Sleep Score")), minutes(labeled(body, "Daily Sleep")), minutes(labeled(body, "Main Sleep (asleep)"))
        if score is None and daily is None and main is None:
            continue
        def pct(label):
            return number(labeled(body, label))
        rows.append({"wake_date": day, "sleep_score": score, "source_score_raw": labeled(body, "Sleep Score"),
                     "daily_sleep_min": daily, "main_sleep_min": main,
                     "main_period_min": minutes(labeled(body, "Main Sleep Period (incl. awake)")),
                     "nap_sleep_min": minutes(labeled(body, "Naps Total")),
                     "deep_pct": pct("Deep Sleep Ratio"), "light_pct": pct("Light Sleep Ratio"),
                     "rem_pct": pct("REM Ratio"), "awake_pct": pct("Awake Ratio"),
                     "awake_min": minutes(labeled(body, "Awake Time")),
                     "awake_count": round(pct("Awake Count (>5 min)")) if pct("Awake Count (>5 min)") is not None else None,
                     "metrics_scope": labeled(body, "Sleep metrics scope"), "data_status": "present"})
    return rows


def parse_coros_hrv(payload: Any) -> list[dict[str, Any]]:
    """Keep COROS's official daily assessment; do not recompute it from raw points."""
    if isinstance(payload, dict):
        if isinstance(payload.get("rows"), list):
            return payload["rows"]
        payload = payload.get("text", "")
    if isinstance(payload, list):
        payload = "\n".join(str(part) for part in payload)
    text = str(payload)
    assessment = text.split("Sleep HRV Time Series", 1)[0]
    day_pattern = re.compile(r"(?m)^(\d{4}-\d{2}-\d{2}):\s*$")
    found = list(day_pattern.finditer(assessment))
    rows = []
    for index, match in enumerate(found):
        day = match.group(1)
        body = assessment[match.end():found[index + 1].start() if index + 1 < len(found) else len(assessment)]
        avg = re.search(r"HRV Avg:\s*(\d+(?:\.\d+)?)\s*ms\s*[—–-]\s*([^\n]+)", body)
        normal = re.search(r"Normal Range:\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*ms", body)
        baseline = re.search(r"Baseline:\s*(\d+(?:\.\d+)?)\s*ms", body)
        if not avg:
            continue
        label = avg.group(2).strip().lower().replace(" ", "_")
        if label not in {"normal", "below_normal", "above_normal", "low"}:
            label = "unknown"
        rows.append({"wake_date": day, "hrv_avg_ms": float(avg.group(1)),
                     "normal_low_ms": float(normal.group(1)) if normal else None,
                     "normal_high_ms": float(normal.group(2)) if normal else None,
                     "baseline_ms": float(baseline.group(1)) if baseline else None,
                     "provider_evaluation": label, "data_status": "present"})
    if not rows:
        raise ValueError("COROS returned no readable official daily HRV assessments")
    return rows


def parse_coros_resting_hr(text: str) -> list[dict[str, Any]]:
    rows = []
    for day, bpm in re.findall(r"(?m)^(\d{4}-\d{2}-\d{2}):\s*(\d+)\s*bpm\s*$", text):
        rows.append({"local_date": day, "rhr_bpm": int(bpm), "data_status": "present"})
    return rows


def parse_coros_fitness(text: str) -> list[dict[str, Any]]:
    metrics = [("VO2max", "vo2max_running", "ml/kg/min"),
               ("Threshold Pace", "threshold_pace_s_per_km", "s/km"),
               ("Threshold HR", "threshold_hr_bpm", "bpm")]
    rows = []
    for label, code, unit in metrics:
        raw = labeled(text, label)
        if raw is None:
            continue
        value = seconds(raw) if unit == "s/km" else number(raw)
        if value is not None:
            rows.append({"metric_code": code, "metric_value": value, "unit": unit})
    return rows


def parse_garmin_csv(data: bytes, distance_unit: str = "km") -> list[dict[str, Any]]:
    if distance_unit not in {"km", "mi"}:
        raise ValueError("Distance unit must be km or mi")
    if len(data) > 5_000_000:
        raise ValueError("CSV exceeds the 5 MB local limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Please export the CSV in UTF-8") from exc
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV has no header")
    headers = {re.sub(r"[^a-z0-9]", "", h.lower()): h for h in reader.fieldnames if h}
    def get(record, *names):
        for name in names:
            col = headers.get(re.sub(r"[^a-z0-9]", "", name.lower()))
            if col and record.get(col):
                return str(record[col]).strip()
        return None
    if not get(dict.fromkeys(reader.fieldnames, "x"), "Date", "Start Time") or not get(dict.fromkeys(reader.fieldnames, "x"), "Distance", "Distance (km)", "Distance (mi)"):
        raise ValueError("Expected Garmin activity CSV columns including Date and Distance")
    rows = []
    for line_no, record in enumerate(reader, 2):
        raw_date = get(record, "Date", "Start Time")
        start = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%b %d, %Y, %I:%M:%S %p", "%b %d, %Y, %I:%M %p", "%m/%d/%Y %I:%M:%S %p"):
            try:
                start = datetime.strptime(raw_date, fmt)
                break
            except (TypeError, ValueError):
                pass
        if start is None:
            raise ValueError(f"Row {line_no}: unsupported date format")
        duration = seconds(get(record, "Time", "Moving Time", "Elapsed Time", "Duration"))
        raw_distance = get(record, "Distance", "Distance (km)", "Distance (mi)")
        km = number(raw_distance)
        if duration is None or km is None:
            raise ValueError(f"Row {line_no}: duration or distance is missing")
        unit = "mi" if "distance(mi)" in headers or " mi" in raw_distance.lower() else "km" if "distance(km)" in headers or " km" in raw_distance.lower() else distance_unit
        metres = round(km * (1609.344 if unit == "mi" else 1000))
        title = get(record, "Activity Type", "Type", "Title") or ""
        source_id = get(record, "Activity ID", "ActivityId", "ID") or fingerprint(start.isoformat(), duration, metres, title)
        def rounded(*keys):
            v = number(get(record, *keys))
            return round(v) if v is not None else None
        rows.append({"source": "garmin", "source_activity_id": source_id,
                     "event_date": start.date().isoformat(), "started_at_local": start.isoformat(sep=" ") if start.time().isoformat() != "00:00:00" else None,
                     "sport_code": "running" if "run" in title.lower() else "other", "duration_s": duration,
                     "distance_m": metres, "avg_hr_bpm": rounded("Avg HR", "Average Heart Rate"),
                     "avg_cadence_spm": rounded("Avg Run Cadence", "Average Cadence", "Avg Cadence"),
                     "avg_power_w": rounded("Avg Power", "Average Power"), "calories_kcal": rounded("Calories")})
    if not rows:
        raise ValueError("CSV contains no activity rows")
    return rows


def parse_garmin_activities(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only activity measurements used by the local semantic model."""
    rows = []
    for index, activity in enumerate(activities, 1):
        source_id = activity.get("activityId") or activity.get("activityUUID")
        raw_start = activity.get("startTimeLocal") or activity.get("startTimeGMT")
        if not source_id or not isinstance(raw_start, str):
            raise ValueError(f"Garmin activity {index} is missing an ID or start time.")
        try:
            started = datetime.fromisoformat(raw_start.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Garmin activity {index} has an unsupported start time.") from exc
        duration = number(activity.get("duration"))
        distance = number(activity.get("distance"))
        if duration is None or distance is None or duration < 0 or distance < 0:
            raise ValueError(f"Garmin activity {index} is missing duration or distance.")
        activity_type = activity.get("activityType") or {}
        if isinstance(activity_type, dict):
            activity_type = activity_type.get("typeKey") or activity_type.get("typeId") or ""
        sport = str(activity_type).lower()
        def rounded(*names):
            for name in names:
                value = number(activity.get(name))
                if value is not None:
                    return round(value)
            return None
        rows.append({
            "source": "garmin", "source_activity_id": str(source_id),
            "event_date": started.date().isoformat(), "started_at_local": started.replace(tzinfo=None).isoformat(sep=" "),
            "sport_code": "running" if "run" in sport else "other",
            "duration_s": round(duration), "distance_m": round(distance),
            "avg_hr_bpm": rounded("averageHR", "averageHeartRate"),
            "avg_cadence_spm": rounded("averageRunningCadenceInStepsPerMinute", "averageRunningCadence", "averageCadence"),
            "avg_power_w": rounded("averagePower"), "calories_kcal": rounded("calories"),
        })
    return rows
