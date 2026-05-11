# How to Run theEagle

This guide is the operational runbook for running the project locally.
It is command-first, validated against the current CLI, and focused on daily use.

## 1. Prerequisites

- OS: Windows, macOS, or Linux
- Python: 3.13+
- Tooling: uv

Check versions:

```powershell
uv --version
python --version
```

## 2. Initial Setup

From the repository root:

```powershell
uv sync
```

What this does:

- Reads dependencies from pyproject.toml
- Creates/updates .venv
- Installs pinned packages

Create the standardized data layout (recommended once per fresh clone):

```powershell
uv run python main.py init
```

This ensures these directories exist:

```text
data/activities/easy/raw
data/activities/easy/processed
data/activities/strength/raw
data/activities/strength/processed
data/activities/general/raw
data/activities/general/processed
```

## 3. Quick Start

If your goal is easy-run HR tracking only:

1. Place easy-run FIT files in data/activities/easy/raw.
2. Run:

```powershell
uv run python main.py easy-score
```

3. Review outputs in reports:

- reports/hr_improvement_plot.png
- reports/hr_timeline_report.md
- reports/hr_improvement_analysis.csv

If your goal is parsing all activity categories and then scoring easy runs:

```powershell
uv run python main.py run-all
```

## 4. FIT Parsing Workflows

The parser command is parse.
Running main.py without a subcommand only shows help.

### 4.1 Parse All Discovered Categories

```powershell
uv run python main.py parse --category all
```

Category discovery includes:

- Any folder under data/activities that contains a raw subfolder
- Legacy fallback categories when legacy paths exist

### 4.2 Parse One Category

```powershell
uv run python main.py parse --category easy
uv run python main.py parse --category strength
uv run python main.py parse --category general
```

### 4.3 Parse One File

```powershell
uv run python main.py parse --file data/activities/easy/raw/my_run.fit --category easy
```

Notes:

- If you omit --category for a single file, output is written under the general category.
- The file can be outside category folders when passed via --file.

### 4.4 Parser Output Layout

For each FIT file, output is saved under:

```text
data/activities/<category>/processed/<fit_file_stem>/
```

Typical files:

- record.csv
- lap.csv
- session.csv
- event.csv
- device_info.csv
- other message-type CSVs if present

For strength sessions, sets_summary.csv is also generated when set data exists.

### 4.5 Module CLI (Direct Parser Invocation)

You can invoke the parser module directly:

```powershell
uv run python -m src.fit_parser path/to/file.fit
uv run python -m src.fit_parser path/to/file.fit data/activities/general/processed
```

## 5. Easy-Run HR Tracker Workflow

### 5.1 Input Folder

Preferred folder:

```text
data/activities/easy/raw
```

### 5.2 Run the Tracker

```powershell
uv run python main.py easy-score
```

Optional custom reports directory:

```powershell
uv run python main.py easy-score --report-dir reports
```

Alternative script entrypoint:

```powershell
uv run easy-run-hr-report
```

### 5.3 What the Command Does

The easy-score workflow:

1. Reads all .fit files from the resolved easy-run folder.
2. Parses each FIT file.
3. Computes steady-state and trend metrics.
4. Builds run-level and weekly summaries.
5. Writes chart, markdown report, and CSV outputs.

### 5.4 Tracker Outputs

- reports/hr_improvement_plot.png: 4-panel trend visualization
- reports/hr_timeline_report.md: detailed run-by-run interpretation
- reports/hr_improvement_analysis.csv: full tabular metrics

## 6. Daily Operating Procedure

After each easy run:

1. Export Original FIT from Garmin Connect.
2. Save it to data/activities/easy/raw.
3. Run:

```powershell
uv run python main.py easy-score
```

4. Check whether latest row and plot point were added in reports outputs.

## 7. Standardized vs Legacy Paths

Preferred standardized layout:

```text
data/activities/<category>/raw
data/activities/<category>/processed
```

Legacy compatibility still exists:

- Easy category fallback: data/easy_runs
- General category fallback: data/raw

Resolution behavior:

- Standardized folders are preferred when they contain FIT files.
- Legacy folders are used automatically when standardized folders are empty or missing.

Recommendation: keep new files in standardized data/activities paths.

## 8. Troubleshooting

### No categories found when parsing all

Run:

```powershell
uv run python main.py init
```

Then place .fit files under category raw folders.

### No .fit files found for a category

Place FIT files in:

```text
data/activities/<category>/raw
```

Then re-run parse or run-all.

### easy-score fails with "No FIT files found"

- Ensure files are in data/activities/easy/raw (preferred)
- Or use legacy data/easy_runs
- Confirm file extension is .fit

### easy-score fails with "No HR data could be extracted"

- Verify heart-rate data exists in the FIT export
- Re-export the original FIT file from Garmin Connect

### main.py with no arguments does nothing

Expected behavior. It prints CLI help.
Use one of: init, parse, easy-score, run-all.

## 9. Dependency Management

Add a package:

```powershell
uv add <package>
```

Remove a package:

```powershell
uv remove <package>
```

Re-sync after manual edits:

```powershell
uv sync
```

## 10. Programmatic Use

Example using FitParser in Python:

```python
from src.fit_parser import FitParser

parser = FitParser("data/activities/easy/raw/my_run.fit")
frames = parser.parse()
parser.save("data/activities/easy/processed")

print(parser.activity_type)
print(parser.available_messages)

records = parser.records
laps = parser.laps
session = parser.session
```

## 11. Project Map (Operational)

```text
theEagle/
  main.py                         # Unified CLI: init, parse, easy-score, run-all
  pyproject.toml                  # Dependencies and script entrypoints
  src/
    fit_parser.py                 # FIT parsing engine
    hr_improvement_tracker.py     # Easy-run scoring and report generation
  data/
    activities/
      <category>/
        raw/                      # Input FIT files
        processed/                # Parsed CSV outputs
    easy_runs/                    # Legacy easy-run input folder
    raw/                          # Legacy general input folder
  reports/                        # Generated tracker outputs
  docs/
    how-to-run.md                 # This runbook
```

## 12. Related References

For deeper background and analysis context, see:

- docs/Efficiency-Factor.md
- docs/HRDI-Analysis.md
- docs/decay-delay-calculation.md
- docs/running_analysis.md

Keep this file focused on execution steps and operational checks.
