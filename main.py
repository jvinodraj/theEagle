"""
theEagle – main entry point
============================
Unified CLI to parse FIT files and run easy-run scorecards.

Standardized layout:
    data/activities/<category>/raw
    data/activities/<category>/processed

Usage:
    uv run python main.py parse --category all
    uv run python main.py parse --category easy
    uv run python main.py parse --category strength
    uv run python main.py parse --category custom_category
    uv run python main.py parse --file path/to/run.fit --category easy
    uv run python main.py easy-score
    uv run python main.py run-all
"""

import argparse
import logging
from pathlib import Path

import pandas as pd
from src.fit_parser import FitParser
from src import hr_improvement_tracker as easy_tracker

logging.basicConfig(level=logging.INFO, format="%(message)s")

DATA_ROOT = Path("data/activities")
LEGACY_RAW_DIR = Path("data/raw")
LEGACY_EASY_DIR = Path("data/easy_runs")


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


def _category_raw_dir(category: str) -> Path:
    return DATA_ROOT / category / "raw"


def _category_processed_dir(category: str) -> Path:
    return DATA_ROOT / category / "processed"


def _ensure_category_structure(category: str) -> tuple[Path, Path]:
    raw_dir = _category_raw_dir(category)
    processed_dir = _category_processed_dir(category)
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, processed_dir


def _discover_categories() -> list[str]:
    categories: set[str] = set()
    if DATA_ROOT.exists():
        for category_dir in DATA_ROOT.iterdir():
            if category_dir.is_dir() and (category_dir / "raw").exists():
                categories.add(category_dir.name)
    # Legacy compatibility for existing repositories
    if LEGACY_EASY_DIR.exists():
        categories.add("easy")
    if LEGACY_RAW_DIR.exists():
        categories.add("general")
    return sorted(categories)


def _resolve_raw_dir(category: str) -> Path:
    if category == "easy":
        standardized = _category_raw_dir("easy")
        if standardized.exists() and any(standardized.glob("*.fit")):
            return standardized
        if LEGACY_EASY_DIR.exists() and any(LEGACY_EASY_DIR.glob("*.fit")):
            return LEGACY_EASY_DIR
        if standardized.exists():
            return standardized
        if LEGACY_EASY_DIR.exists():
            return LEGACY_EASY_DIR
    if category == "general":
        standardized = _category_raw_dir("general")
        if standardized.exists() and any(standardized.glob("*.fit")):
            return standardized
        if LEGACY_RAW_DIR.exists() and any(LEGACY_RAW_DIR.glob("*.fit")):
            return LEGACY_RAW_DIR
        if standardized.exists():
            return standardized
        if LEGACY_RAW_DIR.exists():
            return LEGACY_RAW_DIR
    return _category_raw_dir(category)


def parse_file(fit_path: Path, out_root: Path):
    print(f"\n{'='*60}")
    print(f"Parsing: {fit_path.name}")
    print(f"{'='*60}")
    parser = FitParser(fit_path)
    dfs = parser.parse()
    parser.save(output_dir=out_root)

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


def run_parse_for_category(category: str) -> int:
    raw_dir, processed_dir = _ensure_category_structure(category)
    source_dir = _resolve_raw_dir(category)
    fit_files = sorted(source_dir.glob("*.fit"))

    if not fit_files:
        print(f"No .fit files found in {source_dir}/")
        print(f"Drop your Garmin .fit files into {raw_dir}/ and run again.")
        return 0

    print(f"Found {len(fit_files)} .fit file(s) in {source_dir}/ [category: {category}]")
    for fit_path in fit_files:
        try:
            parse_file(fit_path, processed_dir)
        except Exception as exc:
            print(f"[ERROR] {fit_path.name}: {exc}")

    print(f"\nDone. Outputs in {processed_dir}/")
    return 0


def run_parse_single_file(fit_path: Path, category: str) -> int:
    if not fit_path.exists():
        print(f"Error: file not found – {fit_path}")
        return 1

    _, processed_dir = _ensure_category_structure(category)
    parse_file(fit_path, processed_dir)
    print(f"\nDone. Output in {processed_dir}/")
    return 0


def run_easy_score(report_dir: Path) -> int:
    easy_raw = _resolve_raw_dir("easy")
    if not easy_raw.exists():
        easy_raw.mkdir(parents=True, exist_ok=True)

    try:
        _, _, summary = easy_tracker.run_analysis(fit_dir=easy_raw, report_dir=report_dir)
        print()
        print(summary)
        return 0
    except Exception as exc:
        print(f"[ERROR] easy-score: {exc}")
        return 1


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="theEagle unified CLI")
    sub = parser.add_subparsers(dest="command")

    parse_cmd = sub.add_parser("parse", help="Parse FIT files into CSVs")
    parse_cmd.add_argument(
        "--category",
        default="all",
        help="Category under data/activities/<category>/raw (easy, strength, etc.) or 'all'",
    )
    parse_cmd.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Parse one FIT file into the category's processed directory",
    )

    easy_cmd = sub.add_parser("easy-score", help="Run easy-run HR scorecard")
    easy_cmd.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
        help="Output report directory for scorecard files",
    )

    sub.add_parser("init", help="Create standard category directory layout")

    all_cmd = sub.add_parser("run-all", help="Run parse-all + easy-score workflow")
    all_cmd.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
        help="Output report directory for easy scorecard files",
    )
    return parser


def main() -> int:
    parser = build_cli()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "init":
        for category in ["easy", "strength", "general"]:
            raw_dir, processed_dir = _ensure_category_structure(category)
            print(f"Created/checked: {raw_dir}")
            print(f"Created/checked: {processed_dir}")
        return 0

    if args.command == "easy-score":
        return run_easy_score(args.report_dir)

    if args.command == "run-all":
        categories = _discover_categories()
        if not categories:
            print("No categories found.")
            print("Run: uv run python main.py init")
            return 0
        exit_code = 0
        for category in categories:
            rc = run_parse_for_category(category)
            exit_code = rc if rc != 0 else exit_code
        rc = run_easy_score(args.report_dir)
        return rc if rc != 0 else exit_code

    if args.command == "parse":
        if args.file is not None:
            return run_parse_single_file(args.file, args.category if args.category != "all" else "general")

        if args.category == "all":
            categories = _discover_categories()
            if not categories:
                print("No categories found.")
                print("Run: uv run python main.py init")
                return 0
            exit_code = 0
            for category in categories:
                rc = run_parse_for_category(category)
                exit_code = rc if rc != 0 else exit_code
            return exit_code

        return run_parse_for_category(args.category)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

