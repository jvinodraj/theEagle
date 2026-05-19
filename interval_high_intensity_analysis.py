from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.fit_parser import FitParser

DEFAULT_INTERVAL_DIR = Path("data/activities/interval/raw")
DEFAULT_EASY_CSV = Path("reports/easy/hr_improvement_analysis.csv")
DEFAULT_OUTPUT_DIR = Path("reports/interval")
LOCAL_TIMEZONE = "Asia/Kolkata"


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return None


def _safe_timestamp(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value)
        if pd.isna(ts):
            return None
        return ts
    except Exception:
        return None


def _as_naive(ts: pd.Timestamp | None) -> pd.Timestamp | None:
    if ts is None:
        return None
    # FIT `start_time` values can arrive as naive UTC; normalize all timestamps to
    # local time before removing timezone info so date labels stay on the right day.
    if ts.tzinfo is None:
        return ts.tz_localize("UTC").tz_convert(LOCAL_TIMEZONE).tz_localize(None)
    if ts.tzinfo is not None:
        return ts.tz_convert(LOCAL_TIMEZONE).tz_localize(None)
    return ts


def _session_type_from_name(name: str) -> str:
    lower = name.lower()
    if "threshold" in lower:
        return "threshold"
    if "tempo" in lower:
        return "tempo"
    if "speed" in lower:
        return "speed"
    if "interval" in lower:
        return "interval"
    return "high_intensity_running"


def _get_col(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for col in candidates:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(index=df.index, dtype=float)


def _detect_work_intervals(laps: pd.DataFrame) -> pd.Series:
    speed = _get_col(laps, ["enhanced_avg_speed", "avg_speed", "speed"])
    power = _get_col(laps, ["avg_power", "enhanced_avg_power"])
    hr = _get_col(laps, ["avg_heart_rate"])
    dur = _get_col(laps, ["total_timer_time", "total_elapsed_time"])

    metrics = pd.DataFrame(index=laps.index)
    metrics["speed"] = speed
    metrics["power"] = power
    metrics["hr"] = hr
    metrics["dur"] = dur

    valid = metrics.dropna(how="all", subset=["speed", "power", "hr"])
    if valid.empty:
        return pd.Series(False, index=laps.index)

    speed_thr = np.nanpercentile(valid["speed"].dropna(), 60) if valid["speed"].notna().any() else np.nan
    power_thr = np.nanpercentile(valid["power"].dropna(), 60) if valid["power"].notna().any() else np.nan
    hr_thr = np.nanpercentile(valid["hr"].dropna(), 60) if valid["hr"].notna().any() else np.nan

    is_work = pd.Series(False, index=laps.index)
    if not np.isnan(speed_thr):
        is_work = is_work | (metrics["speed"] >= speed_thr)
    if not np.isnan(power_thr):
        is_work = is_work | (metrics["power"] >= power_thr)
    if not np.isnan(hr_thr):
        is_work = is_work | (metrics["hr"] >= hr_thr)

    is_work = is_work & (metrics["dur"].fillna(0) >= 30)

    # If nearly all laps are classified work, keep top half by speed as work.
    if is_work.mean() > 0.8 and metrics["speed"].notna().sum() >= 4:
        rank = metrics["speed"].rank(pct=True)
        is_work = rank >= 0.5

    return is_work.fillna(False)


def _hr_response_lag(interval_records: pd.DataFrame) -> float | None:
    if interval_records.empty or "heart_rate" not in interval_records.columns or "timestamp" not in interval_records.columns:
        return None

    df = interval_records.dropna(subset=["timestamp", "heart_rate"]).copy()
    if df.empty:
        return None

    peak_hr = float(df["heart_rate"].max())
    target = 0.9 * peak_hr
    start_ts = pd.to_datetime(df["timestamp"].iloc[0])
    reached = df[df["heart_rate"] >= target]
    if reached.empty:
        return None

    t_reach = pd.to_datetime(reached.iloc[0]["timestamp"])
    return float((t_reach - start_ts).total_seconds())


def _hr_recovery_60s(recovery_records: pd.DataFrame, prior_peak_hr: float | None) -> float | None:
    if recovery_records.empty or prior_peak_hr is None:
        return None
    if "heart_rate" not in recovery_records.columns:
        return None

    rec = recovery_records.dropna(subset=["heart_rate"]).copy()
    if rec.empty:
        return None

    first_min = rec.head(60)
    if first_min.empty:
        return None

    min_60 = float(first_min["heart_rate"].min())
    return float(prior_peak_hr - min_60)


def _pace_from_speed(speed_mps: float | None) -> float | None:
    if speed_mps is None or speed_mps <= 0:
        return None
    return 1000.0 / (speed_mps * 60.0)


def _classify_threshold_zone(hr: pd.Series, threshold_hr: float | None) -> pd.Series:
    if threshold_hr is None:
        return pd.Series(False, index=hr.index)
    return hr.between(threshold_hr - 5.0, threshold_hr + 5.0)


def _compute_environment_flags(session_row: pd.Series) -> str:
    avg_temp = _safe_float(session_row.get("avg_temperature"))
    max_temp = _safe_float(session_row.get("max_temperature"))
    if avg_temp is None and max_temp is None:
        return "no_temperature_data"

    avg_t = avg_temp if avg_temp is not None else max_temp
    if avg_t is None:
        return "no_temperature_data"
    if avg_t >= 28:
        return "heat_stress_possible"
    if avg_t <= 8:
        return "cold_conditions_possible"
    return "moderate_conditions"


def _build_interval_rows(parser: FitParser, fit_file: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    record_df = parser.records.copy()
    lap_df = parser._dfs.get("lap", pd.DataFrame()).copy()
    session_df = parser.session.copy()
    zones_df = parser._dfs.get("zones_target", pd.DataFrame()).copy()
    profile_df = parser._dfs.get("user_profile", pd.DataFrame()).copy()

    if session_df.empty:
        return pd.DataFrame(), {}

    session_row = session_df.iloc[0]
    session_ts = _safe_timestamp(session_row.get("timestamp") or session_row.get("start_time"))
    session_ts = _as_naive(session_ts)

    threshold_hr = None
    ftp = None
    if not zones_df.empty:
        threshold_hr = _safe_float(zones_df.iloc[0].get("threshold_heart_rate"))
        ftp = _safe_float(zones_df.iloc[0].get("functional_threshold_power"))

    body_weight = None
    if not profile_df.empty:
        body_weight = _safe_float(profile_df.iloc[0].get("weight"))

    duration_sec = _safe_float(session_row.get("total_timer_time") or session_row.get("total_elapsed_time"))
    duration_min = round(duration_sec / 60.0, 1) if duration_sec is not None else np.nan
    total_distance_km = round((_safe_float(session_row.get("total_distance")) or 0.0) / 1000.0, 2)

    avg_hr = _safe_float(session_row.get("avg_heart_rate"))
    max_hr = _safe_float(session_row.get("max_heart_rate"))
    avg_power = _safe_float(session_row.get("avg_power"))
    max_power = _safe_float(session_row.get("max_power"))
    te_aerobic = _safe_float(session_row.get("total_training_effect"))
    te_anaerobic = _safe_float(session_row.get("total_anaerobic_training_effect"))

    warmup_min = np.nan
    if not lap_df.empty:
        work_mask = _detect_work_intervals(lap_df)
        if work_mask.any():
            warmup_sec = _get_col(lap_df.loc[~work_mask], ["total_timer_time", "total_elapsed_time"]).sum()
            warmup_min = round(float(warmup_sec) / 60.0, 1)

    interval_rows: list[dict[str, Any]] = []

    if not lap_df.empty and "start_time" in lap_df.columns and "timestamp" in lap_df.columns:
        work_mask = _detect_work_intervals(lap_df)
        work_laps = lap_df[work_mask].copy()
        rec_laps = lap_df[~work_mask].copy()

        for idx, (_, lap) in enumerate(work_laps.iterrows(), start=1):
            start = _as_naive(_safe_timestamp(lap.get("start_time")))
            end = _as_naive(_safe_timestamp(lap.get("timestamp")))
            if start is None or end is None or record_df.empty:
                lap_records = pd.DataFrame()
            else:
                ts = pd.to_datetime(record_df.get("timestamp"), errors="coerce")
                ts = ts.dt.tz_localize(None) if hasattr(ts.dt, "tz") and ts.dt.tz is not None else ts
                lap_records = record_df[(ts >= start) & (ts <= end)].copy()

            rec_start = end
            rec_end = None
            if idx < len(work_laps):
                next_start = _as_naive(_safe_timestamp(work_laps.iloc[idx].get("start_time")))
                rec_end = next_start
            recovery_records = pd.DataFrame()
            if rec_start is not None and rec_end is not None and not record_df.empty:
                ts = pd.to_datetime(record_df.get("timestamp"), errors="coerce")
                ts = ts.dt.tz_localize(None) if hasattr(ts.dt, "tz") and ts.dt.tz is not None else ts
                recovery_records = record_df[(ts >= rec_start) & (ts < rec_end)].copy()

            pace = _pace_from_speed(_safe_float(lap.get("enhanced_avg_speed") or lap.get("avg_speed")))
            avg_hr_i = _safe_float(lap.get("avg_heart_rate"))
            max_hr_i = _safe_float(lap.get("max_heart_rate"))
            avg_power_i = _safe_float(lap.get("avg_power"))
            cadence_i = _safe_float(lap.get("avg_running_cadence") or lap.get("avg_cadence"))
            stride_i = _safe_float(lap.get("avg_step_length"))
            if stride_i is not None:
                stride_i = stride_i / 1000.0
            gct_i = _safe_float(lap.get("avg_stance_time"))
            vo_i = _safe_float(lap.get("avg_vertical_oscillation"))

            peak_hr_i = max_hr_i
            if peak_hr_i is None and not lap_records.empty and "heart_rate" in lap_records.columns:
                peak_hr_i = _safe_float(lap_records["heart_rate"].max())

            interval_rows.append(
                {
                    "file": fit_file.name,
                    "date": session_ts,
                    "session_type": _session_type_from_name(fit_file.name),
                    "interval_index": idx,
                    "interval_duration_s": _safe_float(lap.get("total_timer_time") or lap.get("total_elapsed_time")),
                    "recovery_duration_s": _safe_float(rec_laps.get("total_timer_time", pd.Series(dtype=float)).mean()) if not rec_laps.empty else np.nan,
                    "pace_min_per_km": pace,
                    "avg_hr": avg_hr_i,
                    "max_hr": max_hr_i,
                    "avg_power": avg_power_i,
                    "cadence_spm": cadence_i,
                    "stride_length_m": stride_i,
                    "ground_contact_time_ms": gct_i,
                    "vertical_oscillation_mm": vo_i,
                    "hr_response_lag_s": _hr_response_lag(lap_records),
                    "hr_recovery_60s_bpm": _hr_recovery_60s(recovery_records, peak_hr_i),
                }
            )

    interval_df = pd.DataFrame(interval_rows)

    time_near_threshold_s = np.nan
    threshold_pace = np.nan
    threshold_power = np.nan
    pace_sustainability_pct = np.nan
    power_consistency_cv_pct = np.nan
    power_fade_pct = np.nan
    cadence_collapse_pct = np.nan
    form_deterioration_pct = np.nan

    if not record_df.empty:
        hr_series = pd.to_numeric(record_df.get("heart_rate"), errors="coerce")
        near_thr = _classify_threshold_zone(hr_series, threshold_hr)
        time_near_threshold_s = float(near_thr.sum()) if not near_thr.empty else np.nan

        if near_thr.any() and "speed" in record_df.columns:
            thr_speed = pd.to_numeric(record_df.loc[near_thr, "speed"], errors="coerce").dropna().median()
            threshold_pace = _pace_from_speed(float(thr_speed)) if pd.notna(thr_speed) else np.nan

        if near_thr.any() and "power" in record_df.columns:
            thr_pwr = pd.to_numeric(record_df.loc[near_thr, "power"], errors="coerce").dropna().median()
            threshold_power = float(thr_pwr) if pd.notna(thr_pwr) else np.nan

    if not interval_df.empty:
        first = interval_df.iloc[0]
        last = interval_df.iloc[-1]
        p1 = _safe_float(first.get("pace_min_per_km"))
        p2 = _safe_float(last.get("pace_min_per_km"))
        if p1 and p1 > 0 and p2 is not None:
            pace_sustainability_pct = (p2 / p1 - 1.0) * 100.0

        powers = pd.to_numeric(interval_df.get("avg_power"), errors="coerce").dropna()
        if not powers.empty and powers.mean() > 0:
            power_consistency_cv_pct = float((powers.std() / powers.mean()) * 100.0)
            if len(powers) >= 2:
                power_fade_pct = float((powers.iloc[-1] / powers.iloc[0] - 1.0) * 100.0)

        cads = pd.to_numeric(interval_df.get("cadence_spm"), errors="coerce").dropna()
        if len(cads) >= 2 and cads.iloc[0] > 0:
            cadence_collapse_pct = float((cads.iloc[-1] / cads.iloc[0] - 1.0) * 100.0)

        vos = pd.to_numeric(interval_df.get("vertical_oscillation_mm"), errors="coerce").dropna()
        if len(vos) >= 2 and vos.iloc[0] > 0:
            form_deterioration_pct = float((vos.iloc[-1] / vos.iloc[0] - 1.0) * 100.0)

    avg_speed = _safe_float(session_row.get("enhanced_avg_speed") or session_row.get("avg_speed"))
    pace_total = _pace_from_speed(avg_speed)

    wkg = np.nan
    if avg_power is not None and body_weight is not None and body_weight > 0:
        wkg = avg_power / body_weight

    workout_summary = {
        "file": fit_file.name,
        "date": session_ts,
        "session_type": _session_type_from_name(fit_file.name),
        "warmup_duration_min": warmup_min,
        "interval_count": int(len(interval_df)),
        "interval_duration_mean_s": float(interval_df["interval_duration_s"].mean()) if not interval_df.empty else np.nan,
        "recovery_duration_mean_s": float(interval_df["recovery_duration_s"].mean()) if not interval_df.empty else np.nan,
        "total_workout_duration_min": duration_min,
        "total_distance_km": total_distance_km,
        "threshold_pace_min_per_km": threshold_pace,
        "threshold_hr_bpm": threshold_hr,
        "threshold_power_w": threshold_power if not pd.isna(threshold_power) else ftp,
        "time_near_threshold_s": time_near_threshold_s,
        "pace_sustainability_pct": pace_sustainability_pct,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "peak_hr": max_hr,
        "hr_response_lag_s": float(pd.to_numeric(interval_df.get("hr_response_lag_s"), errors="coerce").mean()) if not interval_df.empty else np.nan,
        "hr_recovery_between_reps_bpm": float(pd.to_numeric(interval_df.get("hr_recovery_60s_bpm"), errors="coerce").mean()) if not interval_df.empty else np.nan,
        "cardiac_drift_bpm": np.nan if record_df.empty else float(pd.to_numeric(record_df.get("heart_rate"), errors="coerce").tail(max(1, len(record_df)//5)).mean() - pd.to_numeric(record_df.get("heart_rate"), errors="coerce").head(max(1, len(record_df)//5)).mean()),
        "avg_power": avg_power,
        "peak_power": max_power,
        "power_consistency_cv_pct": power_consistency_cv_pct,
        "w_per_kg": wkg,
        "power_fade_pct": power_fade_pct,
        "aerobic_training_effect": te_aerobic,
        "anaerobic_training_effect": te_anaerobic,
        "exercise_load": _safe_float(session_row.get("exercise_load") or session_row.get("training_load")),
        "recovery_recommendation_h": _safe_float(session_row.get("recovery_time")),
        "vo2max_estimate": _safe_float(session_row.get("enhanced_avg_respiration_rate")),
        "pace_fade_pct": pace_sustainability_pct,
        "hr_escalation_bpm": np.nan if record_df.empty else float(pd.to_numeric(record_df.get("heart_rate"), errors="coerce").tail(max(1, len(record_df)//4)).mean() - pd.to_numeric(record_df.get("heart_rate"), errors="coerce").head(max(1, len(record_df)//4)).mean()),
        "cadence_collapse_pct": cadence_collapse_pct,
        "form_deterioration_pct": form_deterioration_pct,
        "environment_flag": _compute_environment_flags(session_row),
        "garmin_estimated_fields": "threshold_hr_bpm, threshold_power_w, training_effect, anaerobic_training_effect, recovery_recommendation_h, vo2max_estimate",
    }

    return interval_df, workout_summary


def _compute_longitudinal(workouts: pd.DataFrame) -> pd.DataFrame:
    if workouts.empty:
        return pd.DataFrame()

    df = workouts.sort_values("date").copy()
    df["threshold_pace_trend_pct"] = df["threshold_pace_min_per_km"].pct_change(fill_method=None) * 100.0
    df["threshold_hr_trend_pct"] = df["threshold_hr_bpm"].pct_change(fill_method=None) * 100.0
    df["threshold_power_trend_pct"] = df["threshold_power_w"].pct_change(fill_method=None) * 100.0
    df["repeatability_trend_pct"] = -df["power_consistency_cv_pct"].pct_change(fill_method=None) * 100.0
    df["vo2_adaptation_proxy_trend_pct"] = df["aerobic_training_effect"].pct_change(fill_method=None) * 100.0
    df["recovery_efficiency_trend_pct"] = df["hr_recovery_between_reps_bpm"].pct_change(fill_method=None) * 100.0
    df["anaerobic_tolerance_trend_pct"] = df["anaerobic_training_effect"].pct_change(fill_method=None) * 100.0
    return df


def _write_markdown_report(workouts: pd.DataFrame, intervals: pd.DataFrame, longitudinal: pd.DataFrame, out_file: Path) -> None:
    lines: list[str] = []
    lines.append("# Interval / Threshold / Speed Adaptation Report")
    lines.append("")
    lines.append("This report separates direct measurements from Garmin estimates and emphasizes trends over single-session claims.")
    lines.append("")

    if workouts.empty:
        lines.append("No interval workouts found in the configured folder.")
        out_file.write_text("\n".join(lines), encoding="utf-8")
        return

    for _, w in workouts.sort_values("date").iterrows():
        lines.append(f"## Workout: {w['file']} ({pd.to_datetime(w['date']).strftime('%Y-%m-%d')})")
        lines.append("")
        lines.append("### 1. Executive Summary")
        lines.append(f"- Session type: {w['session_type']}")
        lines.append(f"- Total duration: {w['total_workout_duration_min']} min, distance: {w['total_distance_km']} km")
        lines.append(f"- Primary adaptation signal: Aerobic TE {w['aerobic_training_effect']}, Anaerobic TE {w['anaerobic_training_effect']}")
        lines.append(f"- Fatigue signal: Pace fade {w['pace_fade_pct'] if pd.notna(w['pace_fade_pct']) else 'n/a'}%, HR escalation {w['hr_escalation_bpm'] if pd.notna(w['hr_escalation_bpm']) else 'n/a'} bpm")
        lines.append("")

        lines.append("### 2. Workout Structure Breakdown")
        lines.append(f"- Warmup duration: {w['warmup_duration_min']} min")
        lines.append(f"- Interval count: {int(w['interval_count'])}")
        lines.append(f"- Mean interval duration: {w['interval_duration_mean_s']} s")
        lines.append(f"- Mean recovery duration: {w['recovery_duration_mean_s']} s")
        lines.append("")

        lines.append("### 3. Interval-by-Interval Analysis")
        sub = intervals[intervals['file'] == w['file']]
        if sub.empty:
            lines.append("- No interval-level lap segmentation was detected reliably for this file")
        else:
            for _, r in sub.iterrows():
                lines.append(
                    f"- Rep {int(r['interval_index'])}: pace {round(r['pace_min_per_km'], 2) if pd.notna(r['pace_min_per_km']) else 'n/a'} min/km, "
                    f"HR {r['avg_hr']}/{r['max_hr']}, power {r['avg_power']}, cadence {r['cadence_spm']}, "
                    f"stride {r['stride_length_m']}, GCT {r['ground_contact_time_ms']}, VO {r['vertical_oscillation_mm']}"
                )
        lines.append("")

        lines.append("### 4. Threshold Interpretation")
        lines.append(f"- Threshold pace: {w['threshold_pace_min_per_km'] if pd.notna(w['threshold_pace_min_per_km']) else 'n/a'} min/km")
        lines.append(f"- Threshold HR: {w['threshold_hr_bpm'] if pd.notna(w['threshold_hr_bpm']) else 'n/a'} bpm (Garmin estimate)")
        lines.append(f"- Threshold power: {w['threshold_power_w'] if pd.notna(w['threshold_power_w']) else 'n/a'} W (Garmin estimate or proxy)")
        lines.append(f"- Time near threshold: {w['time_near_threshold_s'] if pd.notna(w['time_near_threshold_s']) else 'n/a'} s")
        lines.append(f"- Pace sustainability: {w['pace_sustainability_pct'] if pd.notna(w['pace_sustainability_pct']) else 'n/a'}%")
        lines.append("")

        lines.append("### 5. VO2/Speed Adaptation Analysis")
        lines.append(f"- Avg power: {w['avg_power']}, peak power: {w['peak_power']}")
        lines.append(f"- Power consistency CV: {w['power_consistency_cv_pct'] if pd.notna(w['power_consistency_cv_pct']) else 'n/a'}%")
        lines.append(f"- W/kg: {w['w_per_kg'] if pd.notna(w['w_per_kg']) else 'n/a'}")
        lines.append("- VO2 conclusion: use trend context only; single-session certainty is low")
        lines.append("")

        lines.append("### 6. Fatigue Analysis")
        lines.append(f"- Power fade: {w['power_fade_pct'] if pd.notna(w['power_fade_pct']) else 'n/a'}%")
        lines.append(f"- Cadence collapse: {w['cadence_collapse_pct'] if pd.notna(w['cadence_collapse_pct']) else 'n/a'}%")
        lines.append(f"- Form deterioration (vertical oscillation shift): {w['form_deterioration_pct'] if pd.notna(w['form_deterioration_pct']) else 'n/a'}%")
        lines.append("")

        lines.append("### 7. Recovery Assessment")
        lines.append(f"- HR response lag: {w['hr_response_lag_s'] if pd.notna(w['hr_response_lag_s']) else 'n/a'} s")
        lines.append(f"- HR recovery between reps: {w['hr_recovery_between_reps_bpm'] if pd.notna(w['hr_recovery_between_reps_bpm']) else 'n/a'} bpm")
        lines.append(f"- Cardiac drift: {w['cardiac_drift_bpm'] if pd.notna(w['cardiac_drift_bpm']) else 'n/a'} bpm")
        lines.append(f"- Environment impact flag: {w['environment_flag']}")
        lines.append("")

        lines.append("### 8. Training Recommendations")
        lines.append("- Keep one clear objective per workout: threshold durability or VO2 repeatability")
        lines.append("- If pace fade >3% or power fade >3%, reduce next session intensity or volume")
        lines.append("- If HR recovery between reps declines across weeks, extend recovery intervals")
        lines.append("")

        lines.append("### 9. Risks/Warnings")
        lines.append("- Garmin-derived metrics are estimates and should not be treated as direct lab measurements")
        lines.append("- Missing running-dynamics fields lower certainty for neuromuscular conclusions")
        lines.append("")

    lines.append("## Longitudinal Tracking")
    if longitudinal.empty:
        lines.append("- Not enough sessions for trend analysis")
    else:
        latest = longitudinal.sort_values("date").iloc[-1]
        lines.append(f"- Latest threshold pace trend: {latest['threshold_pace_trend_pct'] if pd.notna(latest['threshold_pace_trend_pct']) else 'n/a'}%")
        lines.append(f"- Latest threshold HR trend: {latest['threshold_hr_trend_pct'] if pd.notna(latest['threshold_hr_trend_pct']) else 'n/a'}%")
        lines.append(f"- Latest threshold power trend: {latest['threshold_power_trend_pct'] if pd.notna(latest['threshold_power_trend_pct']) else 'n/a'}%")
        lines.append(f"- Latest repeatability trend: {latest['repeatability_trend_pct'] if pd.notna(latest['repeatability_trend_pct']) else 'n/a'}%")

    lines.append("")
    lines.append("## Suggested Graphs/Charts")
    lines.append("- Threshold pace and threshold HR over time")
    lines.append("- Interval rep pace/power scatter by workout")
    lines.append("- HR recovery between reps trend")
    lines.append("- Power fade and pace fade trend")
    lines.append("- Cadence vs stride length under high-intensity stress")

    lines.append("")
    lines.append("## Research-Paper-Ready Observations")
    lines.append("- Results should be interpreted as field-derived signals rather than direct metabolic laboratory measures")
    lines.append("- Adaptation inferences are stronger when repeated trends align across pacing, HR dynamics, and power consistency")
    lines.append("- Environmental and sensor-quality constraints should be disclosed in any external interpretation")

    out_file.write_text("\n".join(lines), encoding="utf-8")


def analyze_interval_workouts(interval_dir: Path, easy_csv: Path, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    fit_files = sorted(interval_dir.glob("*.fit")) if interval_dir.exists() else []

    workout_rows: list[dict[str, Any]] = []
    interval_frames: list[pd.DataFrame] = []

    for fit_file in fit_files:
        parser = FitParser(fit_file)
        parser.parse()
        interval_df, workout = _build_interval_rows(parser, fit_file)
        if workout:
            workout_rows.append(workout)
        if not interval_df.empty:
            interval_frames.append(interval_df)

    workouts_df = pd.DataFrame(workout_rows)
    intervals_df = pd.concat(interval_frames, ignore_index=True) if interval_frames else pd.DataFrame()

    if not workouts_df.empty:
        workouts_df = workouts_df.sort_values("date").reset_index(drop=True)

    longitudinal_df = _compute_longitudinal(workouts_df)

    workout_csv = output_dir / "interval_workouts_dataset.csv"
    interval_csv = output_dir / "interval_level_dataset.csv"
    longitudinal_csv = output_dir / "interval_longitudinal_tracking.csv"
    report_md = output_dir / "interval_adaptation_report.md"

    workouts_df.to_csv(workout_csv, index=False)
    intervals_df.to_csv(interval_csv, index=False)
    longitudinal_df.to_csv(longitudinal_csv, index=False)
    _write_markdown_report(workouts_df, intervals_df, longitudinal_df, report_md)

    return {
        "workout_csv": workout_csv,
        "interval_csv": interval_csv,
        "longitudinal_csv": longitudinal_csv,
        "report_md": report_md,
    }


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze interval/threshold/speed FIT workouts")
    parser.add_argument("--interval-dir", type=Path, default=DEFAULT_INTERVAL_DIR, help="Directory containing interval FIT files")
    parser.add_argument("--easy-csv", type=Path, default=DEFAULT_EASY_CSV, help="Optional easy-run CSV (reserved for future coupling)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    return parser


def main() -> int:
    args = build_cli().parse_args()
    outputs = analyze_interval_workouts(
        interval_dir=args.interval_dir,
        easy_csv=args.easy_csv,
        output_dir=args.output_dir,
    )
    print("Generated outputs:")
    for _, path in outputs.items():
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
