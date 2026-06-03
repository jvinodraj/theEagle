#!/usr/bin/env python3
"""Auto-reply to new Strava activity comments using polling.

This script is designed for free usage in GitHub Actions (scheduled) or local cron/Task Scheduler.
It does not require any third-party Python dependencies.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


STRAVA_BASE = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"


@dataclass
class Config:
    client_id: str
    client_secret: str
    refresh_token: str
    athlete_id: int
    reply_template: str
    activity_limit: int
    dry_run: bool


@dataclass
class TokenInfo:
    access_token: str
    scopes: set[str]
    athlete_id: int | None


def _read_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name)
    if value is not None:
        value = value.strip()
        if value == "":
            value = None
    if value is None:
        value = default
    if required and (value is None or value.strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return "" if value is None else value


def load_config() -> Config:
    athlete_raw = _read_env("STRAVA_ATHLETE_ID", required=True)
    try:
        athlete_id = int(athlete_raw)
    except ValueError as exc:
        raise RuntimeError("STRAVA_ATHLETE_ID must be a numeric value.") from exc

    dry_run = _read_env("STRAVA_DRY_RUN", "false").strip().lower() in {"1", "true", "yes", "y"}

    return Config(
        client_id=_read_env("STRAVA_CLIENT_ID", required=True),
        client_secret=_read_env("STRAVA_CLIENT_SECRET", required=True),
        refresh_token=_read_env("STRAVA_REFRESH_TOKEN", required=True),
        athlete_id=athlete_id,
        reply_template=_read_env("STRAVA_REPLY_TEMPLATE", "Thanks for the comment! Ref:{comment_id}"),
        activity_limit=max(1, int(_read_env("STRAVA_ACTIVITY_LIMIT", "8"))),
        dry_run=dry_run,
    )


def _http_json(method: str, url: str, token: str | None = None, form_data: dict[str, Any] | None = None) -> Any:
    data: bytes | None = None
    headers = {"Accept": "application/json"}
    if form_data is not None:
        encoded = parse.urlencode(form_data).encode("utf-8")
        data = encoded
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {method} {url} failed: {body}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc


def refresh_access_token(cfg: Config) -> TokenInfo:
    payload = {
        "client_id": cfg.client_id,
        "client_secret": cfg.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": cfg.refresh_token,
    }
    data = _http_json("POST", TOKEN_URL, form_data=payload)
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Strava token refresh did not return access_token.")

    raw_scope = str(data.get("scope", ""))
    scopes = {scope.strip() for scope in raw_scope.split(",") if scope.strip()}

    athlete_id: int | None = None
    athlete = data.get("athlete")
    if isinstance(athlete, dict) and athlete.get("id") is not None:
        try:
            athlete_id = int(athlete["id"])
        except (TypeError, ValueError):
            athlete_id = None

    return TokenInfo(access_token=str(token), scopes=scopes, athlete_id=athlete_id)


def list_recent_activities(access_token: str, limit: int) -> list[dict[str, Any]]:
    url = f"{STRAVA_BASE}/athlete/activities?per_page={limit}&page=1"
    data = _http_json("GET", url, token=access_token)
    if not isinstance(data, list):
        raise RuntimeError("Unexpected response for athlete activities.")
    return [x for x in data if isinstance(x, dict)]


def list_activity_comments(access_token: str, activity_id: int) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    page = 1
    per_page = 200
    while True:
        url = f"{STRAVA_BASE}/activities/{activity_id}/comments?per_page={per_page}&page={page}"
        data = _http_json("GET", url, token=access_token)
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected comments response for activity {activity_id}.")
        batch = [x for x in data if isinstance(x, dict)]
        comments.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(0.15)
    return comments


def post_comment(access_token: str, activity_id: int, text: str) -> dict[str, Any]:
    url = f"{STRAVA_BASE}/activities/{activity_id}/comments"
    data = _http_json("POST", url, token=access_token, form_data={"text": text})
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected post comment response for activity {activity_id}.")
    return data


def validate_token_permissions(cfg: Config, token_info: TokenInfo) -> None:
    if token_info.athlete_id is not None and token_info.athlete_id != cfg.athlete_id:
        raise RuntimeError(
            "STRAVA_ATHLETE_ID does not match the athlete tied to the refresh token. "
            f"Expected {cfg.athlete_id}, got {token_info.athlete_id}."
        )

    if "activity:write" not in token_info.scopes:
        scope_text = ", ".join(sorted(token_info.scopes)) or "<none returned>"
        raise RuntimeError(
            "The refreshed Strava token does not include activity:write, so comment posting will fail. "
            f"Current scopes: {scope_text}. Re-authorize your Strava app and grant activity:write."
        )


def already_replied(comments: list[dict[str, Any]], athlete_id: int, source_comment_id: int) -> bool:
    marker = f"Ref:{source_comment_id}"
    for c in comments:
        athlete = c.get("athlete") if isinstance(c.get("athlete"), dict) else {}
        author_id = athlete.get("id")
        text = str(c.get("text", ""))
        if author_id == athlete_id and marker in text:
            return True
    return False


def main() -> int:
    cfg = load_config()
    token_info = refresh_access_token(cfg)
    validate_token_permissions(cfg, token_info)
    token = token_info.access_token
    activities = list_recent_activities(token, cfg.activity_limit)

    total_seen = 0
    total_replies = 0

    for activity in activities:
        activity_id_raw = activity.get("id")
        if activity_id_raw is None:
            continue
        try:
            activity_id = int(activity_id_raw)
        except (TypeError, ValueError):
            continue

        comments = list_activity_comments(token, activity_id)
        for comment in comments:
            comment_id_raw = comment.get("id")
            athlete = comment.get("athlete") if isinstance(comment.get("athlete"), dict) else {}
            author_id = athlete.get("id")

            try:
                comment_id = int(comment_id_raw)
            except (TypeError, ValueError):
                continue

            total_seen += 1

            if author_id == cfg.athlete_id:
                continue

            if already_replied(comments, cfg.athlete_id, comment_id):
                continue

            reply_text = cfg.reply_template.format(comment_id=comment_id, activity_id=activity_id)
            if cfg.dry_run:
                print(f"[DRY-RUN] activity={activity_id} comment={comment_id} reply={reply_text}")
                total_replies += 1
                continue

            try:
                post_comment(token, activity_id, reply_text)
            except RuntimeError as exc:
                message = str(exc)
                if "HTTP 401 POST" in message and "/comments" in message:
                    raise RuntimeError(
                        "Strava rejected comment creation with HTTP 401. This usually means the token was not "
                        "authorized with activity:write or the API/app is not permitted to create comments for this athlete. "
                        "Re-authorize the app with activity:write and test again in dry-run first."
                    ) from exc
                raise
            print(f"Replied to activity={activity_id} comment={comment_id}")
            total_replies += 1
            time.sleep(0.3)

    print(f"Done. scanned_comments={total_seen} replies={total_replies} activities={len(activities)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
