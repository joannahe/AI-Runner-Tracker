"""One-shot Garmin Personal API activity import; credentials never persist."""

from __future__ import annotations

from datetime import date

import httpx

TOKEN_URL = "https://personal.connectapi.garmin.com/personalapitoken-service/personal-api/personal-api-key/token"
ACTIVITY_URL = "https://personal.connectapi.garmin.com/activitylist-service/activities/search/activities"


async def fetch_activities(api_key: str, start: date, end: date, transport=None) -> list[dict]:
    """Exchange the user's own key, then read a bounded date window."""
    async with httpx.AsyncClient(timeout=30, transport=transport, follow_redirects=False) as client:
        try:
            token_response = await client.post(TOKEN_URL, headers={"Authorization": f"ApiKey {api_key}", "Accept": "application/json"})
            if token_response.status_code in {401, 403}:
                raise ValueError("Garmin did not accept this Personal API Key. Check or renew it in Garmin Connect.")
            token_response.raise_for_status()
            token_data = token_response.json()
            token = token_data.get("access_token") or token_data.get("accessToken")
            if not isinstance(token, str) or not token:
                raise ValueError("Garmin returned an unexpected token response.")
            rows: list[dict] = []
            for offset in range(0, 500, 100):
                response = await client.get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, params={"start": offset, "limit": 100, "startDate": start.isoformat(), "endDate": end.isoformat()})
                if response.status_code in {401, 403}:
                    raise ValueError("Garmin did not authorize reading activities with this key.")
                response.raise_for_status()
                page = response.json()
                if isinstance(page, dict):
                    page = page.get("activities")
                if not isinstance(page, list) or any(not isinstance(item, dict) for item in page):
                    raise ValueError("Garmin returned an unexpected activities format.")
                rows.extend(page)
                if len(page) < 100:
                    return rows
            raise ValueError("More than 500 activities matched. Choose a shorter date range.")
        except httpx.HTTPError as exc:
            raise ValueError("Garmin could not be reached. Check your connection and try again.") from exc
