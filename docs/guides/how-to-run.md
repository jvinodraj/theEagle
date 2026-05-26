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

Before placing files, follow: [How to Download and Place FIT Files](download-fit-files.md)

Use these folders for new files:

- data/activities/easy/raw
- data/activities/interval/raw
- data/activities/strength/raw
- data/activities/general/raw

Legacy fallbacks still supported:

- data/easy_runs (easy)
- data/raw (general)

## 4. Parse FIT Files

Optional: download directly from Garmin Connect first.

Set credentials:

```powershell
$env:GARMIN_EMAIL="you@example.com"
$env:GARMIN_PASSWORD="your_password"
```

Download one activity by Garmin ID:

```powershell
uv run python main.py download-fit --category easy --activity-id 123456789
```

Download recent activities (bulk):

```powershell
uv run python main.py download-fit --category interval --days 14 --limit 30
```

Advanced options:

```powershell
uv run python main.py download-fit --category strength --days 21 --limit 50 --overwrite --force-login
```

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
uv run python main.py easy-report
```

Default output folder:

- reports/easy

Primary files:

- reports/easy/hr_improvement_analysis.csv
- reports/easy/hr_timeline_report.md
- reports/easy/hr_improvement_plot.png

### 5.1.1 Easy Run EDA Notebook (Prerequisites + Run)

Notebook path:

- notebooks/easy_run_eda.ipynb

Prerequisites:

- Python 3.13+
- uv
- Dependencies synced with dev tools:

```powershell
uv sync --dev
```

- Easy-run report CSV generated (the notebook reads one of these):
  - reports/hr_improvement_analysis.csv
  - reports/easy/hr_improvement_analysis.csv

Generate the required CSV:

```powershell
uv run python main.py easy-report
```

Run the notebook:

1. Open notebooks/easy_run_eda.ipynb in VS Code.
2. Select the project kernel (`theeagle` / `.venv`).
3. Run all cells top-to-bottom.

If the notebook raises file-not-found for CSV input, rerun:

```powershell
uv run python main.py easy-report
```

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

1. Download FIT files using [How to Download and Place FIT Files](download-fit-files.md).
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

# Download from Garmin Connect
uv run python main.py download-fit --category easy --days 14 --limit 20

# Reports
uv run python main.py easy-report
uv run python main.py interval-report
uv run python main.py strength-report
```

## 8. Troubleshooting

### No FIT files found

Use Garmin Connect download command first:

```powershell
uv run python main.py download-fit --category easy --days 14 --limit 20
```

Then parse:

```powershell
uv run python main.py parse --category easy
```

### UnicodeEncodeError on Windows

If you see a `charmap` codec error when running `easy-report`, set encoding explicitly:

```powershell
$env:PYTHONIOENCODING="utf-8"; uv run python main.py easy-report
```


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

