from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.fit_parser import FitParser

DEFAULT_STRENGTH_DIR = Path("data/activities/strength/raw")
DEFAULT_RUNNING_CSV = Path("reports/easy/hr_improvement_analysis.csv")
DEFAULT_OUTPUT_DIR = Path("reports/strength")

HR_ZONE_BOUNDS = (0.60, 0.70, 0.80, 0.90)


@dataclass
class RunningContext:
    before_run: pd.Series | None
    after_run: pd.Series | None


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


def _first_existing(row: pd.Series, keys: list[str]) -> float | None:
    for key in keys:
        if key in row.index:
            out = _safe_float(row.get(key))
            if out is not None:
                return out
    return None


def _compute_hr_zone_distribution(record_df: pd.DataFrame, max_hr_setting: float | None) -> dict[str, float]:
    if record_df.empty or max_hr_setting is None or max_hr_setting <= 0:
        return {
            "hr_z1_pct": np.nan,
            "hr_z2_pct": np.nan,
            "hr_z3_pct": np.nan,
            "hr_z4_pct": np.nan,
            "hr_z5_pct": np.nan,
            "time_high_hr_pct": np.nan,
        }

    if "heart_rate" not in record_df.columns:
        return {
            "hr_z1_pct": np.nan,
            "hr_z2_pct": np.nan,
            "hr_z3_pct": np.nan,
            "hr_z4_pct": np.nan,
            "hr_z5_pct": np.nan,
            "time_high_hr_pct": np.nan,
        }

    hr = pd.to_numeric(record_df["heart_rate"], errors="coerce").dropna()
    if hr.empty:
        return {
            "hr_z1_pct": np.nan,
            "hr_z2_pct": np.nan,
            "hr_z3_pct": np.nan,
            "hr_z4_pct": np.nan,
            "hr_z5_pct": np.nan,
            "time_high_hr_pct": np.nan,
        }

    ratio = hr / max_hr_setting
    z1 = (ratio < HR_ZONE_BOUNDS[0]).mean() * 100
    z2 = ((ratio >= HR_ZONE_BOUNDS[0]) & (ratio < HR_ZONE_BOUNDS[1])).mean() * 100
    z3 = ((ratio >= HR_ZONE_BOUNDS[1]) & (ratio < HR_ZONE_BOUNDS[2])).mean() * 100
    z4 = ((ratio >= HR_ZONE_BOUNDS[2]) & (ratio < HR_ZONE_BOUNDS[3])).mean() * 100
    z5 = (ratio >= HR_ZONE_BOUNDS[3]).mean() * 100

    return {
        "hr_z1_pct": round(float(z1), 1),
        "hr_z2_pct": round(float(z2), 1),
        "hr_z3_pct": round(float(z3), 1),
        "hr_z4_pct": round(float(z4), 1),
        "hr_z5_pct": round(float(z5), 1),
        "time_high_hr_pct": round(float(z4 + z5), 1),
    }


def _compute_hr_drift(record_df: pd.DataFrame) -> float | None:
    if record_df.empty or "heart_rate" not in record_df.columns:
        return None
    hr = pd.to_numeric(record_df["heart_rate"], errors="coerce").dropna().reset_index(drop=True)
    if len(hr) < 30:
        return None

    n = len(hr)
    early = hr.iloc[: max(5, int(n * 0.2))].mean()
    late = hr.iloc[min(n - 1, int(n * 0.8)) :].mean()
    if pd.isna(early) or pd.isna(late):
        return None
    return round(float(late - early), 1)


def _compute_recovery_cost(duration_min: float | None, avg_hr: float | None, max_hr_setting: float | None,
                           training_effect: float | None, hr_drift_bpm: float | None) -> float:
    duration_component = 0.0 if duration_min is None else min(100.0, (duration_min / 90.0) * 100.0)

    if avg_hr is None or max_hr_setting is None or max_hr_setting <= 0:
        intensity_component = 0.0
    else:
        intensity_component = min(100.0, max(0.0, (avg_hr / max_hr_setting) * 100.0))

    te_component = 0.0 if training_effect is None else min(100.0, (training_effect / 5.0) * 100.0)

    if hr_drift_bpm is None:
        drift_component = 30.0
    else:
        drift_component = min(100.0, max(0.0, (hr_drift_bpm + 5.0) * 8.0))

    score = 0.35 * duration_component + 0.35 * intensity_component + 0.20 * te_component + 0.10 * drift_component
    return round(float(score), 1)


def _fatigue_band(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 55:
        return "moderate"
    return "low"


def _read_running_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    if "date" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _find_running_context(running_df: pd.DataFrame, strength_date: pd.Timestamp,
                          window_days: int = 3) -> RunningContext:
    if running_df.empty:
        return RunningContext(before_run=None, after_run=None)

    before_candidates = running_df[running_df["date"] <= strength_date].copy()
    after_candidates = running_df[running_df["date"] >= strength_date].copy()

    before_run = None
    after_run = None

    if not before_candidates.empty:
        before = before_candidates.iloc[-1]
        if (strength_date - before["date"]).days <= window_days:
            before_run = before

    if not after_candidates.empty:
        after = after_candidates.iloc[0]
        if (after["date"] - strength_date).days <= window_days:
            after_run = after

    return RunningContext(before_run=before_run, after_run=after_run)


def _interaction_row(session_row: dict[str, Any], running_ctx: RunningContext) -> dict[str, Any]:
    out = {
        "date": session_row["date"],
        "strength_file": session_row["file"],
        "run_before_date": None,
        "run_after_date": None,
        "days_to_before_run": None,
        "days_to_after_run": None,
        "easy_score_change_after_vs_before": None,
        "steady_pace_change_after_vs_before_pct": None,
        "steady_hr_change_after_vs_before_pct": None,
        "drift_change_after_vs_before_pct_pts": None,
        "interaction_signal": "insufficient_data",
    }

    before = running_ctx.before_run
    after = running_ctx.after_run

    if before is not None:
        out["run_before_date"] = before["date"]
        out["days_to_before_run"] = int((session_row["date"] - before["date"]).days)

    if after is not None:
        out["run_after_date"] = after["date"]
        out["days_to_after_run"] = int((after["date"] - session_row["date"]).days)

    if before is None or after is None:
        return out

    def _pct_change(first: float | None, last: float | None) -> float | None:
        if first is None or last is None:
            return None
        if first == 0:
            return None
        return (last / first - 1.0) * 100.0

    before_score = _safe_float(before.get("easy_run_score"))
    after_score = _safe_float(after.get("easy_run_score"))
    before_pace = _safe_float(before.get("steady_pace_min_per_km"))
    after_pace = _safe_float(after.get("steady_pace_min_per_km"))
    before_hr = _safe_float(before.get("steady_avg_hr"))
    after_hr = _safe_float(after.get("steady_avg_hr"))
    before_drift = _safe_float(before.get("aerobic_drift_pct"))
    after_drift = _safe_float(after.get("aerobic_drift_pct"))

    score_delta = None
    if before_score is not None and after_score is not None:
        score_delta = round(after_score - before_score, 2)

    pace_delta_pct = _pct_change(before_pace, after_pace)
    hr_delta_pct = _pct_change(before_hr, after_hr)
    drift_delta = None
    if before_drift is not None and after_drift is not None:
        drift_delta = round(after_drift - before_drift, 2)

    out["easy_score_change_after_vs_before"] = score_delta
    out["steady_pace_change_after_vs_before_pct"] = round(pace_delta_pct, 2) if pace_delta_pct is not None else None
    out["steady_hr_change_after_vs_before_pct"] = round(hr_delta_pct, 2) if hr_delta_pct is not None else None
    out["drift_change_after_vs_before_pct_pts"] = drift_delta

    positive = 0
    negative = 0

    if score_delta is not None:
        if score_delta >= 2.0:
            positive += 1
        elif score_delta <= -2.0:
            negative += 1

    if pace_delta_pct is not None:
        if pace_delta_pct <= -1.0:
            positive += 1
        elif pace_delta_pct >= 1.0:
            negative += 1

    if hr_delta_pct is not None:
        if hr_delta_pct <= -1.0:
            positive += 1
        elif hr_delta_pct >= 1.0:
            negative += 1

    if drift_delta is not None:
        if drift_delta <= -1.0:
            positive += 1
        elif drift_delta >= 1.0:
            negative += 1

    if positive > negative:
        out["interaction_signal"] = "potential_positive_transfer"
    elif negative > positive:
        out["interaction_signal"] = "possible_interference"
    else:
        out["interaction_signal"] = "neutral_or_inconclusive"

    return out


def _weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    w = df.copy()
    w["week_start"] = w["date"].dt.to_period("W").apply(lambda p: p.start_time)

    grouped = (
        w.groupby("week_start", as_index=False)
        .agg(
            strength_sessions=("file", "count"),
            total_duration_min=("duration_min", "sum"),
            total_repetitions=("total_repetitions", "sum"),
            total_est_load_kg=("estimated_total_load_kg", "sum"),
            avg_recovery_cost=("recovery_cost_score", "mean"),
            avg_training_effect=("training_effect", "mean"),
            high_fatigue_sessions=("fatigue_risk", lambda s: int((s == "high").sum())),
        )
    )

    grouped["sustainability_flag"] = grouped.apply(
        lambda r: (
            "sustainable"
            if r["strength_sessions"] <= 3 and r["avg_recovery_cost"] < 65
            else "watch_load"
        ),
        axis=1,
    )

    numeric_cols = [
        "total_duration_min",
        "total_repetitions",
        "total_est_load_kg",
        "avg_recovery_cost",
        "avg_training_effect",
    ]
    for col in numeric_cols:
        grouped[col] = grouped[col].round(2)

    return grouped


def _transfer_observations(interactions_df: pd.DataFrame, sessions_df: pd.DataFrame) -> pd.DataFrame:
    observations: list[dict[str, Any]] = []

    if sessions_df.empty:
        return pd.DataFrame(
            [{"observation": "No strength sessions found", "value": "n/a", "note": "Check strength input folder"}]
        )

    observations.append(
        {
            "observation": "strength_session_count",
            "value": int(len(sessions_df)),
            "note": "Total strength sessions analyzed",
        }
    )

    observations.append(
        {
            "observation": "avg_recovery_cost_score",
            "value": round(float(sessions_df["recovery_cost_score"].mean()), 2),
            "note": "Lower is easier to absorb into endurance plan",
        }
    )

    observations.append(
        {
            "observation": "high_fatigue_share_pct",
            "value": round(float((sessions_df["fatigue_risk"] == "high").mean() * 100), 1),
            "note": "Share of sessions classified as high fatigue risk",
        }
    )

    if not interactions_df.empty:
        signal_counts = interactions_df["interaction_signal"].value_counts(dropna=False).to_dict()
        for signal, count in signal_counts.items():
            observations.append(
                {
                    "observation": f"interaction_{signal}",
                    "value": int(count),
                    "note": "Count of strength sessions with this running interaction signal",
                }
            )

    return pd.DataFrame(observations)


def _session_recommendations(row: pd.Series, interaction_row: pd.Series | None) -> str:
    recs: list[str] = []

    fatigue = str(row.get("fatigue_risk", "low"))
    if fatigue == "high":
        recs.append("Prioritize 24-36h recovery before key endurance quality sessions")
    elif fatigue == "moderate":
        recs.append("Keep next day run easy and monitor HR response")
    else:
        recs.append("Current strength dose appears compatible with endurance workload")

    time_high_hr = _safe_float(row.get("time_high_hr_pct"))
    if time_high_hr is not None and time_high_hr > 20:
        recs.append("Limit high-intensity overlap: avoid pairing with interval run on same or next day")

    estimated_load = _safe_float(row.get("estimated_total_load_kg"))
    if estimated_load is None:
        recs.append("Capture external load (kg per set) to improve neuromuscular fatigue precision")

    if interaction_row is not None:
        signal = str(interaction_row.get("interaction_signal", ""))
        if signal == "possible_interference":
            recs.append("Move heavy strength farther from quality run day and reassess")
        elif signal == "potential_positive_transfer":
            recs.append("Current sequencing may support transfer; maintain and monitor trend")

    return "; ".join(recs)


def _write_markdown_report(
    sessions_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    weekly_df: pd.DataFrame,
    transfer_df: pd.DataFrame,
    output_path: Path,
) -> None:
    lines: list[str] = []
    lines.append("# Strength-Endurance Integration Analysis")
    lines.append("")
    lines.append("## Scope")
    lines.append("- Objective: evaluate strength-load stress, recovery cost, fatigue risk, and transfer signals to running")
    lines.append(f"- Sessions analyzed: {len(sessions_df)}")
    lines.append("")

    if sessions_df.empty:
        lines.append("No sessions found in the configured strength input directory.")
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return

    for _, row in sessions_df.sort_values("date").iterrows():
        interaction_row = None
        if not interactions_df.empty:
            matched = interactions_df[interactions_df["strength_file"] == row["file"]]
            if not matched.empty:
                interaction_row = matched.iloc[0]

        lines.append(f"## Session: {row['file']} ({row['date'].strftime('%Y-%m-%d')})")
        lines.append("")

        lines.append("### 1. Executive Summary")
        lines.append(
            f"- Strength load: {int(row['sets_count'])} sets, {int(row['total_repetitions'])} reps, "
            f"estimated load {row['estimated_total_load_kg'] if pd.notna(row['estimated_total_load_kg']) else 'n/a'} kg"
        )
        lines.append(
            f"- Session stress: recovery cost score {row['recovery_cost_score']}/100, fatigue risk {row['fatigue_risk']}"
        )
        lines.append(
            f"- Transfer signal: {interaction_row['interaction_signal'] if interaction_row is not None else 'insufficient_data'}"
        )
        lines.append("")

        lines.append("### 2. Workout Breakdown")
        lines.append(f"- Duration: {row['duration_min']} min")
        lines.append(f"- Exercise list: {row['exercise_list']}")
        lines.append(f"- Sets/Reps: {int(row['sets_count'])}/{int(row['total_repetitions'])}")
        lines.append(f"- Rest intervals total: {row['total_rest_s']} s")
        lines.append(
            f"- Total load availability: {'available' if pd.notna(row['estimated_total_load_kg']) else 'not available (weight missing)'}"
        )
        lines.append("")

        lines.append("### 3. Physiological Stress Analysis")
        lines.append(f"- Average HR: {row['avg_hr']} bpm")
        lines.append(f"- Max HR: {row['max_hr']} bpm")
        lines.append(
            f"- HR zones: Z1 {row['hr_z1_pct']}%, Z2 {row['hr_z2_pct']}%, Z3 {row['hr_z3_pct']}%, "
            f"Z4 {row['hr_z4_pct']}%, Z5 {row['hr_z5_pct']}%"
        )
        lines.append(f"- Training Effect: aerobic {row['training_effect']}, anaerobic {row['anaerobic_training_effect']}")
        lines.append(f"- Exercise load field: {row['exercise_load'] if pd.notna(row['exercise_load']) else 'not recorded'}")
        lines.append("")

        lines.append("### 4. Recovery Impact")
        lines.append(f"- Recovery recommendation field: {row['recovery_recommendation_h'] if pd.notna(row['recovery_recommendation_h']) else 'not available'}")
        lines.append(f"- Body Battery field: {row['body_battery'] if pd.notna(row['body_battery']) else 'not available'}")
        lines.append(f"- HRV status field: {row['hrv_status'] if pd.notna(row['hrv_status']) else 'not available'}")
        lines.append(f"- Stress field: {row['stress_level'] if pd.notna(row['stress_level']) else 'not available'}")
        lines.append(
            f"- Recovery cost interpretation: {'high recovery demand' if row['recovery_cost_score'] >= 75 else 'moderate recovery demand' if row['recovery_cost_score'] >= 55 else 'low recovery demand'}"
        )
        lines.append("")

        lines.append("### 5. Interaction With Running")
        if interaction_row is None:
            lines.append("- No nearby easy-run context available within the analysis window")
        else:
            lines.append(f"- Before run date: {interaction_row['run_before_date'] if pd.notna(interaction_row['run_before_date']) else 'n/a'}")
            lines.append(f"- After run date: {interaction_row['run_after_date'] if pd.notna(interaction_row['run_after_date']) else 'n/a'}")
            lines.append(
                f"- Easy score change after vs before: {interaction_row['easy_score_change_after_vs_before'] if pd.notna(interaction_row['easy_score_change_after_vs_before']) else 'n/a'}"
            )
            lines.append(
                f"- Pace change after vs before (%): {interaction_row['steady_pace_change_after_vs_before_pct'] if pd.notna(interaction_row['steady_pace_change_after_vs_before_pct']) else 'n/a'}"
            )
            lines.append(
                f"- HR change after vs before (%): {interaction_row['steady_hr_change_after_vs_before_pct'] if pd.notna(interaction_row['steady_hr_change_after_vs_before_pct']) else 'n/a'}"
            )
            lines.append(f"- Interaction signal: {interaction_row['interaction_signal']}")
        lines.append("")

        lines.append("### 6. Fatigue Risk")
        lines.append(f"- Neuromuscular fatigue proxy (HR drift): {row['hr_drift_bpm']} bpm")
        lines.append(f"- Time in high HR zones (Z4+Z5): {row['time_high_hr_pct']}%")
        lines.append(f"- Elevated HR flag: {row['elevated_hr_flag']}")
        lines.append(f"- Final fatigue risk: {row['fatigue_risk']}")
        lines.append("")

        lines.append("### 7. Recommendations")
        lines.append(f"- { _session_recommendations(row, interaction_row) }")
        lines.append("")

    lines.append("## Final Output Tables")
    lines.append("### Weekly Strength-Load Summary")
    if weekly_df.empty:
        lines.append("- Not enough data for weekly summary")
    else:
        for _, w in weekly_df.iterrows():
            lines.append(
                f"- Week {pd.to_datetime(w['week_start']).strftime('%Y-%m-%d')}: "
                f"sessions {int(w['strength_sessions'])}, duration {w['total_duration_min']} min, "
                f"recovery cost {w['avg_recovery_cost']}, sustainability {w['sustainability_flag']}"
            )

    lines.append("")
    lines.append("### Recovery Interaction Analysis")
    if interactions_df.empty:
        lines.append("- No running interaction rows generated")
    else:
        signal_counts = interactions_df["interaction_signal"].value_counts().to_dict()
        for signal, count in signal_counts.items():
            lines.append(f"- {signal}: {count} session(s)")

    lines.append("")
    lines.append("### Running-Performance Transfer Observations")
    for _, row in transfer_df.iterrows():
        lines.append(f"- {row['observation']}: {row['value']} ({row['note']})")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def analyze_strength_endurance(
    strength_dir: Path,
    running_csv: Path,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    fit_files = sorted(strength_dir.glob("*.fit")) if strength_dir.exists() else []
    running_df = _read_running_df(running_csv)

    session_rows: list[dict[str, Any]] = []
    interaction_rows: list[dict[str, Any]] = []

    for fit_file in fit_files:
        parser = FitParser(fit_file)
        parser.parse()

        session_df = parser.session
        if session_df.empty:
            continue

        session = session_df.iloc[0]
        sets_df = parser.sets_summary
        record_df = parser.records
        zones_df = parser._dfs.get("zones_target", pd.DataFrame())
        zones_row = zones_df.iloc[0] if not zones_df.empty else pd.Series(dtype=object)

        activity_date = _safe_timestamp(session.get("start_time") or session.get("timestamp"))
        if activity_date is None:
            activity_date = pd.Timestamp(fit_file.stat().st_mtime, unit="s")

        duration_min = _safe_float(session.get("total_timer_time") or session.get("total_elapsed_time"))
        duration_min = round(duration_min / 60.0, 1) if duration_min is not None else None

        avg_hr = _first_existing(session, ["avg_heart_rate"])
        max_hr = _first_existing(session, ["max_heart_rate"])
        training_effect = _first_existing(session, ["total_training_effect", "training_effect"])
        anaerobic_training_effect = _first_existing(session, ["total_anaerobic_training_effect", "anaerobic_training_effect"])
        exercise_load = _first_existing(session, ["exercise_load", "training_load"])
        max_hr_setting = _first_existing(zones_row, ["max_heart_rate"])

        zone_distribution = _compute_hr_zone_distribution(record_df, max_hr_setting)
        hr_drift_bpm = _compute_hr_drift(record_df)

        sets_count = int(len(sets_df)) if not sets_df.empty else 0
        total_repetitions = int(pd.to_numeric(sets_df.get("repetitions", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not sets_df.empty else 0
        total_rest_s = float(pd.to_numeric(sets_df.get("rest_s", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not sets_df.empty else 0.0

        exercise_labels = []
        if not sets_df.empty and "exercise_label" in sets_df.columns:
            exercise_labels = [str(v).strip() for v in sets_df["exercise_label"].dropna().astype(str).tolist() if str(v).strip() and str(v).strip().lower() != "none"]
        exercise_list = ", ".join(sorted(set(exercise_labels))) if exercise_labels else "Unknown"

        estimated_total_load_kg = np.nan
        if not sets_df.empty and "weight_kg" in sets_df.columns and "repetitions" in sets_df.columns:
            tmp = sets_df[["weight_kg", "repetitions"]].copy()
            tmp["weight_kg"] = pd.to_numeric(tmp["weight_kg"], errors="coerce")
            tmp["repetitions"] = pd.to_numeric(tmp["repetitions"], errors="coerce")
            tmp = tmp.dropna(subset=["weight_kg", "repetitions"])
            if not tmp.empty:
                estimated_total_load_kg = float((tmp["weight_kg"] * tmp["repetitions"]).sum())

        recovery_cost = _compute_recovery_cost(duration_min, avg_hr, max_hr_setting, training_effect, hr_drift_bpm)
        fatigue_risk = _fatigue_band(recovery_cost)

        elevated_hr_flag = False
        if avg_hr is not None and max_hr_setting is not None and max_hr_setting > 0:
            elevated_hr_flag = (avg_hr / max_hr_setting) >= 0.78
        if not elevated_hr_flag and not pd.isna(zone_distribution["time_high_hr_pct"]):
            elevated_hr_flag = zone_distribution["time_high_hr_pct"] >= 20.0

        session_row = {
            "file": fit_file.name,
            "date": activity_date.tz_localize(None) if activity_date.tzinfo else activity_date,
            "duration_min": duration_min,
            "exercise_list": exercise_list,
            "sets_count": sets_count,
            "total_repetitions": total_repetitions,
            "total_rest_s": round(total_rest_s, 1),
            "estimated_total_load_kg": round(estimated_total_load_kg, 1) if not pd.isna(estimated_total_load_kg) else np.nan,
            "avg_hr": avg_hr,
            "max_hr": max_hr,
            "training_effect": training_effect,
            "anaerobic_training_effect": anaerobic_training_effect,
            "exercise_load": exercise_load,
            "max_hr_setting": max_hr_setting,
            "recovery_recommendation_h": np.nan,
            "body_battery": np.nan,
            "hrv_status": np.nan,
            "stress_level": np.nan,
            "hr_drift_bpm": hr_drift_bpm,
            "elevated_hr_flag": elevated_hr_flag,
            "recovery_cost_score": recovery_cost,
            "fatigue_risk": fatigue_risk,
            **zone_distribution,
        }

        running_ctx = _find_running_context(running_df, session_row["date"], window_days=3)
        interaction_row = _interaction_row(session_row, running_ctx)

        session_rows.append(session_row)
        interaction_rows.append(interaction_row)

    sessions_df = pd.DataFrame(session_rows)
    interactions_df = pd.DataFrame(interaction_rows)

    if not sessions_df.empty:
        sessions_df = sessions_df.sort_values("date").reset_index(drop=True)

    weekly_df = _weekly_summary(sessions_df)
    transfer_df = _transfer_observations(interactions_df, sessions_df)

    sessions_csv = output_dir / "strength_endurance_sessions.csv"
    weekly_csv = output_dir / "strength_weekly_summary.csv"
    interaction_csv = output_dir / "strength_recovery_interaction.csv"
    transfer_csv = output_dir / "strength_running_transfer_observations.csv"
    report_md = output_dir / "strength_endurance_integration_report.md"

    sessions_df.to_csv(sessions_csv, index=False)
    weekly_df.to_csv(weekly_csv, index=False)
    interactions_df.to_csv(interaction_csv, index=False)
    transfer_df.to_csv(transfer_csv, index=False)

    _write_markdown_report(
        sessions_df=sessions_df,
        interactions_df=interactions_df,
        weekly_df=weekly_df,
        transfer_df=transfer_df,
        output_path=report_md,
    )

    return {
        "sessions_csv": sessions_csv,
        "weekly_csv": weekly_csv,
        "interaction_csv": interaction_csv,
        "transfer_csv": transfer_csv,
        "report_md": report_md,
    }


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze strength-endurance integration from Garmin FIT sessions")
    parser.add_argument("--strength-dir", type=Path, default=DEFAULT_STRENGTH_DIR, help="Directory containing strength .fit files")
    parser.add_argument("--running-csv", type=Path, default=DEFAULT_RUNNING_CSV, help="Running metrics CSV for interaction analysis")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for reports and datasets")
    return parser


def main() -> int:
    args = build_cli().parse_args()
    outputs = analyze_strength_endurance(
        strength_dir=args.strength_dir,
        running_csv=args.running_csv,
        output_dir=args.output_dir,
    )

    print("Generated outputs:")
    for _, path in outputs.items():
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
