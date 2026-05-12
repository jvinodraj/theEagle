# theEagle

Python tools for Garmin FIT analysis for half-marathon training, with separate workflows for easy runs, interval/high-intensity sessions, and strength sessions.

Full operational guide: [docs/how-to-run.md](docs/how-to-run.md)

## What This Project Does

- Parse Garmin FIT files into structured CSV outputs.
- Analyze easy-run aerobic efficiency and decoupling trends.
- Analyze interval/tempo/threshold/speed adaptation trends.
- Analyze strength-endurance interaction and recovery cost.
- Keep reports separated by workout type.

## Standard Data Folders

Place FIT files into:

- data/activities/easy/raw
- data/activities/interval/raw
- data/activities/strength/raw
- data/activities/general/raw

Parsed outputs go to:

- data/activities/<category>/processed/<fit_file_stem>/

## Report Folders (Separated)

- Easy reports: reports/easy
- Interval reports: reports/interval
- Strength reports: reports/strength

## CLI Commands

Initialize standard folders:

```powershell
uv run python main.py init
```

Parse FIT files:

```powershell
uv run python main.py parse --category all
uv run python main.py parse --category easy
uv run python main.py parse --category interval
uv run python main.py parse --category strength
uv run python main.py parse --file data/activities/easy/raw/my_run.fit --category easy
```

Run separated reports:

```powershell
uv run python main.py easy-score
uv run python main.py interval-report
uv run python main.py strength-report
```

## Quick Start

```powershell
# 1) install dependencies
uv sync

# 2) create folders
uv run python main.py init

# 3) add FIT files to raw folders by category

# 4) parse files
uv run python main.py parse --category all

# 5) generate reports
uv run python main.py easy-score
uv run python main.py interval-report
uv run python main.py strength-report
```

## Project Layout

```text
theEagle/
	data/
		activities/
			easy/raw
			interval/raw
			strength/raw
			general/raw
			<category>/processed
	reports/
		easy/
		interval/
		strength/
	docs/
		how-to-run.md
	src/
		fit_parser.py
		hr_improvement_tracker.py
	main.py
	interval_high_intensity_analysis.py
	strength_endurance_integration.py
```

## Notes

- Legacy fallback folders still work (data/easy_runs and data/raw), but standardized paths above are recommended.
- Garmin-derived values (for example training effect and threshold settings) should be interpreted as device estimates, not laboratory measurements.

