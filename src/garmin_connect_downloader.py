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


DEFAULT_EMAIL_ENV = "GARMIN_EMAIL"
DEFAULT_PASSWORD_ENV = "GARMIN_PASSWORD"
_GARMIN_CLIENT: Any | None = None


class GarminDownloadError(RuntimeError):
    """Raised when Garmin Connect download workflow cannot proceed."""


@dataclass
class DownloadSummary:
    downloaded: list[Path]
    skipped_existing: list[Path]
    scanned: int


def _import_garminconnect():
    try:
        from garminconnect import Garmin  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise GarminDownloadError(
            "Missing optional dependency 'garminconnect'. Install dependencies and retry."
        ) from exc
    return Garmin


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


def _activity_datetime(activity: dict[str, Any]) -> datetime:
    # Prefer Garmin local start time so weekday matches the run context.
    summary = activity.get("summaryDTO") if isinstance(activity.get("summaryDTO"), dict) else {}
    metadata = activity.get("metadataDTO") if isinstance(activity.get("metadataDTO"), dict) else {}

    candidates = (
        summary.get("startTimeLocal"),
        activity.get("startTimeLocal"),
        metadata.get("startTimeLocal"),
        summary.get("startTimeGMT"),
        activity.get("startTimeGMT"),
        metadata.get("startTimeGMT"),
        summary.get("startTime"),
        activity.get("startTime"),
        metadata.get("startTime"),
    )

    for value in candidates:
        dt = _parse_timestamp(value)
        if dt:
            return dt
    return datetime.now(timezone.utc)


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


def _walk_items(value: Any) -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                items.append((key, child))
            items.extend(_walk_items(child))
    elif isinstance(value, list):
        for child in value:
            items.extend(_walk_items(child))
    return items


def _find_text_field(activity: dict[str, Any], key_tokens: tuple[str, ...]) -> str | None:
    for key, value in _walk_items(activity):
        lowered_key = key.lower()
        if any(token in lowered_key for token in key_tokens) and isinstance(value, str):
            text = value.strip()
            if text:
                return text
    return None


def _find_float_field(activity: dict[str, Any], key_tokens: tuple[str, ...]) -> float | None:
    for key, value in _walk_items(activity):
        lowered_key = key.lower()
        if any(token in lowered_key for token in key_tokens):
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    continue
    return None


def _interval_category_from_benefit(activity: dict[str, Any]) -> str:
    # Prefer Garmin's benefit/adaptation labels when present.
    benefit_text = _find_text_field(
        activity,
        (
            "primarybenefit",
            "benefit",
            "trainingeffect",
            "adaptation",
            "trainingfocus",
        ),
    )
    if benefit_text:
        benefit = benefit_text.lower()
        if "tempo" in benefit or "high aerobic" in benefit:
            return "tempo"
        if "threshold" in benefit or "lactate" in benefit:
            return "threshold"
        if "vo2" in benefit:
            return "vo2max"
        if "anaerobic" in benefit:
            return "anaerobic"
        if "sprint" in benefit:
            return "sprint"

    # Fallback for payloads that only expose numeric training effects.
    aerobic_te = _find_float_field(activity, ("total_training_effect", "aerobic_training_effect"))
    anaerobic_te = _find_float_field(activity, ("total_anaerobic_training_effect", "anaerobic_training_effect"))

    if anaerobic_te is not None and anaerobic_te >= 2.0:
        return "anaerobic"
    if aerobic_te is not None and aerobic_te >= 4.0 and (anaerobic_te is None or anaerobic_te < 1.0):
        return "tempo"
    if aerobic_te is not None and aerobic_te >= 3.0 and (anaerobic_te is None or anaerobic_te < 1.0):
        return "threshold"

    return "interval"


def _date_stamp(activity: dict[str, Any]) -> str:
    return _activity_datetime(activity).strftime("%Y-%m-%d")


def _day_of_run(activity: dict[str, Any]) -> str:
    return _activity_datetime(activity).strftime("%A").lower()


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


def _build_filename(activity: dict[str, Any], category: str) -> str:
    date_part = _date_stamp(activity)
    day_part = _day_of_run(activity)
    category_key = category.lower()
    if category_key == "interval":
        category_part = _interval_category_from_benefit(activity)
    else:
        category_part = _safe_slug(category_key, fallback="general")
    return f"{date_part}_{day_part}_{category_part}.fit"


def _require_client() -> Any:
    if _GARMIN_CLIENT is None:
        raise GarminDownloadError("Garmin client is not authenticated.")
    return _GARMIN_CLIENT


def authenticate(
    *,
    email: str | None,
    password: str | None,
    password_env: str = DEFAULT_PASSWORD_ENV,
    force_login: bool = False,
    session_root: Path = Path("."),
) -> None:
    del force_login
    del session_root

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

    Garmin = _import_garminconnect()
    client = Garmin(resolved_email, resolved_password)
    client.login()

    global _GARMIN_CLIENT
    _GARMIN_CLIENT = client


def _fetch_activities_page(start: int, limit: int) -> list[dict[str, Any]]:
    client = _require_client()
    response = client.get_activities(start=start, limit=limit)

    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        activities = response.get("activities")
        if isinstance(activities, list):
            return [item for item in activities if isinstance(item, dict)]

    return []


def _fetch_activity(activity_id: int) -> dict[str, Any]:
    client = _require_client()
    response = client.get_activity(str(activity_id))
    if isinstance(response, dict):
        return response
    raise GarminDownloadError(f"Unable to fetch metadata for activity {activity_id}")


def _download_fit_bytes(activity_id: int) -> bytes:
    client = _require_client()

    try:
        payload = client.download_activity(
            str(activity_id),
            client.ActivityDownloadFormat.ORIGINAL,
        )
    except Exception as exc:
        raise GarminDownloadError(f"Unable to download activity {activity_id}") from exc

    if isinstance(payload, bytes):
        return _extract_fit_payload(payload)
    if hasattr(payload, "content"):
        return _extract_fit_payload(bytes(payload.content))

    raise GarminDownloadError(f"Unexpected download response type for activity {activity_id}")


def download_activity_fit(
    *,
    activity_id: int,
    category: str,
    output_dir: Path,
    overwrite: bool,
) -> tuple[Path, bool]:
    output_dir.mkdir(parents=True, exist_ok=True)
    activity = _fetch_activity(activity_id)
    filename = _build_filename(activity, category)
    out_path = output_dir / filename

    if out_path.exists() and not overwrite:
        return out_path, False

    fit_payload = _download_fit_bytes(activity_id)
    out_path.write_bytes(fit_payload)
    return out_path, True


def get_health_snapshot(date: str) -> dict[str, Any]:
    """
    Fetch health snapshot for a specific date.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dictionary containing health metrics (body battery, stress, HR, HRV, SpO2, etc.)
    """
    client = _require_client()
    if hasattr(client, "get_health_snapshot"):
        return client.get_health_snapshot(date)

    snapshot: dict[str, Any] = {}

    # Newer garminconnect versions expose per-domain endpoints instead of
    # get_health_snapshot; merge what is available into one daily payload.
    for method_name in (
        "get_stats_and_body",
        "get_stats",
        "get_sleep_data",
        "get_stress_data",
        "get_hrv_data",
        "get_all_day_stress",
    ):
        method = getattr(client, method_name, None)
        if method is None:
            continue
        data = method(date)
        if isinstance(data, dict):
            snapshot[method_name] = data

    body_battery_method = getattr(client, "get_body_battery", None)
    if body_battery_method is not None:
        body_battery_data = body_battery_method(date, date)
        if body_battery_data:
            snapshot["get_body_battery"] = body_battery_data

    return snapshot


def get_health_snapshots_range(
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    """
    Fetch health snapshots for a date range.
    
    The Garmin API works per-date, so this iterates through each day and fetches snapshots.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of dictionaries containing daily health metrics
    """
    from datetime import datetime, timedelta
    
    client = _require_client()
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    snapshots = []
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        try:
            if hasattr(client, "get_health_snapshot"):
                snapshot = client.get_health_snapshot(date_str)
            else:
                snapshot = get_health_snapshot(date_str)
            if snapshot:
                snapshots.append({"date": date_str, **snapshot})
        except Exception as exc:
            # Log warning but continue fetching remaining dates
            print(f"Warning: Could not fetch snapshot for {date_str}: {exc}")
        current += timedelta(days=1)
    
    return snapshots


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

            filename = _build_filename(activity, category)
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
