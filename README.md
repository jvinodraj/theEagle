# theEagle

Python tools for Garmin FIT analysis for half-marathon training, with separate workflows for easy runs, interval/high-intensity sessions, and strength sessions.

Full operational guide: [docs/guides/how-to-run.md](docs/guides/how-to-run.md)

Download and place FIT files: [docs/guides/download-fit-files.md](docs/guides/download-fit-files.md)

Documentation index: [docs/guides/docs-index.md](docs/guides/docs-index.md)

Project structure standard: [docs/guides/project-structure.md](docs/guides/project-structure.md)

Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

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
uv run python main.py easy-report
uv run python main.py interval-report
uv run python main.py strength-report
```

## Help

If you are unsure what to run, start with:

```powershell
uv run python main.py
```

That prints the built-in command help, including the most common workflows:

- `init` to create the standard folder layout
- `parse` to convert FIT files into CSV outputs
- `easy-report` to generate the easy-run HR scorecard and plot
	- `easy-score` remains available as a backward-compatible alias
- `interval-report` to analyze interval / tempo / threshold sessions
- `strength-report` to analyze strength-endurance sessions
- `run-all` to run the combined parse-and-report workflow

For a step-by-step walkthrough, see [docs/guides/how-to-run.md](docs/guides/how-to-run.md).

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
uv run python main.py easy-report
uv run python main.py interval-report
uv run python main.py strength-report
```

## Training Pyramid

Visualise your training load distribution across aerobic base, strength, and interval/threshold work:

```powershell
# All-time view
uv run python training_pyramid.py

# Last N weeks only
uv run python training_pyramid.py --weeks 4
```

Output saved to `reports/training_pyramid.png`.

![Training Pyramid](reports/training_pyramid.png)

Each band's height is proportional to actual training time, so the pyramid shape reflects your real load balance. The ideal pyramid has a wide aerobic base, a medium strength band, and a narrow interval top.

---

## Easy Run EDA Notebook

Notebook:

- notebooks/easy_run_eda.ipynb

Prerequisites:

```powershell
uv sync --dev
uv run python main.py easy-report
```

Then open the notebook in VS Code, select the project kernel, and run all cells.
Detailed runbook: [docs/guides/how-to-run.md](docs/guides/how-to-run.md)

## Project Layout

```text
theEagle/
	configs/
	data/
		activities/
			easy/raw
			interval/raw
			strength/raw
			general/raw
			<category>/processed
	notebooks/
	reports/
		easy/
		interval/
		strength/
	scripts/
	tests/
		unit/
		integration/
	docs/
		README.md
		guides/
		calculations/
		knowledge-base/
		plan/
		misc/
	src/
		fit_parser.py
		hr_improvement_tracker.py
	CONTRIBUTING.md
	pyproject.toml
	uv.lock
	main.py
	interval_high_intensity_analysis.py
	strength_endurance_integration.py
```

## Notes

- Legacy fallback folders still work (data/easy_runs and data/raw), but standardized paths above are recommended.
- Garmin-derived values (for example training effect and threshold settings) should be interpreted as device estimates, not laboratory measurements.
- This workflow has been fully tested only with Garmin Forerunner 255 FIT exports. Other devices may work but are not yet fully validated.
- Existing root-level analysis scripts are kept for compatibility. New scripts should be added under `scripts/`.


