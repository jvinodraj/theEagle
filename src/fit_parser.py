"""
FIT File Parser
---------------
Parses all message types from a Garmin .fit file and writes each message
type to its own CSV inside:

    data/processed/<activity_stem>/
        record.csv            – per-second stream (HR, power, cadence, speed …)
        lap.csv               – lap summaries
        session.csv           – overall session summary
        device_info.csv       – device / sensor info
        event.csv             – start/stop/lap events
        <other>.csv           – any other message type present

    For strength activities, an additional enriched file is written:
        sets_summary.csv      – active sets joined with exercise names,
                                 reps, weight, and duration

Supported activity types (auto-detected):
    running   – outdoor / treadmill run
    strength  – strength training / gym
    other     – everything else (cycling, swimming, …)

Usage (programmatic):
    from src.fit_parser import FitParser
    parser = FitParser("data/raw/my_run.fit")
    dfs = parser.parse()                    # dict[str, pd.DataFrame]
    parser.save(output_dir="data/processed")
    print(parser.activity_type)             # "running" | "strength" | "other"

Usage (CLI):
    uv run python -m src.fit_parser data/raw/my_run.fit
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import pytz
from fitparse import FitFile

logger = logging.getLogger(__name__)

# Timezone for timestamp conversion
_UTC = pytz.UTC
_LOCAL_TZ = pytz.timezone("Asia/Kolkata")

# Columns to convert from semicircles → decimal degrees
_SEMICIRCLE_FIELDS = {"position_lat", "position_long"}
_SEMICIRCLE_TO_DEG = 180.0 / (2**31)

# sport / sub_sport values that identify activity types
_RUNNING_SPORTS = {"running", "treadmill"}
_STRENGTH_SPORTS = {"strength_training", "training"}


def _extract_estimated_sweat_loss_ml(session_row) -> float | None:
    """Return estimated sweat loss in milliliters from known or fallback FIT fields."""
    if session_row is None:
        return None

    for key in ("estimated_sweat_loss", "total_sweat_loss", "sweat_loss", "unknown_178"):
        try:
            value = session_row.get(key)
        except Exception:
            value = None
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


def _convert_value(name: str, value):
    """Apply any necessary unit conversions to a raw field value."""
    if name in _SEMICIRCLE_FIELDS and value is not None:
        return round(value * _SEMICIRCLE_TO_DEG, 6)
    return value


def _localise_timestamp(ts):
    """Convert a timezone-aware (UTC) datetime to IST."""
    if ts is None:
        return None
    try:
        return ts.replace(tzinfo=_UTC).astimezone(_LOCAL_TZ)
    except Exception:
        return ts


def _needs_localisation(field_name: str, msg_name: str = None) -> bool:
    """Check if a field should be localized to IST."""
    # Always localize "timestamp" field
    if field_name == "timestamp":
        return True
    # Also localize "start_time" in set messages (from activity timeframe, not session end)
    if msg_name == "set" and field_name == "start_time":
        return True
    return False


class FitParser:
    """Parse every message in a .fit file and expose results as DataFrames."""

    def __init__(self, fit_path: str | Path, local_tz: str = "Asia/Kolkata"):
        self.fit_path = Path(fit_path)
        self._local_tz = pytz.timezone(local_tz)
        self._dfs: Dict[str, pd.DataFrame] = {}
        self._activity_type: str = "other"  # "running" | "strength" | "other"

        if not self.fit_path.exists():
            raise FileNotFoundError(f"FIT file not found: {self.fit_path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> Dict[str, pd.DataFrame]:
        """
        Parse the FIT file.

        Returns
        -------
        dict[str, pd.DataFrame]
            Keys are message-type names (e.g. "record", "lap", "session").
        """
        logger.info("Parsing %s", self.fit_path)
        fit = FitFile(str(self.fit_path))

        raw: Dict[str, list] = {}

        for msg in fit.get_messages():
            msg_name = msg.name

            row: dict = {}
            for field in msg:
                if field.value is None:
                    continue
                val = _convert_value(field.name, field.value)
                # Localize timestamp fields to IST
                if _needs_localisation(field.name, msg_name):
                    val = _localise_timestamp(val)
                row[field.name] = val

            if not row:
                continue

            raw.setdefault(msg_name, []).append(row)

        # Build DataFrames
        for msg_name, rows in raw.items():
            df = pd.DataFrame(rows)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
            self._dfs[msg_name] = df
            logger.info("  %-20s %d rows, %d cols", msg_name, len(df), len(df.columns))

        self._detect_activity_type()
        self._post_process()
        return self._dfs

    def save(self, output_dir: str | Path = "data/processed") -> Path:
        """
        Write each message-type DataFrame to its own CSV.

        Files are written to:
            <output_dir>/<fit_stem>/<message_type>.csv

        Returns the directory where files were saved.
        """
        if not self._dfs:
            self.parse()

        stem = self.fit_path.stem
        out_dir = Path(output_dir) / stem
        out_dir.mkdir(parents=True, exist_ok=True)

        for msg_name, df in self._dfs.items():
            csv_path = out_dir / f"{msg_name}.csv"
            df.to_csv(csv_path, index=False)
            logger.info("Saved %s → %s (%d rows)", msg_name, csv_path, len(df))

        print(f"[fit_parser] Activity type : {self._activity_type}")
        print(f"[fit_parser] Saved {len(self._dfs)} CSV(s) to: {out_dir}")
        return out_dir

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def activity_type(self) -> str:
        """Detected activity type: 'running', 'strength', or 'other'."""
        return self._activity_type

    @property
    def records(self) -> pd.DataFrame:
        """Per-second data stream (running activities)."""
        return self._dfs.get("record", pd.DataFrame())

    @property
    def laps(self) -> pd.DataFrame:
        return self._dfs.get("lap", pd.DataFrame())

    @property
    def session(self) -> pd.DataFrame:
        return self._dfs.get("session", pd.DataFrame())

    @property
    def sets_summary(self) -> pd.DataFrame:
        """Enriched sets table (strength activities only)."""
        return self._dfs.get("sets_summary", pd.DataFrame())

    @property
    def available_messages(self) -> list[str]:
        return list(self._dfs.keys())

    def get_session_summary(self) -> dict:
        """
        Extract key metrics from session message.

        Returns dict with:
            - total_calories: kcal burned
            - total_elapsed_time: seconds
            - total_timer_time: seconds (active time only)
            - avg_heart_rate: bpm
            - max_heart_rate: bpm
            - min_heart_rate: bpm
            - workout_date: session date (local timezone)
            - start_time: datetime
            - end_time: datetime
            - sport: activity type
            - sub_sport: activity subtype
        """
        session_df = self._dfs.get("session")
        if session_df is None or session_df.empty:
            return {}

        row = session_df.iloc[0]
        summary = {}

        # Duration in seconds
        if "total_elapsed_time" in session_df.columns:
            elapsed = row.get("total_elapsed_time")
            summary["total_elapsed_time_sec"] = float(elapsed) if elapsed else 0.0
            summary["total_elapsed_time_min"] = round(summary["total_elapsed_time_sec"] / 60, 1)

        if "total_timer_time" in session_df.columns:
            timer = row.get("total_timer_time")
            summary["total_timer_time_sec"] = float(timer) if timer else 0.0
            summary["total_timer_time_min"] = round(summary["total_timer_time_sec"] / 60, 1)

        # Calories
        if "total_calories" in session_df.columns:
            cals = row.get("total_calories")
            summary["total_calories"] = int(cals) if cals else 0
            
            # Estimate active vs resting calories
            elapsed = summary.get("total_elapsed_time_sec", 0)
            if elapsed > 0:
                resting_kcal = 1.2 * (elapsed / 60)
                active_kcal = summary["total_calories"] - resting_kcal
                summary["active_calories"] = int(max(0, active_kcal))
                summary["resting_calories"] = int(resting_kcal)
            else:
                summary["active_calories"] = summary["total_calories"]
                summary["resting_calories"] = 0

        # Heart rate stats
        if "avg_heart_rate" in session_df.columns:
            avg_hr = row.get("avg_heart_rate")
            summary["avg_heart_rate"] = int(avg_hr) if avg_hr else None

        if "max_heart_rate" in session_df.columns:
            max_hr = row.get("max_heart_rate")
            summary["max_heart_rate"] = int(max_hr) if max_hr else None

        # Min HR from records if not in session
        record_df = self._dfs.get("record")
        if record_df is not None and not record_df.empty and "heart_rate" in record_df.columns:
            min_hr = record_df["heart_rate"].dropna().min()
            summary["min_heart_rate"] = int(min_hr) if pd.notna(min_hr) else None
        else:
            summary["min_heart_rate"] = None

        # Activity metadata
        if "sport" in session_df.columns:
            summary["sport"] = row.get("sport")
        if "sub_sport" in session_df.columns:
            summary["sub_sport"] = row.get("sub_sport")

        sweat_loss_ml = _extract_estimated_sweat_loss_ml(row)
        if sweat_loss_ml is not None:
            summary["estimated_sweat_loss_ml"] = round(sweat_loss_ml, 1)
            summary["estimated_sweat_loss_l"] = round(sweat_loss_ml / 1000.0, 3)

        # Session window (prefer end timestamp + elapsed duration)
        end_time = row.get("timestamp") if "timestamp" in session_df.columns else None
        elapsed_sec = summary.get("total_elapsed_time_sec", 0.0)
        start_time = None

        if pd.notna(end_time):
            summary["end_time"] = end_time
            if elapsed_sec and elapsed_sec > 0:
                start_time = pd.Timestamp(end_time) - pd.to_timedelta(elapsed_sec, unit="s")

        # Fallback when end timestamp is missing or elapsed is unavailable
        if start_time is None and "start_time" in session_df.columns:
            start_val = row.get("start_time")
            if pd.notna(start_val):
                start_time = start_val

        if start_time is not None:
            summary["start_time"] = start_time

        date_source = summary.get("start_time") or summary.get("end_time")
        if date_source is not None:
            summary["workout_date"] = pd.Timestamp(date_source).date()

        return summary

    def get_exercise_summary(self) -> pd.DataFrame:
        """
        Extract metrics per exercise (strength activities only).

        Returns DataFrame with columns:
            - exercise_label: exercise name
            - sets_count: number of active sets
            - total_duration_s: sum of set durations
            - total_repetitions: sum of reps across sets
            - avg_weight_kg: average weight used
            - avg_heart_rate: HR during exercise window
            - min_heart_rate: min HR during exercise
            - max_heart_rate: max HR during exercise
            - calories: estimated calories burned during exercise

        For each exercise, calculates HR stats from record data by matching
        timestamps with the exercise set timeframes.
        """
        sets_df = self._dfs.get("sets_summary")
        if sets_df is None or sets_df.empty:
            return pd.DataFrame()

        record_df = self._dfs.get("record")
        session_df = self._dfs.get("session")

        # Build per-set end time so exercise HR window covers full set durations.
        sets_for_hr = sets_df.copy()
        if "start_time" in sets_for_hr.columns and "duration_s" in sets_for_hr.columns:
            start_ts = pd.to_datetime(sets_for_hr["start_time"], errors="coerce")
            dur_td = pd.to_timedelta(pd.to_numeric(sets_for_hr["duration_s"], errors="coerce").fillna(0), unit="s")
            sets_for_hr["end_time"] = start_ts + dur_td
        else:
            sets_for_hr["end_time"] = pd.NaT

        # Some devices/exports omit optional strength fields.
        # Ensure all downstream aggregation columns exist.
        if "set_type" not in sets_for_hr.columns:
            sets_for_hr["set_type"] = "active"
        if "exercise_label" not in sets_for_hr.columns:
            if "exercise_name" in sets_for_hr.columns:
                sets_for_hr["exercise_label"] = sets_for_hr["exercise_name"]
            else:
                sets_for_hr["exercise_label"] = "Unknown"
        sets_for_hr["exercise_label"] = sets_for_hr["exercise_label"].fillna("Unknown").astype(str)
        if "duration_s" not in sets_for_hr.columns:
            sets_for_hr["duration_s"] = 0.0
        if "repetitions" not in sets_for_hr.columns:
            sets_for_hr["repetitions"] = 0
        if "weight_kg" not in sets_for_hr.columns:
            sets_for_hr["weight_kg"] = pd.NA
        if "start_time" not in sets_for_hr.columns:
            sets_for_hr["start_time"] = pd.NaT

        # Get total session calories and duration for estimation
        total_calories = 0
        total_duration = 0
        active_calories = 0
        if session_df is not None and not session_df.empty:
            cals = session_df.get("total_calories", pd.Series([0])).iloc[0]
            total_calories = float(cals) if pd.notna(cals) else 0
            dur = session_df.get("total_elapsed_time", pd.Series([0])).iloc[0]
            total_duration = float(dur) if pd.notna(dur) else 1  # avoid division by zero
            
            # Estimate resting metabolic rate: ~1.2 kcal/min for average person
            resting_kcal = 1.2 * (total_duration / 60)
            active_calories = max(0, total_calories - resting_kcal)

        # Group by exercise
        ex_groups = sets_for_hr.groupby("exercise_label", as_index=False).agg({
            "set_type": "count",  # number of sets
            "duration_s": "sum",
            "repetitions": "sum",
            "weight_kg": "mean",
            "start_time": "min",
            "end_time": "max",  # true time range for this exercise
        })

        # Flatten column names
        ex_groups.columns = [
            "exercise_label", "sets_count", "total_duration_s", "total_repetitions",
            "avg_weight_kg", "start_time_min", "end_time_max"
        ]

        # Compute HR stats per exercise by collecting samples from EACH individual set
        # (not a single wide window). This avoids including HR from other exercises
        # performed between rounds in circuit/repeating workouts.
        hr_stats = []
        cals_stats = []

        def _localize(ts):
            t = pd.Timestamp(ts)
            return t.tz_localize("Asia/Kolkata") if t.tz is None else t

        if record_df is not None and not record_df.empty and "heart_rate" in record_df.columns:
            rec_ts = record_df["timestamp"]

            for _, ex_row in ex_groups.iterrows():
                label = ex_row["exercise_label"]

                # Get all individual sets for this exercise
                ex_sets = sets_for_hr[sets_for_hr["exercise_label"] == label]

                # Collect HR from each set's own narrow window
                all_hr = []
                for _, s in ex_sets.iterrows():
                    try:
                        t_start = _localize(s["start_time"]) if pd.notna(s["start_time"]) else None
                        t_end   = _localize(s["end_time"])   if pd.notna(s["end_time"])   else None
                        if t_start is None or t_end is None:
                            continue
                        mask = (rec_ts >= t_start) & (rec_ts <= t_end)
                        hr_slice = record_df.loc[mask, "heart_rate"].dropna()
                        all_hr.extend(hr_slice.tolist())
                    except Exception as e:
                        logger.warning("Error collecting HR for set of %s: %s", label, e)

                if all_hr:
                    hr_stats.append({
                        "exercise_label": label,
                        "avg_heart_rate": int(round(sum(all_hr) / len(all_hr))),
                        "min_heart_rate": int(min(all_hr)),
                        "max_heart_rate": int(max(all_hr)),
                    })
                else:
                    hr_stats.append({
                        "exercise_label": label,
                        "avg_heart_rate": None,
                        "min_heart_rate": None,
                        "max_heart_rate": None,
                    })
        else:
            # No HR data available
            hr_stats = [{"exercise_label": label, "avg_heart_rate": None,
                         "min_heart_rate": None, "max_heart_rate": None}
                        for label in ex_groups["exercise_label"]]

        # Estimate calories per exercise (proportional to duration)
        if total_duration > 0:
            for ex_dur in ex_groups["total_duration_s"]:
                estimated_cals = round((active_calories * ex_dur) / total_duration, 1)
                cals_stats.append({"calories": estimated_cals})
        else:
            cals_stats = [{"calories": 0.0} for _ in ex_groups["total_duration_s"]]

        hr_df = pd.DataFrame(hr_stats)
        cals_df = pd.DataFrame(cals_stats)

        # Merge HR and calories stats back
        result = ex_groups.merge(hr_df, on="exercise_label")
        result = pd.concat([result, cals_df], axis=1)

        # Order exercises by when they first started (timeline order)
        result = result.sort_values(["start_time_min", "exercise_label"], ascending=[True, True])

        result.drop(columns=["start_time_min", "end_time_max"], inplace=True)

        # Clean up columns
        result["total_repetitions"] = result["total_repetitions"].fillna(0).astype(int)
        result["avg_weight_kg"] = result["avg_weight_kg"].round(2)
        result["total_duration_s"] = result["total_duration_s"].round(1)

        return result.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Activity type detection
    # ------------------------------------------------------------------

    def _detect_activity_type(self):
        """Infer activity type from session or sport messages."""
        sport_val = ""
        sub_sport_val = ""

        # Try session message first (most reliable)
        session_df = self._dfs.get("session")
        if session_df is not None and not session_df.empty:
            sport_val = str(session_df.get("sport", pd.Series([""])).iloc[0]).lower()
            sub_sport_val = str(session_df.get("sub_sport", pd.Series([""])).iloc[0]).lower()

        # Fall back to sport message
        if not sport_val:
            sport_df = self._dfs.get("sport")
            if sport_df is not None and not sport_df.empty:
                sport_val = str(sport_df.get("sport", pd.Series([""])).iloc[0]).lower()
                sub_sport_val = str(sport_df.get("sub_sport", pd.Series([""])).iloc[0]).lower()

        if sport_val == "running" or sub_sport_val in _RUNNING_SPORTS:
            self._activity_type = "running"
        elif sub_sport_val in _STRENGTH_SPORTS or sport_val == "training":
            self._activity_type = "strength"
        else:
            self._activity_type = "other"

        logger.info("Detected activity type: %s (sport=%s, sub_sport=%s)",
                    self._activity_type, sport_val, sub_sport_val)

    # ------------------------------------------------------------------
    # Post-processing (dispatches by activity type)
    # ------------------------------------------------------------------

    def _post_process(self):
        if self._activity_type == "running":
            self._post_process_running()
        elif self._activity_type == "strength":
            self._post_process_strength()
        else:
            # Still enrich records if present (e.g. cycling)
            self._post_process_running()

    def _post_process_running(self):
        """Enrich the record DataFrame with derived running metrics."""
        df = self._dfs.get("record")
        if df is None or df.empty:
            return

        # Speed: prefer enhanced_speed
        if "enhanced_speed" in df.columns and "speed" not in df.columns:
            df.rename(columns={"enhanced_speed": "speed"}, inplace=True)
        elif "enhanced_speed" in df.columns:
            df["speed"] = df["enhanced_speed"].combine_first(df["speed"])
            df.drop(columns=["enhanced_speed"], inplace=True)

        # Altitude: prefer enhanced_altitude
        if "enhanced_altitude" in df.columns and "altitude" not in df.columns:
            df.rename(columns={"enhanced_altitude": "altitude"}, inplace=True)
        elif "enhanced_altitude" in df.columns:
            df["altitude"] = df["enhanced_altitude"].combine_first(df.get("altitude"))
            df.drop(columns=["enhanced_altitude"], errors="ignore", inplace=True)

        # Pace (min/km) from speed (m/s)
        if "speed" in df.columns:
            df["pace_min_per_km"] = df["speed"].apply(
                lambda s: round(1000 / (s * 60), 2) if s and s > 0 else None
            )

        # Stride length (m) from step_length (mm)
        if "step_length" in df.columns:
            df["stride_length_m"] = df["step_length"] / 1000.0

        self._dfs["record"] = df

    def _post_process_strength(self):
        """
        Build a clean sets_summary DataFrame by joining set messages with
        exercise_title messages.

        set.wkt_step_index  ↔  exercise_title.message_index

        Output columns:
            timestamp, start_time, exercise_name, exercise_category,
            set_type, duration_s, repetitions, weight_kg
        """
        sets_df = self._dfs.get("set")
        titles_df = self._dfs.get("exercise_title")
        steps_df = self._dfs.get("workout_step")

        if sets_df is None or sets_df.empty:
            logger.warning("No 'set' messages found – cannot build sets_summary.")
            return

        sets = sets_df.copy()

        # ---- decode category tuple → first integer ----
        def _first_int(val):
            """Extract the first element from a tuple-like string e.g. '(28, 28, 28)' → 28."""
            try:
                s = str(val).strip("()")
                return int(s.split(",")[0].strip())
            except Exception:
                return None

        if "category" in sets.columns:
            sets["category_code"] = sets["category"].apply(_first_int)
            sets.drop(columns=["category"], inplace=True)

        if "category_subtype" in sets.columns:
            sets["category_subtype_code"] = sets["category_subtype"].apply(_first_int)
            sets.drop(columns=["category_subtype"], inplace=True)

        # ---- join set -> workout_step on message_index (most reliable mapping) ----
        if steps_df is not None and not steps_df.empty and "message_index" in sets.columns:
            step_cols = [
                "message_index", "exercise_name", "exercise_category",
                "duration_reps", "duration_time", "exercise_weight",
            ]
            available_step_cols = [c for c in step_cols if c in steps_df.columns]
            steps = steps_df[available_step_cols].copy()

            sets["message_index"] = pd.to_numeric(sets["message_index"], errors="coerce")
            steps["message_index"] = pd.to_numeric(steps["message_index"], errors="coerce")
            sets = sets.merge(steps, on="message_index", how="left", suffixes=("", "_step"))

            # Fallback for repeated blocks: match set.wkt_step_index -> workout_step.message_index
            # when direct set.message_index mapping has no exercise metadata.
            if "wkt_step_index" in sets.columns:
                step_lookup = steps.rename(columns={"message_index": "wkt_step_index"}).copy()
                step_lookup["wkt_step_index"] = pd.to_numeric(step_lookup["wkt_step_index"], errors="coerce")
                sets["wkt_step_index"] = pd.to_numeric(sets["wkt_step_index"], errors="coerce")
                sets = sets.merge(step_lookup, on="wkt_step_index", how="left", suffixes=("", "_wkt"))

                for col in ["exercise_name", "exercise_category", "duration_reps", "duration_time", "exercise_weight"]:
                    wkt_col = f"{col}_wkt"
                    if col in sets.columns and wkt_col in sets.columns:
                        sets[col] = sets[col].combine_first(sets[wkt_col])

                drop_cols = [c for c in sets.columns if c.endswith("_wkt")]
                if drop_cols:
                    sets.drop(columns=drop_cols, inplace=True)

        # ---- map workout_step.exercise_name code -> human-readable label ----
        if titles_df is not None and not titles_df.empty and "exercise_name" in sets.columns:
            titles = titles_df[["exercise_name", "wkt_step_name", "exercise_category"]].copy()
            titles["exercise_name"] = pd.to_numeric(titles["exercise_name"], errors="coerce")
            sets["exercise_name"] = pd.to_numeric(sets["exercise_name"], errors="coerce")
            sets = sets.merge(
                titles,
                on="exercise_name",
                how="left",
                suffixes=("", "_title"),
            )

        # Choose a final human-readable exercise label
        if "wkt_step_name" in sets.columns:
            sets["exercise_label"] = sets["wkt_step_name"]
        elif "exercise_label" not in sets.columns:
            sets["exercise_label"] = None

        if "exercise_label" in sets.columns and "exercise_category" in sets.columns:
            missing = sets["exercise_label"].isna()
            cat = sets["exercise_category"]
            has_cat = missing & cat.notna()
            sets.loc[has_cat, "exercise_label"] = cat[has_cat].astype(str).str.replace("_", " ").str.title()

            still_missing = sets["exercise_label"].isna()
            if "wkt_step_index" in sets.columns:
                idx_text = sets.loc[still_missing, "wkt_step_index"].fillna(-1).astype(int).astype(str)
                sets.loc[still_missing, "exercise_label"] = "Unknown Step " + idx_text
            else:
                sets.loc[still_missing, "exercise_label"] = "Unknown Exercise"

        # ---- tidy up column names ----
        rename_map = {
            "duration": "duration_s",
            "weight": "weight_kg",
        }
        sets.rename(columns={k: v for k, v in rename_map.items() if k in sets.columns},
                    inplace=True)

        # ---- keep only active sets for the summary ----
        active_sets = sets[sets.get("set_type", pd.Series(["active"])) == "active"].copy() \
            if "set_type" in sets.columns else sets.copy()

        # Add rest duration after each active set (next set row if it is rest)
        if "duration_s" in sets.columns and "set_type" in sets.columns:
            sets_sorted = sets.sort_values("message_index").reset_index(drop=True)
            next_type = sets_sorted["set_type"].shift(-1)
            next_duration = pd.to_numeric(sets_sorted["duration_s"].shift(-1), errors="coerce").fillna(0)
            sets_sorted["rest_s"] = next_duration.where(next_type == "rest", 0.0)
            active_rest = sets_sorted[sets_sorted["set_type"] == "active"][["message_index", "rest_s"]]
            active_sets = active_sets.merge(active_rest, on="message_index", how="left")
            active_sets["rest_s"] = active_sets["rest_s"].fillna(0).round(3)

        # ---- reorder columns for readability ----
        preferred_order = [
            "timestamp", "start_time", "exercise_label", "exercise_category",
            "exercise_name", "set_type", "duration_s", "rest_s", "repetitions", "weight_kg",
            "wkt_step_index", "category_code", "category_subtype_code",
        ]
        ordered_cols = [c for c in preferred_order if c in active_sets.columns] + \
                       [c for c in active_sets.columns if c not in preferred_order]
        active_sets = active_sets[ordered_cols]

        self._dfs["sets_summary"] = active_sets
        logger.info("  %-20s %d rows, %d cols", "sets_summary",
                    len(active_sets), len(active_sets.columns))


# ---------------------------------------------------------------------------
# CLI entry point:  uv run python -m src.fit_parser path/to/file.fit [out_dir]
# ---------------------------------------------------------------------------

def _cli():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.fit_parser <path/to/file.fit> [output_dir]")
        sys.exit(1)

    fit_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data/processed"

    parser = FitParser(fit_path)
    dfs = parser.parse()
    saved_to = parser.save(output_dir=out_dir)

    print(f"\nMessage types parsed:")
    for name, df in dfs.items():
        print(f"  {name:<20} {len(df):>5} rows  {len(df.columns):>3} cols")
    print(f"\nAll CSVs saved to: {saved_to}")


if __name__ == "__main__":
    _cli()
