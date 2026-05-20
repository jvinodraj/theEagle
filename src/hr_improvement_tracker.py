from __future__ import annotations

import logging
import argparse
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.fit_parser import FitParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EASY_RUNS_DIR = Path("data/activities/easy/raw")
LEGACY_EASY_RUNS_DIR = Path("data/easy_runs")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)
CSV_REPORT_PATH = REPORT_DIR / "hr_improvement_analysis.csv"
PLOT_REPORT_PATH = REPORT_DIR / "hr_improvement_plot.png"
TIMELINE_REPORT_PATH = REPORT_DIR / "hr_timeline_report.md"
STEADY_STATE_START_M = 2000.0
STEADY_STATE_MAX_START_M = 3000.0
MOVING_SPEED_THRESHOLD_MPS = 0.5
HR_ZONE_PCT_BOUNDS = (0.60, 0.70, 0.80, 0.90)
POWER_ZONE_PCT_BOUNDS = (0.55, 0.75, 0.90, 1.05)

# ── International scoring reference ranges ─────────────────────────────────
# Efficiency Factor (EF) = power / HR in W/bpm  (Joe Friel / TrainingPeaks)
# Reference: 0.9 W/bpm (beginner) → 2.0 W/bpm (well-trained)
EF_REF_MIN: float = 0.9
EF_REF_MAX: float = 2.0

# Aerobic Decoupling threshold (Garmin / Joe Friel standard)
# <5% = aerobically fit for that distance
DECOUPLING_FIT_PCT: float = 5.0


def resolve_easy_runs_dir(fit_dir: Path | None = None) -> Path:
    if fit_dir is not None:
        return fit_dir
    if EASY_RUNS_DIR.exists() and any(EASY_RUNS_DIR.glob("*.fit")):
        return EASY_RUNS_DIR
    if LEGACY_EASY_RUNS_DIR.exists() and any(LEGACY_EASY_RUNS_DIR.glob("*.fit")):
        return LEGACY_EASY_RUNS_DIR
    if EASY_RUNS_DIR.exists():
        return EASY_RUNS_DIR
    if LEGACY_EASY_RUNS_DIR.exists():
        return LEGACY_EASY_RUNS_DIR
    return EASY_RUNS_DIR


def configure_report_paths(report_dir: Path | None = None) -> None:
    global REPORT_DIR, CSV_REPORT_PATH, PLOT_REPORT_PATH, TIMELINE_REPORT_PATH
    if report_dir is not None:
        REPORT_DIR = report_dir
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_REPORT_PATH = REPORT_DIR / "hr_improvement_analysis.csv"
    PLOT_REPORT_PATH = REPORT_DIR / "hr_improvement_plot.png"
    TIMELINE_REPORT_PATH = REPORT_DIR / "hr_timeline_report.md"


def extract_date_from_filename(filename: str) -> datetime | None:
    try:
        date_str = filename.split("_")[0]
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, IndexError):
        return None


def choose_activity_date(session_row: pd.Series, fit_file: Path) -> tuple[datetime | None, bool]:
    session_ts = session_row.get("timestamp")
    start_time = session_row.get("start_time")
    activity_ts = session_ts if pd.notna(session_ts) else start_time

    if pd.isna(activity_ts):
        return extract_date_from_filename(fit_file.name), False

    activity_ts = pd.to_datetime(activity_ts)
    canonical_date = activity_ts.tz_localize(None) if activity_ts.tzinfo else activity_ts

    filename_date = extract_date_from_filename(fit_file.name)
    filename_mismatch = bool(
        filename_date is not None and filename_date.date() != canonical_date.date()
    )
    return canonical_date, filename_mismatch


def pace_from_speed(speed_mps: float) -> float | None:
    if pd.isna(speed_mps) or speed_mps <= 0:
        return None
    return 1000 / (speed_mps * 60)


def pct_change(first_value: float, last_value: float) -> float | None:
    if pd.isna(first_value) or pd.isna(last_value) or first_value == 0:
        return None
    return ((last_value / first_value) - 1) * 100


def lower_is_better_change(first_value: float, last_value: float) -> float | None:
    if pd.isna(first_value) or pd.isna(last_value) or last_value == 0:
        return None
    return ((first_value / last_value) - 1) * 100


def format_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:+.1f}%"


def calculate_aerobic_drift(records_df: pd.DataFrame) -> float | None:
    if records_df.empty or "heart_rate" not in records_df.columns or "speed" not in records_df.columns:
        return None

    filtered = records_df.dropna(subset=["heart_rate", "speed"]).copy()
    filtered = filtered[filtered["speed"] > MOVING_SPEED_THRESHOLD_MPS]
    if len(filtered) < 20:
        return None

    midpoint = len(filtered) // 2
    first_half = filtered.iloc[:midpoint]
    second_half = filtered.iloc[midpoint:]

    first_ratio = first_half["speed"].mean() / first_half["heart_rate"].mean()
    second_ratio = second_half["speed"].mean() / second_half["heart_rate"].mean()
    if first_ratio <= 0 or second_ratio <= 0:
        return None

    return abs(((second_ratio / first_ratio) - 1) * 100)


def duration_bucket(duration_min: float) -> str:
    if pd.isna(duration_min):
        return "unknown"
    if duration_min < 40:
        return "short_easy"
    if duration_min <= 55:
        return "standard_easy"
    return "long_easy"


def clip_score(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return float(np.clip(value, lower, upper))


def select_steady_state_records(records_df: pd.DataFrame) -> tuple[pd.DataFrame, float, float]:
    filtered = records_df.dropna(subset=["distance", "heart_rate", "speed"]).copy()
    filtered = filtered[filtered["speed"] > MOVING_SPEED_THRESHOLD_MPS]
    if filtered.empty:
        return filtered, 0.0, 0.0

    total_distance = float(filtered["distance"].max())
    start_m = min(STEADY_STATE_MAX_START_M, max(STEADY_STATE_START_M, total_distance * 0.25))
    end_m = total_distance * 0.95 if total_distance >= 4000 else total_distance

    steady = filtered[(filtered["distance"] >= start_m) & (filtered["distance"] <= end_m)].copy()
    if len(steady) < 120:
        steady = filtered[filtered["distance"] >= min(STEADY_STATE_START_M, total_distance * 0.2)].copy()
    if len(steady) < 120:
        start_idx = int(len(filtered) * 0.2)
        end_idx = max(start_idx + 1, int(len(filtered) * 0.95))
        steady = filtered.iloc[start_idx:end_idx].copy()
    return steady, start_m, end_m


def summarize_steady_state(records_df: pd.DataFrame) -> dict:
    steady, start_m, end_m = select_steady_state_records(records_df)
    if steady.empty:
        return {
            "steady_start_km": np.nan,
            "steady_end_km": np.nan,
            "steady_avg_hr": np.nan,
            "steady_avg_speed_mps": np.nan,
            "steady_pace_min_per_km": np.nan,
            "steady_avg_power": np.nan,
            "steady_speed_per_hr": np.nan,
            "steady_power_per_hr": np.nan,
            "steady_hr_rise_bpm": np.nan,
            "steady_hr_std": np.nan,
        }

    steady_avg_hr = float(steady["heart_rate"].mean())
    steady_avg_speed = float(steady["speed"].mean())
    steady_avg_power = float(steady["power"].dropna().mean()) if "power" in steady.columns else np.nan
    midpoint = len(steady) // 2
    first_half = steady.iloc[:midpoint]
    second_half = steady.iloc[midpoint:]
    hr_rise = float(second_half["heart_rate"].mean() - first_half["heart_rate"].mean()) if midpoint > 0 else np.nan

    return {
        "steady_start_km": round(start_m / 1000, 2),
        "steady_end_km": round(end_m / 1000, 2),
        "steady_avg_hr": round(steady_avg_hr, 1),
        "steady_avg_speed_mps": round(steady_avg_speed, 3),
        "steady_pace_min_per_km": round(pace_from_speed(steady_avg_speed), 2) if pace_from_speed(steady_avg_speed) is not None else np.nan,
        "steady_avg_power": round(steady_avg_power, 1) if not pd.isna(steady_avg_power) else np.nan,
        "steady_speed_per_hr": round(steady_avg_speed / steady_avg_hr, 5) if steady_avg_hr else np.nan,
        "steady_power_per_hr": round(steady_avg_power / steady_avg_hr, 3) if steady_avg_hr and not pd.isna(steady_avg_power) else np.nan,
        "steady_hr_rise_bpm": round(hr_rise, 1) if not pd.isna(hr_rise) else np.nan,
        "steady_hr_std": round(float(steady["heart_rate"].std()), 1) if len(steady) > 1 else np.nan,
    }


def round_or_nan(value, digits: int = 2) -> float:
    if value is None or pd.isna(value):
        return np.nan
    return round(float(value), digits)


def get_message_row(parser: FitParser, message_name: str) -> pd.Series | None:
    df = parser._dfs.get(message_name)
    if df is None or df.empty:
        return None
    return df.iloc[0]


def get_active_records(records_df: pd.DataFrame) -> pd.DataFrame:
    if records_df.empty or "speed" not in records_df.columns:
        return pd.DataFrame()
    active = records_df.dropna(subset=["speed"]).copy()
    return active[active["speed"] > MOVING_SPEED_THRESHOLD_MPS]


def calculate_ratio_decoupling(records_df: pd.DataFrame, numerator_col: str) -> float | None:
    if records_df.empty or "heart_rate" not in records_df.columns or numerator_col not in records_df.columns:
        return None

    filtered = records_df.dropna(subset=["heart_rate", numerator_col]).copy()
    if numerator_col == "speed":
        filtered = filtered[filtered["speed"] > MOVING_SPEED_THRESHOLD_MPS]
    else:
        filtered = filtered[filtered[numerator_col] > 0]
    if len(filtered) < 20:
        return None

    midpoint = len(filtered) // 2
    first_half = filtered.iloc[:midpoint]
    second_half = filtered.iloc[midpoint:]
    first_ratio = first_half[numerator_col].mean() / first_half["heart_rate"].mean()
    second_ratio = second_half[numerator_col].mean() / second_half["heart_rate"].mean()
    if first_ratio <= 0 or second_ratio <= 0:
        return None
    return abs(((second_ratio / first_ratio) - 1) * 100)


def calculate_variability_pct(records_df: pd.DataFrame, column: str) -> float | None:
    if records_df.empty or column not in records_df.columns:
        return None
    values = records_df[column].dropna()
    if len(values) < 20 or values.mean() == 0:
        return None
    return float(values.std() / values.mean() * 100)


def calculate_pace_durability(records_df: pd.DataFrame) -> float | None:
    active = get_active_records(records_df)
    if len(active) < 30:
        return None

    chunk_len = max(10, len(active) // 3)
    first_chunk = active.iloc[:chunk_len]
    last_chunk = active.iloc[-chunk_len:]
    first_speed = first_chunk["speed"].mean()
    last_speed = last_chunk["speed"].mean()
    if first_speed <= 0 or last_speed <= 0:
        return None

    first_pace = pace_from_speed(first_speed)
    last_pace = pace_from_speed(last_speed)
    if first_pace is None or last_pace is None or first_pace == 0:
        return None
    return ((last_pace / first_pace) - 1) * 100


def calculate_recovery_hr_60s(records_df: pd.DataFrame, events_df: pd.DataFrame) -> float | None:
    if records_df.empty or events_df.empty or "heart_rate" not in records_df.columns or "timestamp" not in records_df.columns:
        return None

    timer_events = events_df[(events_df.get("event") == "timer") & (events_df.get("event_type") == "stop")]
    if timer_events.empty or "timestamp" not in timer_events.columns:
        return None

    stop_time = pd.to_datetime(timer_events["timestamp"].max())
    records = records_df.dropna(subset=["timestamp", "heart_rate"]).copy()
    if records.empty:
        return None

    pre_stop = records[records["timestamp"] <= stop_time]
    post_stop = records[records["timestamp"] >= stop_time + pd.Timedelta(seconds=55)]
    if pre_stop.empty or post_stop.empty:
        return None

    end_hr = float(pre_stop.iloc[-1]["heart_rate"])
    hr_60s = float(post_stop.iloc[0]["heart_rate"])
    return end_hr - hr_60s


def build_zone_distribution(series: pd.Series, bounds: tuple[float, float, float, float], scale: float) -> dict:
    values = series.dropna()
    if values.empty or scale <= 0:
        return {}

    ratios = values / scale
    total = len(ratios)
    counts = {
        "z1": int((ratios < bounds[0]).sum()),
        "z2": int(((ratios >= bounds[0]) & (ratios < bounds[1])).sum()),
        "z3": int(((ratios >= bounds[1]) & (ratios < bounds[2])).sum()),
        "z4": int(((ratios >= bounds[2]) & (ratios < bounds[3])).sum()),
        "z5": int((ratios >= bounds[3]).sum()),
    }
    distribution: dict[str, float] = {}
    for zone_name, count in counts.items():
        distribution[f"{zone_name}_sec"] = count
        distribution[f"{zone_name}_pct"] = round(count / total * 100, 1)
    return distribution


def summarize_hr_zone2(records_df: pd.DataFrame, max_hr_setting: float | None) -> dict:
    if records_df.empty or pd.isna(max_hr_setting) or "heart_rate" not in records_df.columns:
        return {
            "zone2_duration_min": np.nan,
            "zone2_avg_hr": np.nan,
            "zone2_pace_min_per_km": np.nan,
            "zone2_avg_power": np.nan,
        }

    lower = max_hr_setting * HR_ZONE_PCT_BOUNDS[0]
    upper = max_hr_setting * HR_ZONE_PCT_BOUNDS[1]
    zone2 = records_df.dropna(subset=["heart_rate", "speed"]).copy()
    zone2 = zone2[(zone2["speed"] > MOVING_SPEED_THRESHOLD_MPS) & (zone2["heart_rate"] >= lower) & (zone2["heart_rate"] < upper)]
    if zone2.empty:
        return {
            "zone2_duration_min": 0.0,
            "zone2_avg_hr": np.nan,
            "zone2_pace_min_per_km": np.nan,
            "zone2_avg_power": np.nan,
        }

    mean_speed = zone2["speed"].mean()
    return {
        "zone2_duration_min": round(len(zone2) / 60, 1),
        "zone2_avg_hr": round_or_nan(zone2["heart_rate"].mean(), 1),
        "zone2_pace_min_per_km": round_or_nan(pace_from_speed(mean_speed), 2),
        "zone2_avg_power": round_or_nan(zone2["power"].dropna().mean(), 1) if "power" in zone2.columns else np.nan,
    }


def estimate_load_focus(training_effect: float | None, anaerobic_training_effect: float | None) -> str | None:
    if training_effect is None or pd.isna(training_effect):
        return None
    aerobic_te = float(training_effect)
    anaerobic_te = float(anaerobic_training_effect) if anaerobic_training_effect is not None and pd.notna(anaerobic_training_effect) else 0.0
    if anaerobic_te >= 1.0:
        return "mixed_or_anaerobic_estimated"
    if aerobic_te < 1.5:
        return "recovery_estimated"
    if aerobic_te <= 3.5:
        return "low_aerobic_estimated"
    return "high_aerobic_estimated"


def extract_estimated_sweat_loss_ml(session_row: pd.Series) -> float | None:
    for key in ("estimated_sweat_loss", "total_sweat_loss", "sweat_loss", "unknown_178"):
        value = session_row.get(key)
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except Exception:
            pass
        try:
            return float(value)
        except Exception:
            continue
    return None


def fatigue_component_score(drift_pct: float, hr_rise_bpm: float) -> float:
    drift_penalty = max(float(drift_pct) - 3.0, 0.0) * 11.0 if pd.notna(drift_pct) else 25.0
    rise_penalty = max(float(hr_rise_bpm) - 4.0, 0.0) * 6.0 if pd.notna(hr_rise_bpm) else 15.0
    return round(clip_score(100.0 - drift_penalty - rise_penalty), 1)


def extract_hr_metrics(fit_file: Path) -> dict | None:
    try:
        parser = FitParser(fit_file)
        parser.parse()

        records_df = parser.records
        session_df = parser.session
        if records_df.empty or session_df.empty:
            logger.warning("Missing record/session data in %s", fit_file.name)
            return None
        if "heart_rate" not in records_df.columns:
            logger.warning("No HR data in %s", fit_file.name)
            return None

        session_row = session_df.iloc[0]
        zones_row = get_message_row(parser, "zones_target")
        user_profile_row = get_message_row(parser, "user_profile")
        workout_row = get_message_row(parser, "workout")
        events_df = parser._dfs.get("event", pd.DataFrame())

        hr_data = records_df["heart_rate"].dropna()
        if hr_data.empty:
            logger.warning("No HR readings in %s", fit_file.name)
            return None

        activity_date, filename_mismatch = choose_activity_date(session_row, fit_file)
        active_records = get_active_records(records_df)
        avg_speed = float(
            session_row.get(
                "enhanced_avg_speed",
                records_df["speed"].dropna().mean() if "speed" in records_df.columns else np.nan,
            )
        )
        moving_speed = float(active_records["speed"].mean()) if not active_records.empty else avg_speed
        best_speed = float(
            session_row.get(
                "enhanced_max_speed",
                active_records["speed"].max() if not active_records.empty else np.nan,
            )
        )
        avg_power = float(
            session_row.get(
                "avg_power",
                records_df["power"].dropna().mean() if "power" in records_df.columns else np.nan,
            )
        )
        duration_min = round(float(session_row.get("total_timer_time", session_row.get("total_elapsed_time", 0))) / 60, 1)
        distance_km = round(float(session_row.get("total_distance", 0)) / 1000, 2)
        avg_hr = float(session_row.get("avg_heart_rate", hr_data.mean()))
        pace_min_per_km = pace_from_speed(avg_speed)
        moving_pace = pace_from_speed(moving_speed)
        best_pace = pace_from_speed(best_speed)
        aerobic_drift_pct = calculate_aerobic_drift(records_df)
        power_hr_decoupling_pct = calculate_ratio_decoupling(records_df, "power")
        steady_state_metrics = summarize_steady_state(records_df)
        pace_durability_pct = calculate_pace_durability(records_df)
        power_stability_cv_pct = calculate_variability_pct(active_records, "power")
        cadence_stability_cv_pct = calculate_variability_pct(active_records, "cadence")
        recovery_hr_60s = calculate_recovery_hr_60s(records_df, events_df)

        hr_max_setting = zones_row.get("max_heart_rate") if zones_row is not None else np.nan
        ftp_setting = zones_row.get("functional_threshold_power") if zones_row is not None else np.nan
        threshold_hr = zones_row.get("threshold_heart_rate") if zones_row is not None else np.nan
        weight_kg = user_profile_row.get("weight") if user_profile_row is not None else np.nan
        resting_hr = user_profile_row.get("resting_heart_rate") if user_profile_row is not None else np.nan
        sleep_time = user_profile_row.get("sleep_time") if user_profile_row is not None else None
        wake_time = user_profile_row.get("wake_time") if user_profile_row is not None else None
        workout_title = workout_row.get("wkt_name") if workout_row is not None else fit_file.stem

        hr_zone_distribution = build_zone_distribution(hr_data, HR_ZONE_PCT_BOUNDS, float(hr_max_setting)) if pd.notna(hr_max_setting) else {}
        power_values = active_records["power"].dropna() if "power" in active_records.columns else pd.Series(dtype=float)
        power_zone_distribution = build_zone_distribution(power_values, POWER_ZONE_PCT_BOUNDS, float(ftp_setting)) if pd.notna(ftp_setting) else {}
        zone2_metrics = summarize_hr_zone2(records_df, float(hr_max_setting)) if pd.notna(hr_max_setting) else summarize_hr_zone2(pd.DataFrame(), np.nan)

        avg_stride_length_m = np.nan
        if pd.notna(session_row.get("avg_step_length")):
            avg_stride_length_m = float(session_row.get("avg_step_length")) / 1000.0
        elif not active_records.empty and "stride_length_m" in active_records.columns:
            avg_stride_length_m = float(active_records["stride_length_m"].mean())

        running_economy = float(avg_power / avg_speed) if pd.notna(avg_power) and avg_speed > 0 else np.nan
        energy_cost_j_per_m = float(avg_power / avg_speed) if pd.notna(avg_power) and avg_speed > 0 else np.nan
        total_work_kj = float(session_row.get("total_work", np.nan)) / 1000 if pd.notna(session_row.get("total_work", np.nan)) else np.nan
        avg_power_wkg = float(avg_power / weight_kg) if pd.notna(avg_power) and pd.notna(weight_kg) and weight_kg > 0 else np.nan
        max_power_wkg = float(session_row.get("max_power", np.nan) / weight_kg) if pd.notna(session_row.get("max_power", np.nan)) and pd.notna(weight_kg) and weight_kg > 0 else np.nan
        fatigue_score = fatigue_component_score(
            aerobic_drift_pct if aerobic_drift_pct is not None else np.nan,
            steady_state_metrics.get("steady_hr_rise_bpm", np.nan),
        )
        estimated_sweat_loss_ml = extract_estimated_sweat_loss_ml(session_row)

        return {
            "file": fit_file.name,
            "date": activity_date,
            "filename_date": extract_date_from_filename(fit_file.name),
            "filename_mismatch": filename_mismatch,
            "workout_title": workout_title,
            "avg_hr": round(avg_hr, 1),
            "max_hr": int(hr_data.max()),
            "min_hr": int(hr_data.min()),
            "std_hr": round(hr_data.std(), 1),
            "hr_readings": len(hr_data),
            "avg_power": round(avg_power, 1),
            "normalized_power": round_or_nan(session_row.get("normalized_power"), 1),
            "max_power": round_or_nan(session_row.get("max_power"), 1),
            "avg_speed_mps": round(avg_speed, 3),
            "moving_speed_mps": round_or_nan(moving_speed, 3),
            "best_speed_mps": round_or_nan(best_speed, 3),
            "pace_min_per_km": round(pace_min_per_km, 2) if pace_min_per_km is not None else np.nan,
            "moving_pace_min_per_km": round(moving_pace, 2) if moving_pace is not None else np.nan,
            "best_pace_min_per_km": round(best_pace, 2) if best_pace is not None else np.nan,
            "duration_min": duration_min,
            "distance_km": distance_km,
            "total_ascent_m": round_or_nan(session_row.get("total_ascent"), 1),
            "total_descent_m": round_or_nan(session_row.get("total_descent"), 1),
            "avg_temperature_c": round_or_nan(session_row.get("avg_temperature"), 1),
            "max_temperature_c": round_or_nan(session_row.get("max_temperature"), 1),
            "power_per_hr": round(avg_power / avg_hr, 3) if avg_hr and not pd.isna(avg_power) else np.nan,
            "speed_per_hr": round(avg_speed / avg_hr, 5) if avg_hr and not pd.isna(avg_speed) else np.nan,
            "aerobic_drift_pct": round(aerobic_drift_pct, 2) if aerobic_drift_pct is not None else np.nan,
            "power_hr_decoupling_pct": round(power_hr_decoupling_pct, 2) if power_hr_decoupling_pct is not None else np.nan,
            "pace_durability_pct": round(pace_durability_pct, 2) if pace_durability_pct is not None else np.nan,
            "recovery_hr_60s_bpm": round_or_nan(recovery_hr_60s, 1),
            "power_stability_cv_pct": round_or_nan(power_stability_cv_pct, 2),
            "cadence_stability_cv_pct": round_or_nan(cadence_stability_cv_pct, 2),
            "avg_running_cadence": round_or_nan(session_row.get("avg_running_cadence"), 1),
            "max_running_cadence": round_or_nan(session_row.get("max_running_cadence"), 1),
            "avg_stride_length_m": round_or_nan(avg_stride_length_m, 3),
            "avg_stance_time_ms": round_or_nan(session_row.get("avg_stance_time"), 1),
            "avg_vertical_oscillation_mm": round_or_nan(session_row.get("avg_vertical_oscillation"), 1),
            "avg_vertical_ratio_pct": round_or_nan(session_row.get("avg_vertical_ratio"), 2),
            "left_right_balance_pct": np.nan,
            "aerobic_training_effect": round_or_nan(session_row.get("total_training_effect"), 1),
            "anaerobic_training_effect": round_or_nan(session_row.get("total_anaerobic_training_effect"), 1),
            "exercise_load": np.nan,
            "estimated_sweat_loss_ml": round_or_nan(estimated_sweat_loss_ml, 1),
            "estimated_sweat_loss_l": round_or_nan(estimated_sweat_loss_ml / 1000.0, 3) if estimated_sweat_loss_ml is not None else np.nan,
            "measured_load_focus_category": np.nan,
            "estimated_load_focus_category": estimate_load_focus(session_row.get("total_training_effect"), session_row.get("total_anaerobic_training_effect")),
            "vo2max": np.nan,
            "body_battery_before_run": np.nan,
            "hrv_status": np.nan,
            "stress_level": np.nan,
            "recovery_time_recommendation_h": np.nan,
            "sleep_time_profile": sleep_time,
            "wake_time_profile": wake_time,
            "resting_heart_rate": round_or_nan(resting_hr, 1),
            "weight_kg": round_or_nan(weight_kg, 1),
            "avg_power_wkg": round_or_nan(avg_power_wkg, 2),
            "max_power_wkg": round_or_nan(max_power_wkg, 2),
            "functional_threshold_power": round_or_nan(ftp_setting, 1),
            "threshold_heart_rate": round_or_nan(threshold_hr, 1),
            "max_heart_rate_setting": round_or_nan(hr_max_setting, 1),
            "hr_zone_source": "garmin_percent_max_hr" if pd.notna(hr_max_setting) else "unavailable",
            "power_zone_source": "garmin_percent_ftp" if pd.notna(ftp_setting) else "unavailable",
            "running_economy_w_per_mps": round_or_nan(running_economy, 1),
            "energy_cost_j_per_m": round_or_nan(energy_cost_j_per_m, 1),
            "total_work_kj": round_or_nan(total_work_kj, 1),
            "fatigue_resilience_score": fatigue_score,
            **{f"hr_{key}": value for key, value in hr_zone_distribution.items()},
            **{f"power_{key}": value for key, value in power_zone_distribution.items()},
            **zone2_metrics,
            **steady_state_metrics,
        }
    except Exception as exc:
        logger.error("Error parsing %s: %s", fit_file.name, exc)
        return None


def load_run_dataframe(fit_dir: Path | None = None) -> pd.DataFrame:
    runs_dir = resolve_easy_runs_dir(fit_dir)
    if not runs_dir.exists():
        raise FileNotFoundError(f"Directory not found: {runs_dir}")

    fit_files = sorted(runs_dir.glob("*.fit"))
    if not fit_files:
        raise FileNotFoundError(f"No FIT files found in {runs_dir}")

    print(f"\nParsing {len(fit_files)} easy-run FIT files...")
    hr_data: list[dict] = []
    for fit_file in fit_files:
        metrics = extract_hr_metrics(fit_file)
        if metrics:
            hr_data.append(metrics)
            print(
                f"  - {metrics['file']}: steady pace {metrics['steady_pace_min_per_km']:.2f} min/km, "
                f"steady HR {metrics['steady_avg_hr']:.0f}, duration {metrics['duration_min']:.1f} min"
            )

    if not hr_data:
        raise ValueError("No HR data could be extracted from the FIT files")

    df = pd.DataFrame(hr_data)
    df = df.dropna(subset=["date"]).copy()
    df["week"] = df["date"].dt.strftime("%W").astype(int)
    df["day_name"] = df["date"].dt.day_name()
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    df["pace_str"] = df["pace_min_per_km"].apply(lambda value: f"{value:.2f}" if pd.notna(value) else "n/a")
    df["steady_pace_str"] = df["steady_pace_min_per_km"].apply(lambda value: f"{value:.2f}" if pd.notna(value) else "n/a")
    df["duration_bucket"] = df["duration_min"].apply(duration_bucket)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def add_run_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Score each run using internationally recognised metrics.

    Components (all 0-100):
    - EF Score       (50%): Efficiency Factor = power / HR in W/bpm.
                            Reference scale: 0.9 W/bpm (beginner) to 2.0 W/bpm (well-trained).
                            Source: Joe Friel *The Triathlete's Training Bible*; TrainingPeaks.
    - Decoupling Score (35%): Aerobic Decoupling = cardiac drift in steady section.
                            <5% = aerobically fit (Garmin / Joe Friel standard).
    - Stability Score (15%): Steady-state HR standard deviation. Low variability = consistent effort.

    These metrics are load-independent — valid for comparing 5 km and 10 km easy runs alike.
    """
    df = df.copy()
    ef_scores: list[float] = []
    decoupling_scores: list[float] = []
    stability_scores: list[float] = []
    overall_scores: list[float] = []
    score_labels: list[str] = []

    for _, row in df.iterrows():
        # --- EF Score (power-based; fall back to pace-based if no power) ---
        ef_wbpm = row.get("steady_power_per_hr")
        if pd.notna(ef_wbpm):
            ef_score = clip_score((float(ef_wbpm) - EF_REF_MIN) / (EF_REF_MAX - EF_REF_MIN) * 100)
        else:
            speed_hr = row.get("steady_speed_per_hr")
            # Pace EF: map 0.012 m/s/bpm (beginner) to 0.020 m/s/bpm (trained) -> 0-100
            ef_score = clip_score((float(speed_hr) - 0.012) / 0.008 * 100) if pd.notna(speed_hr) else 50.0

        # --- Aerobic Decoupling Score (Garmin / Joe Friel: <5% = aerobically fit) ---
        drift = row.get("aerobic_drift_pct")
        decoupling_score = clip_score(100.0 - float(drift) * 8.0) if pd.notna(drift) else 50.0

        # --- HR Stability Score (lower steady-section HR std dev = more consistent effort) ---
        hr_std = row.get("steady_hr_std")
        if pd.notna(hr_std):
            stability_score = clip_score(100.0 - max(0.0, float(hr_std) - 1.5) * 10.0)
        else:
            stability_score = 50.0

        overall = round(0.50 * ef_score + 0.35 * decoupling_score + 0.15 * stability_score, 1)

        # Label: aerobic decoupling >8% is the primary fatigue signal
        drift_val = float(drift) if pd.notna(drift) else 0.0
        if drift_val > 8.0:
            label = "fatigue_risk"
        elif ef_score >= 60.0 and decoupling_score >= 60.0:
            label = "strong"
        elif ef_score >= 52.0:
            label = "good"
        elif ef_score >= 45.0:
            label = "steady"
        else:
            label = "below_par"

        ef_scores.append(round(ef_score, 1))
        decoupling_scores.append(round(decoupling_score, 1))
        stability_scores.append(round(stability_score, 1))
        overall_scores.append(overall)
        score_labels.append(label)

    df["ef_score"] = ef_scores
    df["decoupling_score"] = decoupling_scores
    df["stability_score"] = stability_scores
    df["easy_run_score"] = overall_scores
    df["score_label"] = score_labels
    return df


def get_reference_run(df: pd.DataFrame, row_index: int) -> pd.Series | None:
    if row_index == 0:
        return None

    current = df.iloc[row_index]
    prior_rows = df.iloc[:row_index]
    same_bucket = prior_rows[prior_rows["duration_bucket"] == current["duration_bucket"]]
    if not same_bucket.empty:
        return same_bucket.iloc[-1]
    return prior_rows.iloc[-1]


def classify_run_status(current: pd.Series, reference: pd.Series | None) -> tuple[str, str]:
    ef_wbpm = current.get("steady_power_per_hr")
    drift = current.get("aerobic_drift_pct")
    drift_str = f"{float(drift):.1f}%" if pd.notna(drift) else "n/a"
    ef_str = f"{float(ef_wbpm):.3f} W/bpm" if pd.notna(ef_wbpm) else "n/a"
    fit_tag = "below 5% — aerobically fit" if pd.notna(drift) and float(drift) < DECOUPLING_FIT_PCT else "above 5% threshold"

    if reference is None:
        return "baseline", (
              f"First run. EF {ef_str} (Joe Friel scale: 0.9 beginner -> 2.0 trained); "
            f"aerobic decoupling {drift_str} ({fit_tag})."
        )

    ef_change = pct_change(reference.get("steady_power_per_hr"), ef_wbpm)
    drift_delta: float | None = None
    if pd.notna(reference.get("aerobic_drift_pct")) and pd.notna(drift):
        drift_delta = float(drift) - float(reference["aerobic_drift_pct"])

    improvement_pts = 0
    fatigue_pts = 0
    reasons: list[str] = []

    if ef_change is not None:
        if ef_change >= 1.0:
            improvement_pts += 2
            reasons.append(f"EF improved {format_pct(ef_change)} to {ef_str}")
        elif ef_change <= -1.0:
            fatigue_pts += 2
            reasons.append(f"EF dropped {format_pct(ef_change)} to {ef_str}")
        else:
            reasons.append(f"EF steady at {ef_str} ({format_pct(ef_change)})")

    if pd.notna(drift):
        drift_f = float(drift)
        if drift_f < DECOUPLING_FIT_PCT:
            improvement_pts += 1
            reasons.append(f"aerobic decoupling {drift_str} (below 5% — aerobically fit)")
        elif drift_f < 8.0:
            reasons.append(f"aerobic decoupling {drift_str} (5-8% moderate cardiac drift)")
        else:
            fatigue_pts += 2
            reasons.append(f"aerobic decoupling {drift_str} (above 8% — high cardiac drift)")

    if drift_delta is not None:
        if drift_delta <= -1.0:
            improvement_pts += 1
            reasons.append(f"decoupling improved {drift_delta:+.1f}% vs reference")
        elif drift_delta >= 1.5:
            fatigue_pts += 1
            reasons.append(f"decoupling worsened {drift_delta:+.1f}% vs reference")

    reasons.append(
        f"score {current['easy_run_score']:.1f}/100 "
        f"(EF {current['ef_score']:.0f}, decoupling {current['decoupling_score']:.0f}, stability {current['stability_score']:.0f})"
    )

    drift_f2 = float(drift) if pd.notna(drift) else 0.0
    if drift_f2 > 8.0 or (fatigue_pts >= 3 and fatigue_pts > improvement_pts):
        return "fatigue_risk", "; ".join(reasons)
    if improvement_pts >= 3 or (improvement_pts >= 2 and current["easy_run_score"] >= 60):
        return "improving", "; ".join(reasons)
    return "steady", "; ".join(reasons)


def add_timeline_status(df: pd.DataFrame) -> pd.DataFrame:
    statuses: list[str] = []
    notes: list[str] = []
    reference_dates: list[str] = []
    for row_index in range(len(df)):
        reference = get_reference_run(df, row_index)
        status, note = classify_run_status(df.iloc[row_index], reference)
        statuses.append(status)
        notes.append(note)
        reference_dates.append(reference["date_str"] if reference is not None else "")

    df = df.copy()
    df["timeline_status"] = statuses
    df["timeline_note"] = notes
    df["reference_date"] = reference_dates
    return df


def add_longitudinal_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pace_change_vs_reference: list[float] = []
    hr_change_vs_reference: list[float] = []
    ef_change_vs_reference: list[float] = []
    drift_delta_vs_reference: list[float] = []
    hr_cost_change_vs_reference: list[float] = []
    pace_at_similar_hr_change: list[float] = []
    hr_at_similar_pace_change: list[float] = []

    for row_index in range(len(df)):
        current = df.iloc[row_index]
        reference = get_reference_run(df, row_index)
        if reference is None:
            pace_change_vs_reference.append(np.nan)
            hr_change_vs_reference.append(np.nan)
            ef_change_vs_reference.append(np.nan)
            drift_delta_vs_reference.append(np.nan)
            hr_cost_change_vs_reference.append(np.nan)
            pace_at_similar_hr_change.append(np.nan)
            hr_at_similar_pace_change.append(np.nan)
            continue

        pace_change_vs_reference.append(
            lower_is_better_change(reference.get("steady_pace_min_per_km"), current.get("steady_pace_min_per_km"))
        )
        hr_change_vs_reference.append(
            lower_is_better_change(reference.get("steady_avg_hr"), current.get("steady_avg_hr"))
        )
        ef_change_vs_reference.append(
            pct_change(reference.get("steady_power_per_hr"), current.get("steady_power_per_hr"))
        )

        if pd.notna(reference.get("aerobic_drift_pct")) and pd.notna(current.get("aerobic_drift_pct")):
            drift_delta_vs_reference.append(float(current["aerobic_drift_pct"]) - float(reference["aerobic_drift_pct"]))
        else:
            drift_delta_vs_reference.append(np.nan)

        ref_hr_cost = reference.get("steady_avg_hr") / reference.get("steady_avg_speed_mps") if pd.notna(reference.get("steady_avg_hr")) and pd.notna(reference.get("steady_avg_speed_mps")) and reference.get("steady_avg_speed_mps") else np.nan
        cur_hr_cost = current.get("steady_avg_hr") / current.get("steady_avg_speed_mps") if pd.notna(current.get("steady_avg_hr")) and pd.notna(current.get("steady_avg_speed_mps")) and current.get("steady_avg_speed_mps") else np.nan
        hr_cost_change_vs_reference.append(lower_is_better_change(ref_hr_cost, cur_hr_cost))

        if pd.notna(reference.get("steady_avg_hr")) and pd.notna(current.get("steady_avg_hr")) and abs(float(current["steady_avg_hr"]) - float(reference["steady_avg_hr"])) <= 3.0:
            pace_at_similar_hr_change.append(
                lower_is_better_change(reference.get("steady_pace_min_per_km"), current.get("steady_pace_min_per_km"))
            )
        else:
            pace_at_similar_hr_change.append(np.nan)

        if pd.notna(reference.get("steady_pace_min_per_km")) and pd.notna(current.get("steady_pace_min_per_km")) and abs(float(current["steady_pace_min_per_km"]) - float(reference["steady_pace_min_per_km"])) <= 0.15:
            hr_at_similar_pace_change.append(
                lower_is_better_change(reference.get("steady_avg_hr"), current.get("steady_avg_hr"))
            )
        else:
            hr_at_similar_pace_change.append(np.nan)

    df["pace_change_vs_reference_pct"] = [round_or_nan(value, 1) for value in pace_change_vs_reference]
    df["steady_hr_change_vs_reference_pct"] = [round_or_nan(value, 1) for value in hr_change_vs_reference]
    df["ef_change_vs_reference_pct"] = [round_or_nan(value, 1) for value in ef_change_vs_reference]
    df["drift_delta_vs_reference_pct_pts"] = [round_or_nan(value, 1) for value in drift_delta_vs_reference]
    df["hr_cost_change_vs_reference_pct"] = [round_or_nan(value, 1) for value in hr_cost_change_vs_reference]
    df["pace_change_at_similar_hr_pct"] = [round_or_nan(value, 1) for value in pace_at_similar_hr_change]
    df["hr_change_at_similar_pace_pct"] = [round_or_nan(value, 1) for value in hr_at_similar_pace_change]
    df["rolling_3run_duration_min"] = df["duration_min"].rolling(3, min_periods=1).sum().round(1)
    df["rolling_3run_total_work_kj"] = df["total_work_kj"].rolling(3, min_periods=1).sum().round(1)
    df["rolling_3run_training_effect"] = df["aerobic_training_effect"].rolling(3, min_periods=1).sum().round(1)
    temp_median = df["avg_temperature_c"].median()
    df["temperature_vs_median_c"] = (df["avg_temperature_c"] - temp_median).round(1) if pd.notna(temp_median) else np.nan
    return df


def classify_week_status(current: pd.Series, reference: pd.Series | None) -> tuple[str, str]:
    if reference is None:
        return "baseline", "First week in timeline."

    ef_change = pct_change(reference["ef_wbpm"], current["ef_wbpm"])
    drift_delta = current["aerobic_drift_pct"] - reference["aerobic_drift_pct"]

    if (
        current["easy_run_score"] >= 58
        and (ef_change is None or ef_change >= 0.0)
        and current["aerobic_drift_pct"] <= 7.0
    ):
        return "improving", f"score {current['easy_run_score']:.1f}, EF {format_pct(ef_change)}, drift {current['aerobic_drift_pct']:.1f}%"
    if (
        current["aerobic_drift_pct"] > 8.0
        or (ef_change is not None and ef_change <= -1.5)
        or (current["aerobic_drift_pct"] >= 6.5 and drift_delta >= 1.0)
    ):
        return "fatigue_risk", f"score {current['easy_run_score']:.1f}, drift {current['aerobic_drift_pct']:.1f}%"
    return "steady", f"score {current['easy_run_score']:.1f}, drift {current['aerobic_drift_pct']:.1f}%"


def build_weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    weekly = (
        df.groupby("week", as_index=False)
        .agg(
            run_count=("file", "count"),
            avg_hr=("steady_avg_hr", "mean"),
            pace_min_per_km=("steady_pace_min_per_km", "mean"),
            ef_wbpm=("steady_power_per_hr", "mean"),
            aerobic_drift_pct=("aerobic_drift_pct", "median"),
            easy_run_score=("easy_run_score", "mean"),
            ef_score=("ef_score", "mean"),
            decoupling_score=("decoupling_score", "mean"),
            stability_score=("stability_score", "mean"),
            start_date=("date", "min"),
            end_date=("date", "max"),
        )
        .sort_values("week")
        .reset_index(drop=True)
    )
    weekly["start_date_str"] = weekly["start_date"].dt.strftime("%Y-%m-%d")
    weekly["end_date_str"] = weekly["end_date"].dt.strftime("%Y-%m-%d")

    statuses: list[str] = []
    notes: list[str] = []
    for row_index in range(len(weekly)):
        reference = weekly.iloc[row_index - 1] if row_index > 0 else None
        status, note = classify_week_status(weekly.iloc[row_index], reference)
        statuses.append(status)
        notes.append(note)
    weekly["timeline_status"] = statuses
    weekly["timeline_note"] = notes
    return weekly


def get_bucket_comparison(df: pd.DataFrame, bucket_name: str) -> dict | None:
    bucket_df = df[df["duration_bucket"] == bucket_name].sort_values("date")
    if len(bucket_df) < 2:
        return None
    first_row = bucket_df.iloc[0]
    last_row = bucket_df.iloc[-1]
    return {
        "label": bucket_name,
        "run_count": len(bucket_df),
        "first_date": first_row["date_str"],
        "last_date": last_row["date_str"],
        "first_pace": first_row["pace_str"],
        "last_pace": last_row["pace_str"],
        "first_hr": first_row["avg_hr"],
        "last_hr": last_row["avg_hr"],
        "speed_hr_change": pct_change(first_row["speed_per_hr"], last_row["speed_per_hr"]),
        "power_hr_change": pct_change(first_row["power_per_hr"], last_row["power_per_hr"]),
    }


def build_overall_assessment(df: pd.DataFrame, weekly: pd.DataFrame) -> tuple[str, list[str]]:
    first_row = df.iloc[0]
    last_row = df.iloc[-1]
    latest_week = weekly.iloc[-1]

    ef_trend = pct_change(first_row["steady_power_per_hr"], last_row["steady_power_per_hr"])
    avg_drift = df["aerobic_drift_pct"].median()
    runs_below_5pct = int((df["aerobic_drift_pct"] < DECOUPLING_FIT_PCT).sum())

    headline = "steady"
    details: list[str] = []

    details.append(
        f"Efficiency Factor (EF, W/bpm — Joe Friel / TrainingPeaks standard): "
            f"first run {first_row['steady_power_per_hr']:.3f} W/bpm -> "
        f"last run {last_row['steady_power_per_hr']:.3f} W/bpm ({format_pct(ef_trend)}). "
        f"Reference: <1.4 beginner, 1.4–1.8 recreational, 1.8+ trained."
    )
    if ef_trend is not None and ef_trend >= 1.0:
        headline = "improving"

    details.append(
        f"Aerobic Decoupling (Garmin / Joe Friel standard — <5% = aerobically fit run): "
        f"median {avg_drift:.1f}%, {runs_below_5pct}/{len(df)} runs below the 5% threshold. "
        f"This metric is load-independent — valid for comparing 5 km and 10 km easy runs."
    )

    details.append(
        f"Latest run score {last_row['easy_run_score']:.1f}/100 "
        f"(EF {last_row['ef_score']:.1f}, decoupling {last_row['decoupling_score']:.1f}, stability {last_row['stability_score']:.1f})."
    )

    if latest_week["timeline_status"] == "fatigue_risk":
        headline = "improving_with_fatigue_risk" if headline == "improving" else "fatigue_risk"
        details.append(
            f"Latest week shows fatigue risk: aerobic decoupling {latest_week['aerobic_drift_pct']:.1f}%, "
            f"score {latest_week['easy_run_score']:.1f}."
        )

    if not details:
        details.append("The timeline is mostly steady; no strong improvement or fatigue signal dominates yet.")
    return headline, details


def build_console_summary(df: pd.DataFrame, weekly: pd.DataFrame) -> str:
    headline, details = build_overall_assessment(df, weekly)
    first_row = df.iloc[0]
    last_row = df.iloc[-1]
    mismatch_count = int(df["filename_mismatch"].sum())

    lines = []
    lines.append("=" * 70)
    lines.append("EASY RUN HR TIMELINE REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Data quality:")
    lines.append(f"- Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    lines.append(f"- Runs analyzed: {len(df)}")
    lines.append(
        f"- Duration range: {df['duration_min'].min():.1f}-{df['duration_min'].max():.1f} min; "
        f"distance range: {df['distance_km'].min():.2f}-{df['distance_km'].max():.2f} km"
    )
    lines.append(
        f"- Run scores use the steady-state section after roughly {STEADY_STATE_START_M/1000:.0f}-{STEADY_STATE_MAX_START_M/1000:.0f} km, "
        "so the initial HR ramp-up does not dominate the score."
    )
    if mismatch_count:
        lines.append(f"- Corrected {mismatch_count} filename date mismatch using FIT session timestamps")
    lines.append("")
    lines.append(f"Overall status: {headline}")
    for detail in details:
        lines.append(f"- {detail}")
    lines.append(
        f"- First run {first_row['date_str']}: steady pace {first_row['steady_pace_str']} min/km at steady HR {first_row['steady_avg_hr']:.0f}; "
        f"last run {last_row['date_str']}: steady pace {last_row['steady_pace_str']} min/km at steady HR {last_row['steady_avg_hr']:.0f}"
    )
    lines.append(f"- Median aerobic drift: {df['aerobic_drift_pct'].median():.2f}% (lower is better, <5% is steady)")
    lines.append("")
    lines.append("Weekly timeline:")
    for _, row in weekly.iterrows():
        lines.append(
            f"- Week {int(row['week'])} ({row['start_date_str']} to {row['end_date_str']}): "
            f"score {row['easy_run_score']:.1f}, EF {row['ef_wbpm']:.3f} W/bpm, "
            f"decoupling {row['aerobic_drift_pct']:.1f}%, status {row['timeline_status']}"
        )
    lines.append("")
    lines.append("Run-by-run timeline:")
    for _, row in df.iterrows():
        ref_text = f" vs {row['reference_date']}" if row['reference_date'] else ""
        lines.append(
            f"- {row['date_str']} | {row['distance_km']:.2f} km | {row['duration_min']:.1f} min | "
            f"score {row['easy_run_score']:.1f}/100 | EF {row['steady_power_per_hr']:.3f} W/bpm | "
            f"decoupling {row['aerobic_drift_pct']:.1f}% | {row['timeline_status']}{ref_text}"
        )
        lines.append(f"  {row['timeline_note']}")
    lines.append("")
    lines.append(f"Reports saved to {CSV_REPORT_PATH}, {PLOT_REPORT_PATH}, and {TIMELINE_REPORT_PATH}")
    return "\n".join(lines)


def format_metric(value, digits: int = 1, suffix: str = "", missing: str = "unavailable") -> str:
    if value is None or pd.isna(value):
        return missing
    if isinstance(value, str):
        return value
    if isinstance(value, (bool, np.bool_)):
        return str(value)
    if not isinstance(value, (int, float, np.integer, np.floating)):
        return str(value)
    return f"{float(value):.{digits}f}{suffix}"


def metric_status(value, estimated: bool = False) -> str:
    if value is None or pd.isna(value) or value == "":
        return "unavailable"
    return "estimated" if estimated else "measured"


def build_longitudinal_observations(df: pd.DataFrame) -> list[str]:
    observations: list[str] = []
    first_row = df.iloc[0]
    last_row = df.iloc[-1]

    pace_change = lower_is_better_change(first_row.get("steady_pace_min_per_km"), last_row.get("steady_pace_min_per_km"))
    ef_change = pct_change(first_row.get("steady_power_per_hr"), last_row.get("steady_power_per_hr"))
    drift_delta = float(last_row.get("aerobic_drift_pct") - first_row.get("aerobic_drift_pct")) if pd.notna(first_row.get("aerobic_drift_pct")) and pd.notna(last_row.get("aerobic_drift_pct")) else np.nan

    if pd.notna(pace_change):
        observations.append(
            f"Steady-state easy pace changed {format_pct(pace_change)} from the first comparable run to the latest run."
        )
    if pd.notna(ef_change):
        observations.append(
            f"Steady power-per-heartbeat changed {format_pct(ef_change)} across the timeline, which is the cleanest aerobic-efficiency signal in this dataset."
        )
    if pd.notna(drift_delta):
        observations.append(
            f"Aerobic decoupling moved {drift_delta:+.1f} percentage points from the opening run to the latest run."
        )

    hot_runs = df[df["avg_temperature_c"] >= 30]
    if len(hot_runs) >= 2:
        observations.append(
            f"{len(hot_runs)} runs were recorded at 30 C or hotter; heat is a plausible confounder for drift and HR cost in this sample."
        )

    high_drift_runs = int((df["aerobic_drift_pct"] >= 8.0).sum())
    if high_drift_runs:
        observations.append(
            f"{high_drift_runs}/{len(df)} runs crossed the 8% decoupling line, which is the strongest within-run fatigue signal in these easy sessions."
        )
    return observations


def build_run_concerns(row: pd.Series) -> list[str]:
    concerns: list[str] = []
    if pd.notna(row.get("aerobic_drift_pct")) and float(row["aerobic_drift_pct"]) >= 8.0:
        concerns.append(f"High aerobic decoupling at {row['aerobic_drift_pct']:.1f}% suggests cardiovascular drift beyond a typical easy-run target.")
    if pd.notna(row.get("pace_durability_pct")) and float(row["pace_durability_pct"]) >= 3.0:
        concerns.append(f"Pace slowed by {row['pace_durability_pct']:.1f}% from early to late run segments, which weakens durability.")
    if pd.notna(row.get("avg_temperature_c")) and float(row["avg_temperature_c"]) >= 30.0:
        concerns.append(f"Average temperature was {row['avg_temperature_c']:.1f} C, so heat strain is a realistic contributor to elevated HR and drift.")
    if pd.notna(row.get("hr_z4_pct")) and float(row["hr_z4_pct"]) >= 20.0:
        concerns.append(f"{row['hr_z4_pct']:.1f}% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.")
    if not concerns:
        concerns.append("No acute red flags stand out in this file beyond the usual Garmin power and training-effect uncertainty.")
    return concerns


def build_run_recommendations(row: pd.Series) -> list[str]:
    recommendations: list[str] = []
    if pd.notna(row.get("aerobic_drift_pct")) and float(row["aerobic_drift_pct"]) >= 8.0:
        recommendations.append("Slow the first 15-20 minutes or insert brief walk resets so the steady section stays below the decoupling threshold.")
    if pd.notna(row.get("zone2_duration_min")) and float(row["zone2_duration_min"]) < 10.0:
        recommendations.append("If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.")
    if pd.notna(row.get("avg_temperature_c")) and float(row["avg_temperature_c"]) >= 30.0:
        recommendations.append("Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.")
    if pd.notna(row.get("aerobic_drift_pct")) and float(row["aerobic_drift_pct"]) < 5.0 and pd.notna(row.get("pace_change_vs_reference_pct")) and float(row["pace_change_vs_reference_pct"]) > 0:
        recommendations.append("This is a good candidate benchmark run; keep conditions similar and use it to judge whether aerobic efficiency is actually improving.")
    if not recommendations:
        recommendations.append("Hold the current easy-run structure and keep judging progress with matched-duration comparisons rather than single-run pace changes.")
    return recommendations


def write_timeline_report(df: pd.DataFrame, weekly: pd.DataFrame) -> Path:
    headline, details = build_overall_assessment(df, weekly)
    measured_unavailable = [
        "Measured directly from current FIT exports: session totals, heart rate, power, cadence, stride length, stance time, vertical oscillation/ratio, Garmin training effect, Garmin zone target settings, and profile weight/resting HR.",
        "Measured from session metadata (mapped field): estimated sweat loss in mL/L.",
        "Estimated in this report: load focus category only. It is inferred from Garmin aerobic and anaerobic training effect, not read directly from the FIT file.",
        "Unavailable in the current FIT exports: Body Battery before run, HRV status, stress level, recovery-time recommendation, per-run sleep metrics, VO2 max, direct exercise load, and left/right balance.",
    ]

    lines: list[str] = []
    lines.append("# Easy Run Endurance Analysis")
    lines.append("")
    lines.append(f"Overall status: **{headline}**")
    lines.append("")
    for detail in details:
        lines.append(f"- {detail}")
    lines.append("")
    lines.append("## Metric Availability")
    lines.append("")
    for item in measured_unavailable:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Longitudinal Tracking")
    lines.append("")
    lines.append("| Date | Workout | km | Steady Pace | Steady HR | EF W/bpm | Drift % | Pace vs ref % | HR cost vs ref % | 3-run work kJ | Status |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for _, row in df.iterrows():
        lines.append(
            f"| {row['date_str']} | {row['workout_title']} | {row['distance_km']:.2f} | {row['steady_pace_str']} | {row['steady_avg_hr']:.0f} | {row['steady_power_per_hr']:.3f} | {row['aerobic_drift_pct']:.1f} | {format_metric(row.get('pace_change_vs_reference_pct'), 1, '%')} | {format_metric(row.get('hr_cost_change_vs_reference_pct'), 1, '%')} | {format_metric(row.get('rolling_3run_total_work_kj'), 1)} | {row['timeline_status']} |"
        )
    lines.append("")
    lines.append("## Weekly Summary")
    lines.append("")
    lines.append("| Week | Dates | Runs | Score | EF W/bpm | Decoupling % | Status |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")
    for _, row in weekly.iterrows():
        lines.append(
            f"| {int(row['week'])} | {row['start_date_str']} to {row['end_date_str']} | {int(row['run_count'])} | {row['easy_run_score']:.1f} | {row['ef_wbpm']:.3f} | {row['aerobic_drift_pct']:.1f} | {row['timeline_status']} |"
        )
    lines.append("")
    lines.append("## Overall Observations Worth Tracking")
    lines.append("")
    for observation in build_longitudinal_observations(df):
        lines.append(f"- {observation}")
    lines.append("")
    lines.append("## Per-Run Summaries")
    lines.append("")

    for row_index in range(len(df)):
        row = df.iloc[row_index]
        reference = get_reference_run(df, row_index)
        concerns = build_run_concerns(row)
        recommendations = build_run_recommendations(row)
        physiologic_interpretation = []
        if pd.notna(row.get("aerobic_drift_pct")) and float(row["aerobic_drift_pct"]) < 5.0:
            physiologic_interpretation.append("The steady section stayed inside the usual aerobic-decoupling target, which supports durable easy-run metabolism for this duration.")
        elif pd.notna(row.get("aerobic_drift_pct")):
            physiologic_interpretation.append("Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.")
        if pd.notna(row.get("pace_change_at_similar_hr_pct")):
            physiologic_interpretation.append(f"At roughly the same steady HR as the reference run, pace changed {format_pct(row['pace_change_at_similar_hr_pct'])}, which is direct evidence about aerobic development.")
        elif pd.notna(row.get("hr_change_at_similar_pace_pct")):
            physiologic_interpretation.append(f"At nearly the same steady pace as the reference run, HR cost changed {format_pct(row['hr_change_at_similar_pace_pct'])}.")
        else:
            physiologic_interpretation.append("This run is best interpreted against the same duration bucket rather than as a standalone benchmark.")

        lines.append(f"### {row['date_str']} - {row['workout_title']}")
        lines.append("")
        lines.append("#### 1. Executive Summary")
        lines.append("")
        lines.append(f"- {row['distance_km']:.2f} km in {row['duration_min']:.1f} min, average pace {row['pace_min_per_km']:.2f} min/km, steady pace {row['steady_pace_min_per_km']:.2f} min/km.")
        lines.append(f"- Average HR {row['avg_hr']:.0f} bpm, steady HR {row['steady_avg_hr']:.0f} bpm, EF {row['steady_power_per_hr']:.3f} W/bpm, aerobic decoupling {row['aerobic_drift_pct']:.1f}%.")
        if reference is not None:
            lines.append(f"- Reference comparison ({reference['date_str']}): pace {format_metric(row.get('pace_change_vs_reference_pct'), 1, '%')} better/worse depending on sign, EF {format_metric(row.get('ef_change_vs_reference_pct'), 1, '%')}, drift delta {format_metric(row.get('drift_delta_vs_reference_pct_pts'), 1, ' pts')}.")
        else:
            lines.append("- Baseline run for this dataset segment; use later runs to judge adaptation.")
        lines.append("")
        lines.append("#### 2. Key Metrics Table")
        lines.append("")
        lines.append("| Category | Metric | Value | Status |")
        lines.append("| --- | --- | --- | --- |")
        lines.append(f"| Basic | Duration | {row['duration_min']:.1f} min | measured |")
        lines.append(f"| Basic | Distance | {row['distance_km']:.2f} km | measured |")
        lines.append(f"| Basic | Average pace | {row['pace_min_per_km']:.2f} min/km | measured |")
        lines.append(f"| Basic | Moving pace | {format_metric(row.get('moving_pace_min_per_km'), 2, ' min/km')} | measured |")
        lines.append(f"| Basic | Best pace | {format_metric(row.get('best_pace_min_per_km'), 2, ' min/km')} | measured |")
        lines.append(f"| Basic | Elevation gain/loss | {format_metric(row.get('total_ascent_m'), 1, ' m')} / {format_metric(row.get('total_descent_m'), 1, ' m')} | measured |")
        lines.append(f"| Environment | Average / max temperature | {format_metric(row.get('avg_temperature_c'), 1, ' C')} / {format_metric(row.get('max_temperature_c'), 1, ' C')} | {metric_status(row.get('avg_temperature_c'))} |")
        lines.append(f"| Heart rate | Average / max HR | {row['avg_hr']:.0f} / {row['max_hr']:.0f} bpm | measured |")
        lines.append(f"| Heart rate | HR zone distribution | Z1 {format_metric(row.get('hr_z1_pct'), 1, '%')}, Z2 {format_metric(row.get('hr_z2_pct'), 1, '%')}, Z3 {format_metric(row.get('hr_z3_pct'), 1, '%')}, Z4 {format_metric(row.get('hr_z4_pct'), 1, '%')}, Z5 {format_metric(row.get('hr_z5_pct'), 1, '%')} | {metric_status(row.get('hr_z1_pct'))} |")
        lines.append(f"| Heart rate | Recovery HR at 60 s | {format_metric(row.get('recovery_hr_60s_bpm'), 1, ' bpm')} | {metric_status(row.get('recovery_hr_60s_bpm'))} |")
        lines.append(f"| Power | Average / max / normalized power | {format_metric(row.get('avg_power'), 1, ' W')} / {format_metric(row.get('max_power'), 1, ' W')} / {format_metric(row.get('normalized_power'), 1, ' W')} | measured |")
        lines.append(f"| Power | Power zones | Z1 {format_metric(row.get('power_z1_pct'), 1, '%')}, Z2 {format_metric(row.get('power_z2_pct'), 1, '%')}, Z3 {format_metric(row.get('power_z3_pct'), 1, '%')}, Z4 {format_metric(row.get('power_z4_pct'), 1, '%')}, Z5 {format_metric(row.get('power_z5_pct'), 1, '%')} | {metric_status(row.get('power_z1_pct'))} |")
        lines.append(f"| Power | W/kg / stability | {format_metric(row.get('avg_power_wkg'), 2, ' W/kg')} / {format_metric(row.get('power_stability_cv_pct'), 1, '% CV')} | {metric_status(row.get('avg_power_wkg'))} |")
        lines.append(f"| Dynamics | Cadence / stride length | {format_metric(row.get('avg_running_cadence'), 1, ' spm')} / {format_metric(row.get('avg_stride_length_m'), 3, ' m')} | measured |")
        lines.append(f"| Dynamics | Ground contact / vertical oscillation / vertical ratio | {format_metric(row.get('avg_stance_time_ms'), 1, ' ms')} / {format_metric(row.get('avg_vertical_oscillation_mm'), 1, ' mm')} / {format_metric(row.get('avg_vertical_ratio_pct'), 2, '%')} | measured |")
        lines.append(f"| Aerobic | Training effect / anaerobic TE | {format_metric(row.get('aerobic_training_effect'), 1)} / {format_metric(row.get('anaerobic_training_effect'), 1)} | measured |")
        lines.append(f"| Aerobic | Load focus | {format_metric(row.get('estimated_load_focus_category'))} | estimated |")
        lines.append(f"| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |")
        lines.append(f"| Recovery | Estimated sweat loss | {format_metric(row.get('estimated_sweat_loss_ml'), 1, ' mL')} ({format_metric(row.get('estimated_sweat_loss_l'), 3, ' L')}) | {metric_status(row.get('estimated_sweat_loss_ml'))} |")
        lines.append(f"| Recovery | Sleep profile window | {format_metric(row.get('sleep_time_profile'))} to {format_metric(row.get('wake_time_profile'))} | {metric_status(row.get('sleep_time_profile'))} |")
        lines.append("")
        lines.append("#### 3. Physiological Interpretation")
        lines.append("")
        for item in physiologic_interpretation:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("#### 4. Aerobic Efficiency Analysis")
        lines.append("")
        lines.append(f"- Steady-state EF was {row['steady_power_per_hr']:.3f} W/bpm and steady speed per HR was {row['steady_speed_per_hr']:.5f} m/s/bpm.")
        lines.append(f"- Aerobic decoupling was {row['aerobic_drift_pct']:.1f}% and power-HR decoupling was {format_metric(row.get('power_hr_decoupling_pct'), 1, '%')}.")
        lines.append(f"- Time spent in Garmin HR zone 2 was {format_metric(row.get('zone2_duration_min'), 1, ' min')}; pace inside that zone was {format_metric(row.get('zone2_pace_min_per_km'), 2, ' min/km')}.")
        lines.append("")
        lines.append("#### 5. Fatigue/Recovery Assessment")
        lines.append("")
        lines.append(f"- Fatigue resilience score: {format_metric(row.get('fatigue_resilience_score'), 1, '/100')} with steady HR rise {format_metric(row.get('steady_hr_rise_bpm'), 1, ' bpm')}. ")
        lines.append(f"- Rolling 3-run load proxy: {format_metric(row.get('rolling_3run_total_work_kj'), 1, ' kJ')} mechanical work and {format_metric(row.get('rolling_3run_training_effect'), 1)} summed aerobic training effect.")
        lines.append(f"- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.")
        lines.append("")
        lines.append("#### 6. Running Economy Notes")
        lines.append("")
        lines.append(f"- Mechanical energy cost was {format_metric(row.get('energy_cost_j_per_m'), 1, ' J/m')} and average running economy was {format_metric(row.get('running_economy_w_per_mps'), 1, ' W per m/s')}.")
        lines.append(f"- Cadence stability was {format_metric(row.get('cadence_stability_cv_pct'), 1, '% CV')} and pace durability changed {format_metric(row.get('pace_durability_pct'), 1, '%')} from early to late thirds.")
        lines.append("")
        lines.append("#### 7. Concerns or Risks")
        lines.append("")
        for item in concerns:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("#### 8. Recommendations")
        lines.append("")
        for item in recommendations:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Suggested Visualization Ideas")
    lines.append("")
    lines.append("- Matched-duration slope chart: steady pace and steady HR for 45 min, 50-55 min, and 60+ min buckets.")
    lines.append("- Heat-context scatter: average temperature vs aerobic decoupling, colored by fatigue resilience score.")
    lines.append("- Pace vs HR-cost chart: steady pace on one axis, steady HR/speed on the other, with point size driven by duration.")
    lines.append("- Running-dynamics trend panel: stride length, stance time, and vertical ratio against steady pace.")
    lines.append("")
    lines.append("## Important Limitations")
    lines.append("")
    lines.append("- Garmin running power, training effect, and normalized power are vendor-derived and should be treated as consistent heuristics, not laboratory truth.")
    lines.append("- This dataset is small and weather is warm in several runs, so trend interpretation should prioritize repeated conditions and matched durations.")
    lines.append("- Recovery and wellness conclusions are indirect because the relevant wellness metrics are not present in these FIT exports.")

    TIMELINE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return TIMELINE_REPORT_PATH
def create_plots(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Easy Run Scorecard — International Metrics", fontsize=16, fontweight="bold")
    x = np.arange(len(df))
    x_labels = df["date_str"]

    # Panel 1: EF trend (primary fitness indicator)
    ax = axes[0, 0]
    ax.plot(x, df["steady_power_per_hr"], marker="o", linewidth=2.5, markersize=7,
            color="midnightblue", label="EF (W/bpm)")
    ef_values = df["steady_power_per_hr"]
    ef_min = ef_values.min(skipna=True)
    ef_max = ef_values.max(skipna=True)
    ef_range = (ef_max - ef_min) if pd.notna(ef_min) and pd.notna(ef_max) else 0.0
    ef_label_offset = max(0.01, ef_range * 0.08)
    for i, ef in enumerate(ef_values):
        if pd.notna(ef):
            ax.text(i, ef + ef_label_offset, f"{ef:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold", color="midnightblue")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.axhline(1.8, color="seagreen", linestyle="--", linewidth=1.2, label="Trained (1.8)")
    ax.axhline(1.4, color="darkorange", linestyle="--", linewidth=1.2, label="Recreational (1.4)")
    if pd.notna(ef_max):
        ax.set_ylim(top=ef_max + ef_label_offset + 0.03)
    ax.set_xlabel("Date")
    ax.set_ylabel("Efficiency Factor (W/bpm)")
    ax.set_title("Efficiency Factor Trend\n(Joe Friel / TrainingPeaks — higher = fitter)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    ax.tick_params(axis="x", rotation=45)

    # Panel 2: Aerobic Decoupling % with Garmin 5% threshold
    ax = axes[0, 1]
    colors = ["seagreen" if d < DECOUPLING_FIT_PCT else ("darkorange" if d < 8.0 else "crimson")
              for d in df["aerobic_drift_pct"]]
    bars = ax.bar(x, df["aerobic_drift_pct"], color=colors, alpha=0.85, edgecolor="black", linewidth=0.7)
    
    # Add labels: mins spent and avg HR (with dynamic spacing to avoid title crowding)
    max_drift = df["aerobic_drift_pct"].max()
    label_offset = max(0.5, max_drift * 0.08)  # Dynamic offset based on highest bar
    for i, (idx, row) in enumerate(df.iterrows()):
        drift_pct = row["aerobic_drift_pct"]
        mins = row.get("duration_min", np.nan)
        avg_hr = row.get("steady_avg_hr", np.nan)
        label_text = f"{mins:.0f}m\n{avg_hr:.0f}bpm" if not (pd.isna(mins) or pd.isna(avg_hr)) else ""
        ax.text(i, drift_pct + label_offset, label_text, ha="center", va="bottom", fontsize=7, fontweight="bold")
    
    ax.axhline(DECOUPLING_FIT_PCT, color="seagreen", linestyle="--", linewidth=1.5,
               label=f"Fit threshold ({DECOUPLING_FIT_PCT:.0f}%)")
    ax.axhline(8.0, color="crimson", linestyle=":", linewidth=1.2, label="High drift (8%)")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_ylabel("Aerobic Decoupling (%)")
    ax.set_ylim(0, max_drift + label_offset + 2)  # Add extra space at top for labels
    ax.set_title("Aerobic Decoupling %\n(Garmin/Friel standard — <5% = aerobically fit)\nLabels: duration (mins) / avg HR (bpm)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper left")

    # Panel 3: Score components over time
    ax = axes[1, 0]
    ax.plot(x, df["ef_score"], marker="o", linewidth=2, markersize=7,
            color="steelblue", label="EF score")
    ax.plot(x, df["decoupling_score"], marker="s", linewidth=2, markersize=7,
            color="darkorange", label="Decoupling score")
    ax.plot(x, df["stability_score"], marker="^", linewidth=2, markersize=7,
            color="slateblue", label="Stability score")
    ax.plot(x, df["easy_run_score"], marker="D", linewidth=2.5, markersize=8,
            color="midnightblue", linestyle="-.", label="Overall score")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.axhline(60, color="seagreen", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Date")
    ax.set_ylabel("Score (0–100)")
    ax.set_ylim(0, 100)
    ax.set_title("Score Components Over Time")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    # Panel 4: Pace vs HR scatter coloured by EF
    ax = axes[1, 1]
    scatter = ax.scatter(
        df["steady_avg_hr"],
        df["steady_pace_min_per_km"],
        c=df["steady_power_per_hr"],
        cmap="RdYlGn",
        s=120,
        edgecolors="black",
        linewidth=0.8,
        vmin=EF_REF_MIN,
        vmax=EF_REF_MAX,
    )
    for _, row in df.iterrows():
        ax.annotate(
            row["date_str"][5:],
            (row["steady_avg_hr"], row["steady_pace_min_per_km"]),
            textcoords="offset points", xytext=(5, 4), fontsize=7, color="dimgray"
        )
    ax.set_xlabel("Steady HR (bpm)")
    ax.set_ylabel("Steady Pace (min/km)")
    ax.invert_yaxis()
    ax.set_title("Pace vs HR (colour = EF W/bpm)")
    ax.grid(True, alpha=0.3)
    colorbar = plt.colorbar(scatter, ax=ax)
    colorbar.set_label("EF (W/bpm)")

    plt.tight_layout()
    plt.savefig(PLOT_REPORT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return PLOT_REPORT_PATH


def run_analysis(fit_dir: Path | None = None, report_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    configure_report_paths(report_dir)
    df = load_run_dataframe(fit_dir)
    df = add_run_scores(df)
    df = add_timeline_status(df)
    df = add_longitudinal_fields(df)
    weekly = build_weekly_summary(df)
    df.to_csv(CSV_REPORT_PATH, index=False)
    write_timeline_report(df, weekly)
    create_plots(df)
    summary = build_console_summary(df, weekly)
    return df, weekly, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Easy run HR tracker")
    parser.add_argument(
        "--fit-dir",
        type=Path,
        default=None,
        help="Directory containing easy-run .fit files (default: data/activities/easy/raw; fallback data/easy_runs)",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
        help="Output report directory (default: reports)",
    )
    args = parser.parse_args(argv)

    try:
        _, _, summary = run_analysis(fit_dir=args.fit_dir, report_dir=args.report_dir)
        print()
        print(summary)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
