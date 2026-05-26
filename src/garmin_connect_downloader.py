from __future__ import annotations

import os
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from getpass import getpass
from io import BytesIO
from pathlib import Path
from typing import Any


SESSION_FILE = ".garth"
DEFAULT_EMAIL_ENV = "GARMIN_EMAIL"
DEFAULT_PASSWORD_ENV = "GARMIN_PASSWORD"


class GarminDownloadError(RuntimeError):
    """Raised when Garmin Connect download workflow cannot proceed."""


@dataclass
class DownloadSummary:
    downloaded: list[Path]
    skipped_existing: list[Path]
    scanned: int


def _import_garth():
    try:
        import garth  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise GarminDownloadError(
            "Missing optional dependency 'garth'. Install dependencies and retry."
        ) from exc
    return garth


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    candidates = (
        value,
        value.replace("Z", "+00:00"),
        value + "+00:00" if value.endswith("Z") is False and "+" not in value else value,
    )

    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def _activity_type_key(activity: dict[str, Any]) -> str:
    activity_type = activity.get("activityType")
    if isinstance(activity_type, dict):
        type_key = activity_type.get("typeKey")
        if type_key:
            return str(type_key).lower()
    return ""


def _matches_category(activity: dict[str, Any], category: str) -> bool:
    category = category.lower()
    type_key = _activity_type_key(activity)

    if category == "strength":
        return "strength" in type_key

    if category in {"easy", "interval"}:
        # Garmin API does not reliably tag easy vs interval sessions at this endpoint.
        # For category-based routing, both map to running-family activities.
        return any(token in type_key for token in ("running", "trail_running", "treadmill"))

    if category == "general":
        return True

    # For custom categories, avoid dropping data: accept all activities.
    return True


def _safe_slug(value: str, fallback: str = "activity") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or fallback


def _date_stamp(activity: dict[str, Any]) -> str:
    for key in ("startTimeLocal", "startTimeGMT", "startTime"):
        dt = _parse_timestamp(activity.get(key))
        if dt:
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _extract_fit_payload(payload: bytes) -> bytes:
    # Garmin sometimes returns a zip payload. Use the first .fit entry if present.
    if payload[:2] != b"PK":
        return payload

    try:
        with zipfile.ZipFile(BytesIO(payload)) as zf:
            fit_members = [name for name in zf.namelist() if name.lower().endswith(".fit")]
            if not fit_members:
                raise GarminDownloadError("Downloaded zip does not contain a .fit file.")
            with zf.open(fit_members[0]) as fh:
                return fh.read()
    except zipfile.BadZipFile:
        return payload


def _build_filename(activity: dict[str, Any], activity_id: int) -> str:
    date_part = _date_stamp(activity)
    type_part = _safe_slug(_activity_type_key(activity), fallback="unknown")
    return f"{date_part}_{type_part}_{activity_id}.fit"


def _session_path(root: Path) -> Path:
    return root / SESSION_FILE


def authenticate(
    *,
    email: str | None,
    password: str | None,
    password_env: str = DEFAULT_PASSWORD_ENV,
    force_login: bool = False,
    session_root: Path = Path("."),
) -> None:
    garth = _import_garth()
    session_path = _session_path(session_root)

    if not force_login and session_path.exists():
        try:
            garth.resume(str(session_path))
            return
        except Exception:
            pass

    resolved_email = email or os.getenv(DEFAULT_EMAIL_ENV)
    resolved_password = password or os.getenv(password_env)

    if not resolved_email:
        raise GarminDownloadError(
            f"Missing Garmin email. Set {DEFAULT_EMAIL_ENV} or pass --email."
        )

    if not resolved_password:
        try:
            resolved_password = getpass("Garmin password: ")
        except Exception as exc:
            raise GarminDownloadError(
                f"Missing Garmin password. Set {password_env} or run interactively."
            ) from exc

    if not resolved_password:
        raise GarminDownloadError("Garmin password is empty.")

    garth.login(resolved_email, resolved_password)
    # Persist session for future non-interactive downloads.
    garth.save(str(session_path))


def _fetch_activities_page(start: int, limit: int) -> list[dict[str, Any]]:
    garth = _import_garth()
    response = garth.connectapi(
        "/activitylist-service/activities/search/activities",
        params={"start": start, "limit": limit},
    )

    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        activities = response.get("activities")
        if isinstance(activities, list):
            return [item for item in activities if isinstance(item, dict)]

    return []


def _download_fit_bytes(activity_id: int) -> bytes:
    garth = _import_garth()

    endpoints = (
        f"/download-service/files/activity/{activity_id}",
        f"/download-service/export/original-activity/{activity_id}",
    )

    last_error: Exception | None = None
    for endpoint in endpoints:
        try:
            payload = garth.download(endpoint)
            if isinstance(payload, bytes):
                return _extract_fit_payload(payload)
            if hasattr(payload, "content"):
                return _extract_fit_payload(bytes(payload.content))
            raise GarminDownloadError(f"Unexpected download response type for {endpoint}")
        except Exception as exc:
            last_error = exc

    raise GarminDownloadError(f"Unable to download activity {activity_id}") from last_error


def download_activity_fit(
    *,
    activity_id: int,
    output_dir: Path,
    overwrite: bool,
    filename: str | None = None,
) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / (filename or f"{activity_id}.fit")

    if out_path.exists() and not overwrite:
        return None

    fit_payload = _download_fit_bytes(activity_id)
    out_path.write_bytes(fit_payload)
    return out_path


def download_recent_fits(
    *,
    category: str,
    output_dir: Path,
    days: int,
    limit: int,
    overwrite: bool,
    page_size: int = 100,
    max_scan: int = 1000,
) -> DownloadSummary:
    if days < 1:
        raise GarminDownloadError("--days must be >= 1")
    if limit < 1:
        raise GarminDownloadError("--limit must be >= 1")

    output_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    scanned = 0
    downloaded: list[Path] = []
    skipped_existing: list[Path] = []

    start = 0
    while len(downloaded) < limit and scanned < max_scan:
        page = _fetch_activities_page(start=start, limit=page_size)
        if not page:
            break

        start += page_size

        for activity in page:
            scanned += 1
            if scanned > max_scan:
                break

            dt = _parse_timestamp(
                activity.get("startTimeGMT") or activity.get("startTimeLocal") or activity.get("startTime")
            )
            if dt and dt < cutoff:
                # Activities are returned newest first; safe to stop early.
                return DownloadSummary(downloaded=downloaded, skipped_existing=skipped_existing, scanned=scanned)

            if not _matches_category(activity, category):
                continue

            activity_id = activity.get("activityId")
            if not isinstance(activity_id, int):
                continue

            filename = _build_filename(activity, activity_id)
            path = output_dir / filename

            if path.exists() and not overwrite:
                skipped_existing.append(path)
                continue

            fit_payload = _download_fit_bytes(activity_id)
            path.write_bytes(fit_payload)
            downloaded.append(path)

            if len(downloaded) >= limit:
                break

    return DownloadSummary(downloaded=downloaded, skipped_existing=skipped_existing, scanned=scanned)
