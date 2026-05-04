"""
theEagle – main entry point
============================
Batch-parses all .fit files found in data/raw/ and writes per-message-type
CSVs to data/processed/<activity_name>/.

Usage:
    uv run python main.py                   # parse all .fit in data/raw/
    uv run python main.py path/to/run.fit   # parse a single file
"""

import sys
import logging
from pathlib import Path

import pandas as pd
from src.fit_parser import FitParser

logging.basicConfig(level=logging.INFO, format="%(message)s")

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")


def _fmt_mm_ss(seconds: float) -> str:
    """Format seconds as M:SS.s (or M:SS when near whole-second)."""
    if pd.isna(seconds):
        return "0:00"
    total = float(seconds)
    mins = int(total // 60)
    secs = total - (mins * 60)
    if abs(secs - round(secs)) < 0.05:
        return f"{mins}:{int(round(secs)):02d}"
    return f"{mins}:{secs:04.1f}"


def parse_file(fit_path: Path):
    print(f"\n{'='*60}")
    print(f"Parsing: {fit_path.name}")
    print(f"{'='*60}")
    parser = FitParser(fit_path)
    dfs = parser.parse()
    parser.save(output_dir=OUT_DIR)

    print(f"\nActivity type : {parser.activity_type.upper()}")

    # Extract session summary metrics
    session_info = parser.get_session_summary()
    if session_info:
        def _fmt_dt(dt_value, fmt: str) -> str:
            if pd.isna(dt_value):
                return "N/A"
            return pd.Timestamp(dt_value).strftime(fmt)

        print(f"\nSession Metrics:")
        if session_info.get("workout_date"):
            print(f"  Date            : {_fmt_dt(session_info['workout_date'], '%Y-%m-%d')}")
        if session_info.get("start_time") or session_info.get("end_time"):
            start_str = _fmt_dt(session_info.get("start_time"), "%H:%M:%S")
            end_str = _fmt_dt(session_info.get("end_time"), "%H:%M:%S")
            print(f"  Time window     : {start_str} to {end_str}")
        if "total_elapsed_time_min" in session_info:
            print(f"  Duration        : {session_info['total_elapsed_time_min']} min")
        if "total_calories" in session_info:
            active = session_info.get("active_calories", 0)
            resting = session_info.get("resting_calories", 0)
            total = session_info["total_calories"]
            print(f"  Calories burned : {active} kcal active + {resting} kcal resting = {total} kcal total")
        if session_info.get("avg_heart_rate"):
            hr_info = f"{session_info['avg_heart_rate']} bpm avg"
            if session_info.get("min_heart_rate"):
                hr_info += f" (min: {session_info['min_heart_rate']}, "
            if session_info.get("max_heart_rate"):
                hr_info += f"max: {session_info['max_heart_rate']})"
            print(f"  Heart rate      : {hr_info}")

    if parser.activity_type == "running":
        rec = parser.records
        if not rec.empty:
            duration_min = round(len(rec) / 60, 1)
            print(f"Data points     : {len(rec)} ({duration_min} min @ 1 Hz)")
            cols = [c for c in ["heart_rate", "speed", "power", "cadence", "pace_min_per_km"]
                    if c in rec.columns]
            if cols:
                print(f"Metrics         : {', '.join(cols)}")

    elif parser.activity_type == "strength":
        sets = parser.sets_summary
        if not sets.empty:
            print(f"Total sets      : {len(sets)}")
            if "exercise_label" in sets.columns:
                exercises = sets["exercise_label"].dropna().unique()
                print(f"Exercises       : {', '.join(exercises[:5])}", end="")
                if len(exercises) > 5:
                    print(f" + {len(exercises) - 5} more")
                else:
                    print()

            # Show per-exercise metrics
            ex_summary = parser.get_exercise_summary()
            if not ex_summary.empty:
                print(f"\nPer-Exercise Metrics:")
                COL_W = 28
                print(f"{'Exercise':<{COL_W}} {'Sets':>5} {'Dur(s)':>8} {'Reps':>6} "
                      f"{'Wt(kg)':>8} {'Cals':>7} {'HR Avg':>8} {'HR(min-max)':>12}")
                print("-" * (COL_W + 58))
                for _, row in ex_summary.iterrows():
                    hr_range = ""
                    if pd.notna(row.get("min_heart_rate")):
                        hr_range = f"{int(row['min_heart_rate'])}-{int(row['max_heart_rate'])}"
                    hr_avg = f"{int(row['avg_heart_rate'])}" if pd.notna(row.get("avg_heart_rate")) else "N/A"
                    cals = f"{row['calories']:.1f}" if pd.notna(row.get('calories')) else "0.0"
                    label = str(row['exercise_label'])
                    label = label[:COL_W - 3] + '..' if len(label) > COL_W else label
                    print(f"{label:<{COL_W}} {int(row['sets_count']):>5} "
                          f"{row['total_duration_s']:>8.1f} {int(row['total_repetitions']):>6} "
                          f"{row['avg_weight_kg']:>8.2f} {cals:>7} {hr_avg:>8} {hr_range:>12}")

            print("\nSet Details (Garmin-style):")
            print(f"{'Set':>3} {'Exercise':<35} {'Time':>8} {'Rest':>8} {'Reps':>6} {'Weight':>12}")
            print("-" * 80)
            display_sets = sets.sort_values("message_index") if "message_index" in sets.columns else sets
            for idx, (_, row) in enumerate(display_sets.iterrows(), start=1):
                ex_name = str(row.get("exercise_label") or "Unknown")
                time_s = _fmt_mm_ss(row.get("duration_s", 0))
                rest_s = _fmt_mm_ss(row.get("rest_s", 0))

                reps_val = row.get("repetitions")
                reps_str = "" if pd.isna(reps_val) else str(int(reps_val))

                wt_val = row.get("weight_kg")
                if pd.isna(wt_val):
                    weight_str = "--"
                elif abs(float(wt_val)) < 0.001:
                    weight_str = "Bodyweight"
                else:
                    weight_str = f"{float(wt_val):.1f} kg"

                ex_name_d = ex_name[:33] + '..' if len(ex_name) > 35 else ex_name
                print(f"{idx:>3} {ex_name_d:<35} {time_s:>8} {rest_s:>8} {reps_str:>6} {weight_str:>12}")


    print("\nMessage types extracted:")
    for name, df in dfs.items():
        print(f"  {name:<22} {len(df):>5} rows  {len(df.columns):>3} cols")


def main():
    # Single file passed as argument
    if len(sys.argv) > 1:
        fit_path = Path(sys.argv[1])
        if not fit_path.exists():
            print(f"Error: file not found – {fit_path}")
            sys.exit(1)
        parse_file(fit_path)
        return

    # Batch mode: process every .fit in data/raw/
    fit_files = sorted(RAW_DIR.glob("*.fit"))
    if not fit_files:
        print(f"No .fit files found in {RAW_DIR}/")
        print("Drop your Garmin .fit files into data/raw/ and run again.")
        return

    print(f"Found {len(fit_files)} .fit file(s) in {RAW_DIR}/")
    for fit_path in fit_files:
        try:
            parse_file(fit_path)
        except Exception as exc:
            print(f"[ERROR] {fit_path.name}: {exc}")

    print(f"\nDone. All outputs in {OUT_DIR}/")


if __name__ == "__main__":
    main()

