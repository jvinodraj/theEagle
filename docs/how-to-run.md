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

---

## 7. Easy Run HR Tracker

Track heart-rate efficiency improvements across easy training runs coached by Coach Gokul.
Uses internationally recognised scoring metrics (not custom comparisons).

### 7.1 Setup — add your FIT files

Copy all easy-run `.fit` files exported from Garmin Connect into:

```
data/easy_runs/
```

Recommended naming convention (date must be at the front):

```
YYYY-MM-DD_day_label.fit
# examples
2026-04-16_thursday_easy.fit
2026-04-18_saturday_easy.fit
```

> The tool always uses the **FIT session timestamp** as the canonical activity date.
> A filename date mismatch is detected automatically and reported.

### 7.2 Run

```powershell
uv run easy-run-hr-report
```

That is the only command needed. The tool:

1. Parses every `.fit` file in `data/easy_runs/`
2. Strips the first 2–3 km warmup from each run
3. Computes international-standard metrics on the **steady-state section**
4. Scores each run 0–100
5. Writes three output files (see §7.4)

### 7.3 Metric definitions

All metrics are computed on the **steady-state section** — the portion of the run
after the first 2–3 km where HR has stabilised.  This means warmup HR does not
inflate or deflate any score, and a 5 km run and a 10 km run are compared fairly.

#### Efficiency Factor (EF)

```
EF = avg_power (W) ÷ avg_HR (bpm)  →  unit: W/bpm
```

| Source | Joe Friel *The Triathlete's Training Bible*; TrainingPeaks |
|--------|------------------------------------------------------------|
| Why it matters | Measures how much power your heart produces per beat. Higher = more aerobically efficient. |
| Reference scale | < 1.4 W/bpm — beginner · 1.4–1.8 W/bpm — recreational · 1.8+ W/bpm — trained |
| Load-independence | Calculated per heartbeat, so distance and duration cancel out. A 5 km and 10 km run are directly comparable. |
| Trend to watch | A rising EF over weeks (even 2–3%) signals genuine aerobic adaptation. |

#### Aerobic Decoupling %

```
decoupling = (EF_first_half − EF_second_half) / EF_first_half × 100
```

Measures how much your efficiency *drifts* from the first half to the second half of the steady section.

| Source | Garmin Connect; Joe Friel (same 5 % threshold) |
|--------|------------------------------------------------|
| Why it matters | If HR rises while pace stays the same, your aerobic system is tiring — the heart works harder for the same output. |
| Thresholds | < 5 % — aerobically fit for that run · 5–8 % — moderate cardiac drift · > 8 % — high drift / fatigue risk |
| Load-independence | Measures *drift rate*, not total load. A 10 km run and a 5 km run can both be below 5 %. |

#### HR Stability (steady-section HR std dev)

Standard deviation of heart rate within the steady section.
Low variability means you ran at a consistent effort with no sudden spikes.
Used as a 15 % weight in the overall score.

---

### 7.4 Output files

| File | Contents |
|------|----------|
| `reports/hr_improvement_plot.png` | Four-panel chart: EF trend · Aerobic Decoupling % per run · Score components · Pace vs HR scatter |
| `reports/hr_timeline_report.md` | Markdown table with one row per run: date, distance, EF, decoupling %, score, status, plain-English note |
| `reports/hr_improvement_analysis.csv` | Full raw + derived metrics for every run (import into Excel / Sheets) |

### 7.5 Score components and overall score

```
EF Score        (50 %)  =  clip((EF − 0.9) / (2.0 − 0.9) × 100,  0, 100)
Decoupling Score (35 %)  =  clip(100 − decoupling_pct × 8,         0, 100)
Stability Score (15 %)  =  clip(100 − max(0, hr_std − 1.5) × 10,  0, 100)

Overall Score = 0.50 × EF Score + 0.35 × Decoupling Score + 0.15 × Stability Score
```

### 7.6 Run status labels

| Label | Meaning |
|-------|---------|
| `baseline` | First run — no prior reference |
| `improving` | EF rose ≥ 1 % vs reference **and** decoupling < 5 % |
| `good` | EF score ≥ 52, decoupling moderate |
| `steady` | No clear direction either way |
| `fatigue_risk` | Aerobic decoupling > 8 % (high cardiac drift) |
| `below_par` | EF score < 45 — efficiency below your norm |

### 7.7 Weekly status labels

| Label | Trigger |
|-------|---------|
| `baseline` | First week |
| `improving` | Weekly score ≥ 58, EF trend flat or rising, decoupling ≤ 7 % |
| `steady` | Mixed signals, no red flag |
| `fatigue_risk` | Median decoupling > 8 %, or EF dropped > 1.5 %, or drift rising while decoupling ≥ 6.5 % |

### 7.8 Reading the chart panels

| Panel | What to look for |
|-------|-----------------|
| **EF Trend** (top-left) | Rising line = improving aerobic fitness. Dashed lines mark recreational (1.4) and trained (1.8) thresholds. |
| **Aerobic Decoupling %** (top-right) | Green bars = runs below 5 % threshold. Orange = 5–8 %. Red = above 8 %. The dashed green line is the Garmin fit-threshold. |
| **Score Components** (bottom-left) | EF score, decoupling score, stability score, and overall score over time. |
| **Pace vs HR scatter** (bottom-right) | Each dot is one run. Colour = EF (green = high). Ideal: dots move toward faster pace + lower HR as training progresses. |

### 7.9 Common questions

**Why can I compare a 5 km and a 10 km run?**  
Both EF and aerobic decoupling are *rate* metrics — they measure efficiency per
heartbeat and cardiac drift *rate*, not total output.  Distance and duration cancel
out, so the comparison is fair regardless of load.

**My EF is 1.53 W/bpm — is that good?**  
That's solidly in the recreational range (1.4–1.8). For a runner doing 25 km/week
training for a half-marathon, a target of 1.6–1.7 W/bpm after 8–12 weeks of
consistent easy running is realistic.

**What does it mean if decoupling is high on a long run?**  
Your aerobic base isn't yet strong enough to hold that distance without cardiac drift.
The fix is more Zone 2 easy runs (< 5 % decoupling), not more intensity.

**How do I export a FIT file from Garmin Connect?**  
Activity page → ⋯ (three dots) → Export Original. Save the `.fit` file into
`data/easy_runs/`.
```
