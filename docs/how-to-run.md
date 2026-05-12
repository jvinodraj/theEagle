# How to Run theEagle

This is the standard runbook for parsing Garmin FIT files and generating separated reports for easy, interval, and strength workflows.

## 1. Prerequisites

- Python 3.13+
- uv

Check:

```powershell
python --version
uv --version
```

## 2. Setup

From repository root:

```powershell
uv sync
uv run python main.py init
```

The init command prepares category folders under data/activities.

## 3. Standard FIT Input Folders

Use these folders for new files:

- data/activities/easy/raw
- data/activities/interval/raw
- data/activities/strength/raw
- data/activities/general/raw

Legacy fallbacks still supported:

- data/easy_runs (easy)
- data/raw (general)

## 4. Parse FIT Files

Parse all categories:

```powershell
uv run python main.py parse --category all
```

Parse one category:

```powershell
uv run python main.py parse --category easy
uv run python main.py parse --category interval
uv run python main.py parse --category strength
uv run python main.py parse --category general
```

Parse one file:

```powershell
uv run python main.py parse --file data/activities/interval/raw/my_workout.fit --category interval
```

Parsed CSV output format:

```text
data/activities/<category>/processed/<fit_file_stem>/
```

## 5. Generate Reports (Separated by Workout Type)

### 5.1 Easy Runs

Command:

```powershell
uv run python main.py easy-score
```

Default output folder:

- reports/easy

Primary files:

- reports/easy/hr_improvement_analysis.csv
- reports/easy/hr_timeline_report.md
- reports/easy/hr_improvement_plot.png

### 5.2 Interval / Tempo / Threshold / Speed

Keep interval FIT files in:

- data/activities/interval/raw

Command:

```powershell
uv run python main.py interval-report
```

Optional custom interval input folder:

```powershell
uv run python main.py interval-report --interval-dir data/activities/interval/raw
```

Default output folder:

- reports/interval

Primary files:

- reports/interval/interval_workouts_dataset.csv
- reports/interval/interval_level_dataset.csv
- reports/interval/interval_longitudinal_tracking.csv
- reports/interval/interval_adaptation_report.md

### 5.3 Strength

Command:

```powershell
uv run python main.py strength-report
```

Default output folder:

- reports/strength

Primary files:

- reports/strength/strength_endurance_sessions.csv
- reports/strength/strength_weekly_summary.csv
- reports/strength/strength_recovery_interaction.csv
- reports/strength/strength_running_transfer_observations.csv
- reports/strength/strength_endurance_integration_report.md

## 6. Recommended Daily Workflow

1. Export FIT files from Garmin Connect.
2. Drop files into the correct category raw folder.
3. Run parse for that category.
4. Run the matching report command.
5. Review the latest CSV + markdown output in the category report folder.

## 7. Command Reference

```powershell
# Initialize folders
uv run python main.py init

# Parse
uv run python main.py parse --category all

# Reports
uv run python main.py easy-score
uv run python main.py interval-report
uv run python main.py strength-report
```

## 8. Troubleshooting

### No FIT files found

- Confirm files are in data/activities/<category>/raw.
- Confirm extension is .fit.

### Command runs but report is missing

- Check the category-specific report folder:
  - reports/easy
  - reports/interval
  - reports/strength

### Missing metrics in reports

- Some Garmin fields are device-dependent and may be absent in certain FIT exports.
- Garmin estimates (for example training effect or threshold settings) are not direct lab measurements.

## 9. Operational Notes

- main.py is the unified CLI entry point.
- Use standardized category folders for consistency and easier automation.
- Keep easy, interval, and strength reports separate to avoid mixing interpretations.
