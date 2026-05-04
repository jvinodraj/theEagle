# theEagle
Python tools for analysing Garmin FIT files — aimed at half-marathon runners training with a coach.

> Full how-to guide: [`docs/how-to-run.md`](docs/how-to-run.md)

---

## Tools

### Easy Run HR Tracker ⭐

Tracks heart-rate efficiency across easy training runs using internationally
recognised metrics (**Efficiency Factor** and **Aerobic Decoupling %**).
Because these are rate metrics they are valid for comparing runs of different
distances (e.g. 5 km Thursday easy vs 10 km Saturday easy).

```powershell
# drop FIT files into data/easy_runs/, then:
uv run easy-run-hr-report
```

Outputs:
- `reports/hr_improvement_plot.png` — four-panel chart
- `reports/hr_timeline_report.md` — run-by-run table with plain-English notes
- `reports/hr_improvement_analysis.csv` — full metrics spreadsheet

Key metrics explained in [`docs/how-to-run.md §7`](docs/how-to-run.md#7-easy-run-hr-tracker).

---

### FIT File Parser

Parses any Garmin `.fit` file into structured CSVs (one per message type).

```powershell
uv run python main.py          # batch-parse all files in data/raw/
uv run python main.py my.fit   # single file
```

Output folder: `data/processed/<activity_name>/` — contains `record.csv`,
`session.csv`, `lap.csv`, and one CSV per additional message type.

---

### Other Analysis Scripts

| Script | Purpose |
|--------|---------|
| `HRbyPower.py` | Scatter: heart rate vs power coloured by HR zone |
| `BoxPlot-HRbyPower.py` | Box plot: power distribution per HR zone |
| `correlation-analysis.py` | Correlation matrix across all running metrics |
| `running-analysis.py` | General session analysis and pace breakdown |
| `track-power-zone.py` | Time-in-zone breakdown for power |
| `ftp-test.py` | FTP estimation from a test effort |
| `predict-efficiency.py` | Running economy regression model |

---

## Quick Start

```powershell
# 1. install uv (once)
winget install astral-sh.uv        # Windows
# brew install uv                  # macOS

# 2. clone and set up
git clone <repo-url>
cd theEagle
uv sync

# 3. run the HR tracker
#    (drop your FIT files into data/easy_runs/ first)
uv run easy-run-hr-report
```

---

## Project Structure

```
theEagle/
├── data/
│   ├── raw/              # raw .fit files for batch parsing
│   ├── easy_runs/        # easy-run .fit files for HR tracker
│   └── processed/        # parsed CSVs
├── docs/                 # how-to guides and metric explanations
├── reports/              # generated reports and charts
├── src/
│   ├── fit_parser.py             # FIT → DataFrame parser
│   ├── hr_improvement_tracker.py # Easy Run HR Tracker (main logic)
│   ├── feature_engineering.py
│   ├── eda.py
│   └── model.py
├── main.py               # batch parse entry point
└── pyproject.toml        # dependencies and script entrypoints
```

## Questions?
Open an issue or reach out at [vinodraj.j@gmail.com].

