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
    filtered = filtered[filtered["speed"] > 0.5]
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
    filtered = filtered[filtered["speed"] > 0.5]
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

        hr_data = records_df["heart_rate"].dropna()
        if hr_data.empty:
            logger.warning("No HR readings in %s", fit_file.name)
            return None

        row = session_df.iloc[0]
        activity_date, filename_mismatch = choose_activity_date(row, fit_file)
        avg_speed = float(
            row.get(
                "enhanced_avg_speed",
                records_df["speed"].dropna().mean() if "speed" in records_df.columns else np.nan,
            )
        )
        avg_power = float(
            row.get(
                "avg_power",
                records_df["power"].dropna().mean() if "power" in records_df.columns else np.nan,
            )
        )
        duration_min = round(float(row.get("total_timer_time", row.get("total_elapsed_time", 0))) / 60, 1)
        distance_km = round(float(row.get("total_distance", 0)) / 1000, 2)
        avg_hr = float(row.get("avg_heart_rate", hr_data.mean()))
        pace_min_per_km = pace_from_speed(avg_speed)
        aerobic_drift_pct = calculate_aerobic_drift(records_df)
        steady_state_metrics = summarize_steady_state(records_df)

        return {
            "file": fit_file.name,
            "date": activity_date,
            "filename_date": extract_date_from_filename(fit_file.name),
            "filename_mismatch": filename_mismatch,
            "avg_hr": round(avg_hr, 1),
            "max_hr": int(hr_data.max()),
            "min_hr": int(hr_data.min()),
            "std_hr": round(hr_data.std(), 1),
            "hr_readings": len(hr_data),
            "avg_power": round(avg_power, 1),
            "avg_speed_mps": round(avg_speed, 3),
            "pace_min_per_km": round(pace_min_per_km, 2) if pace_min_per_km is not None else np.nan,
            "duration_min": duration_min,
            "distance_km": distance_km,
            "power_per_hr": round(avg_power / avg_hr, 3) if avg_hr and not pd.isna(avg_power) else np.nan,
            "speed_per_hr": round(avg_speed / avg_hr, 5) if avg_hr and not pd.isna(avg_speed) else np.nan,
            "aerobic_drift_pct": round(aerobic_drift_pct, 2) if aerobic_drift_pct is not None else np.nan,
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
            f"First run. EF {ef_str} (Joe Friel scale: 0.9 beginner → 2.0 trained); "
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
        f"first run {first_row['steady_power_per_hr']:.3f} W/bpm → "
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


def write_timeline_report(df: pd.DataFrame, weekly: pd.DataFrame) -> Path:
    headline, details = build_overall_assessment(df, weekly)
    lines: list[str] = []
    lines.append("# Easy Run HR Timeline Report")
    lines.append("")
    lines.append(f"Overall status: **{headline}**")
    lines.append("")
    for detail in details:
        lines.append(f"- {detail}")
    lines.append("")
    lines.append("## Report Files")
    lines.append("")
    lines.append(f"- CSV metrics: `{CSV_REPORT_PATH}`")
    lines.append(f"- Plot: `{PLOT_REPORT_PATH}`")
    lines.append(f"- Timeline report: `{TIMELINE_REPORT_PATH}`")
    lines.append("")
    lines.append("## Weekly Summary")
    lines.append("")
    lines.append("| Week | Dates | Runs | Score | EF W/bpm | Decoupling % | Status |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")
    for _, row in weekly.iterrows():
        lines.append(
            f"| {int(row['week'])} | {row['start_date_str']} to {row['end_date_str']} | {int(row['run_count'])} | "
            f"{row['easy_run_score']:.1f} | {row['ef_wbpm']:.3f} | {row['aerobic_drift_pct']:.1f} | {row['timeline_status']} |"
        )
    lines.append("")
    lines.append("## Run Timeline")
    lines.append("")
    lines.append("> Scoring: **EF** (Efficiency Factor, W/bpm) = power÷HR — Joe Friel/TrainingPeaks standard. "
                 "**Aerobic Decoupling** = cardiac drift in steady section — <5% = aerobically fit (Garmin standard). "
                 "Both metrics are load-independent: valid for comparing 5 km and 10 km runs.")
    lines.append("")
    lines.append("| Date | km | min | Score | EF W/bpm | Decoupling % | Stability | Pace | HR | Status | Note |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for _, row in df.iterrows():
        note = row["timeline_note"].replace("|", "/")
        lines.append(
            f"| {row['date_str']} | {row['distance_km']:.2f} | {row['duration_min']:.1f} | {row['easy_run_score']:.1f} | "
            f"{row['steady_power_per_hr']:.3f} | {row['aerobic_drift_pct']:.1f} | {row['stability_score']:.1f} | "
            f"{row['steady_pace_str']} | {row['steady_avg_hr']:.0f} | "
            f"{row['timeline_status']} | {note} |"
        )

    TIMELINE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return TIMELINE_REPORT_PATH


def create_plots(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Easy Run Scorecard — International Metrics", fontsize=16, fontweight="bold")

    # Panel 1: EF trend (primary fitness indicator)
    ax = axes[0, 0]
    ax.plot(df["date"], df["steady_power_per_hr"], marker="o", linewidth=2.5, markersize=7,
            color="midnightblue", label="EF (W/bpm)")
    ax.axhline(1.8, color="seagreen", linestyle="--", linewidth=1.2, label="Trained (1.8)")
    ax.axhline(1.4, color="darkorange", linestyle="--", linewidth=1.2, label="Recreational (1.4)")
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
    x = np.arange(len(df))
    bars = ax.bar(x, df["aerobic_drift_pct"], color=colors, alpha=0.85, edgecolor="black", linewidth=0.7)
    ax.axhline(DECOUPLING_FIT_PCT, color="seagreen", linestyle="--", linewidth=1.5,
               label=f"Fit threshold ({DECOUPLING_FIT_PCT:.0f}%)")
    ax.axhline(8.0, color="crimson", linestyle=":", linewidth=1.2, label="High drift (8%)")
    ax.set_xticks(x)
    ax.set_xticklabels(df["date_str"], rotation=45)
    ax.set_ylabel("Aerobic Decoupling (%)")
    ax.set_title("Aerobic Decoupling %\n(Garmin/Friel standard — <5% = aerobically fit)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper left")

    # Panel 3: Score components over time
    ax = axes[1, 0]
    ax.plot(df["date"], df["ef_score"], marker="o", linewidth=2, markersize=7,
            color="steelblue", label="EF score")
    ax.plot(df["date"], df["decoupling_score"], marker="s", linewidth=2, markersize=7,
            color="darkorange", label="Decoupling score")
    ax.plot(df["date"], df["stability_score"], marker="^", linewidth=2, markersize=7,
            color="slateblue", label="Stability score")
    ax.plot(df["date"], df["easy_run_score"], marker="D", linewidth=2.5, markersize=8,
            color="midnightblue", linestyle="-.", label="Overall score")
    ax.axhline(60, color="seagreen", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Date")
    ax.set_ylabel("Score (0–100)")
    ax.set_ylim(0, 100)
    ax.set_title("Score Components Over Time")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    ax.tick_params(axis="x", rotation=45)

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
