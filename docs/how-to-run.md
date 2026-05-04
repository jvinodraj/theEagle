# How to Run theEagle

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`uv --version` to check)
- Python 3.13+ (uv manages this automatically)

---

## 1. Install Dependencies

Run once after cloning or pulling changes:

```powershell
uv sync
```

This reads `pyproject.toml`, creates a `.venv`, and installs all packages.

---

## 2. Parse FIT Files

### Batch mode — parse all files at once

1. Copy your Garmin `.fit` files into `data/raw/`
2. Run:

```powershell
uv run python main.py
```

Each file is parsed and its outputs are written to:

```
data/processed/<activity_name>/
    record.csv        # per-second stream: HR, power, cadence, speed, pace
    lap.csv           # lap summaries
    session.csv       # overall session summary
    device_info.csv   # device / sensor info
    event.csv         # start/stop/lap events
    <other>.csv       # any additional message types in the file
```

### Single file

```powershell
uv run python main.py data/raw/my_run.fit
```

Or use the module directly and specify a custom output directory:

```powershell
uv run python -m src.fit_parser data/raw/my_run.fit data/processed
```

---

## 3. Use the Parser in Your Own Scripts

```python
from src.fit_parser import FitParser

parser = FitParser("data/raw/my_run.fit")
dfs = parser.parse()          # returns dict[str, pd.DataFrame]
parser.save("data/processed") # writes all CSVs

# Access specific DataFrames directly
records = parser.records       # per-second stream
laps    = parser.laps
session = parser.session

print(parser.available_messages)  # list all message types found
```

---

## 4. Feature Engineering

After parsing, run feature engineering to add derived metrics:

```powershell
uv run python -m src.feature_engineering
```

Reads `data/processed/cleaned_fit_data.csv`, adds:
- `pace_min_per_km`
- `power_to_weight` (assumes 72 kg — edit `src/feature_engineering.py` to change)
- `cadence_to_speed`

Output: `data/processed/enhanced_fit_data.csv`

---

## 5. Exploratory Data Analysis

```powershell
uv run python -m src.eda
```

Generates time-series plots, correlation heatmap, and pairwise scatter plots from `data/processed/enhanced_fit_data.csv`.

---

## 6. Add / Remove Packages

```powershell
uv add <package>        # add a new dependency
uv remove <package>     # remove a dependency
uv sync                 # re-sync environment after manual pyproject.toml edits
```

---

## Project Structure

```
theEagle/
├── data/
│   ├── raw/                   # drop .fit files here
│   └── processed/
│       └── <activity_name>/   # one folder per parsed activity
├── src/
│   ├── fit_parser.py          # FIT → CSV parser (all message types)
│   ├── data_loader.py         # legacy single-file loader
│   ├── feature_engineering.py # derived metrics
│   ├── eda.py                 # visualisations
│   └── model.py               # running efficiency model
├── main.py                    # batch parse entry point
├── pyproject.toml             # uv project config & dependencies
└── uv.lock                    # locked dependency versions
```
