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
# drop FIT files into data/activities/easy/raw/, then:
uv run python main.py easy-score
```

Outputs:
- `reports/hr_improvement_plot.png` — four-panel chart
- `reports/hr_timeline_report.md` — detailed run-by-run markdown analysis
- `reports/hr_improvement_analysis.csv` — full metrics spreadsheet

Operational details are documented in [`docs/how-to-run.md`](docs/how-to-run.md).

---

### FIT File Parser

Parses any Garmin `.fit` file into structured CSVs (one per message type).

```powershell
uv run python main.py parse --category all
uv run python main.py parse --category easy
uv run python main.py parse --file data/activities/easy/raw/my_run.fit --category easy
```

Output folder: `data/activities/<category>/processed/<activity_name>/` — contains `record.csv`,
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
uv run python main.py init

# 3. run the HR tracker
#    (drop your FIT files into data/activities/easy/raw/ first)
uv run python main.py easy-score

# optional: parse all categories first, then run easy-score
uv run python main.py run-all
```

---

## Project Structure

```
theEagle/
├── data/
│   ├── activities/
│   │   └── <category>/
│   │       ├── raw/      # input FIT files
│   │       └── processed/ # parsed CSVs
│   ├── raw/              # legacy general input folder
│   └── easy_runs/        # legacy easy-run input folder
├── docs/                 # how-to guides and metric explanations
├── reports/              # generated reports and charts
├── src/
│   ├── fit_parser.py             # FIT → DataFrame parser
│   ├── hr_improvement_tracker.py # Easy Run HR Tracker (main logic)
│   └── model.py
├── main.py               # unified CLI: init, parse, easy-score, run-all
└── pyproject.toml        # dependencies and script entrypoints
```

## Questions?
Open an issue or reach out at [vinodraj.j@gmail.com].

