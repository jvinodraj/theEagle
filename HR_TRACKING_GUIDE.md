# 📊 HR Improvement Tracking Guide

## Overview
This guide helps you track **Heart Rate improvements over your half marathon training period** using FIT files from your easy runs (Thursday and Saturday runs).

## ✅ Step-by-Step Setup

### Step 1: Create the FIT Files Directory
```bash
mkdir -p data/easy_runs
```

Your directory structure should look like:
```
theEagle/
├── data/
│   ├── easy_runs/          ← Store FIT files here
│   ├── raw/
│   └── processed/
├── hr_improvement_tracker.py
└── ...
```

### Step 2: Download FIT Files from Garmin Connect

**For each easy run:**
1. Go to [Garmin Connect](https://connect.garmin.com)
2. Find the **Thursday or Saturday easy run**
3. Click on the activity
4. Click **Export** → **Original (.FIT)**
5. Download the file

### Step 3: Rename & Organize Files

**Naming convention: `YYYY-MM-DD_day_easy.fit`**

Examples:
- `2026-04-16_thursday_easy.fit` (Thursday, April 16)
- `2026-04-18_saturday_easy.fit` (Saturday, April 18)
- `2026-04-23_thursday_easy.fit` (Thursday, April 23)
- `2026-04-25_saturday_easy.fit` (Saturday, April 25)

**Save all renamed files in:** `data/easy_runs/`

### Step 4: Run the Analysis

```bash
# Make sure you're in the project root
cd c:\Users\A717631\repo\theEagle

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Run the HR tracker
uv run python hr_improvement_tracker.py
```

### Step 5: Review Results

The script will:
1. **Print to console:**
   - Overall HR statistics
   - Week-by-week HR trends
   - HR improvement percentage
   - Thursday vs Saturday comparison

2. **Generate CSV report:**
   - `reports/hr_improvement_analysis.csv` - Detailed metrics per run

3. **Generate visualization:**
   - `reports/hr_improvement_plot.png` - 4 charts showing HR trends

## 📈 What Gets Tracked

For **each easy run**, the script extracts:
- **avg_hr**: Average heart rate during the run
- **max_hr**: Peak heart rate
- **min_hr**: Lowest heart rate
- **std_hr**: HR variability
- **duration_min**: Run duration
- **distance_km**: Distance covered
- **week**: Week number
- **date**: Run date

## 🎯 What to Look For

### Good Signs of Improvement ✓
- **Decreasing average HR** over time (same effort, lower HR = better fitness)
- **Lower max HR** while maintaining distance
- **Reduced HR variability** (more stable HR)
- **Consistent Thursday/Saturday HR** (stable baseline)

### Caution Signs ⚠️
- **Increasing average HR** (possible fatigue or illness)
- **High HR variability** (inconsistent pacing or recovery)
- **Elevated resting HR** (possible overtraining)

## 💡 Tips for Better Tracking

1. **Track consistently:**
   - Export runs immediately after completing them
   - Keep file naming consistent

2. **Minimum data needed:**
   - At least 4-5 runs (2 weeks) for meaningful trends
   - Better with all 8 weeks of data

3. **Export from Garmin:**
   - Use the **original FIT** export (not GPX)
   - Ensure HR data is captured (check on watch)

4. **Run again weekly:**
   - Re-run the script each week to update trends
   - Watch progression over the training period

## 📝 Example Output

```
======================================================================
HR IMPROVEMENT ANALYSIS
======================================================================

📈 Overall Statistics:
   • Period: 2026-04-16 to 2026-05-01
   • Total runs analyzed: 8
   • Average HR across all runs: 148.6 bpm
   • Min HR recorded: 140.2 bpm (Run: 2026-04-30)
   • Max HR recorded: 155.8 bpm (Run: 2026-04-16)

📊 Week-by-Week Analysis:

   Week 16:
     • Runs: 2
     • Avg HR: 151.5 bpm
     • HR range: 148.0 - 155.0 bpm
     • Max HR (avg): 165.2 bpm

   Week 17:
     • Runs: 2
     • Avg HR: 149.2 bpm
     • HR range: 147.5 - 150.9 bpm
     • Max HR (avg): 163.8 bpm

🎯 HR Improvement Trend:
   ✓ HR DECREASED by 5.3 bpm (3.4%)
     → Better training adaptation! Lower HR at same effort.
   
   First run: 2026-04-16 - Avg HR: 155.8 bpm
   Last run:  2026-05-01 - Avg HR: 150.5 bpm

📌 Day-of-Week Analysis:

   Thursdays:
     • Runs: 4
     • Avg HR: 149.0 bpm
     • HR range: 140.2 - 155.8 bpm

   Saturdays:
     • Runs: 4
     • Avg HR: 148.2 bpm
     • HR range: 142.1 - 153.1 bpm

✅ Report saved: reports/hr_improvement_analysis.csv
✅ Plot saved: reports/hr_improvement_plot.png
```

## 🔧 Troubleshooting

### "No FIT files found"
- Check files are in `data/easy_runs/`
- Check filenames follow the format: `YYYY-MM-DD_day_easy.fit`
- Run `ls data/easy_runs/` to verify

### "No HR data in file"
- Check HR recording was enabled on your watch during the run
- Verify file isn't corrupted (try re-downloading from Garmin)
- Check file size is > 1 KB

### Script crashes
- Ensure virtual environment is activated: `.\.venv\Scripts\Activate.ps1`
- Ensure required packages installed: `uv pip install fitparse pandas matplotlib seaborn`

## 📊 Next Steps

1. ✅ Download 2-3 easy runs as FIT files
2. ✅ Save them in `data/easy_runs/` with correct naming
3. ✅ Run: `uv run python hr_improvement_tracker.py`
4. ✅ Review the plots and CSV report
5. ✅ Share insights from your training

For questions, check the generated report in `reports/` directory!
