# 🚀 QUICK START - HR Improvement Tracker

## 5-Minute Setup

### 1️⃣ Create directory for FIT files
```bash
mkdir -p data/easy_runs
```

### 2️⃣ Download FIT files from Garmin Connect
- Go to https://connect.garmin.com
- Find Thursday/Saturday easy runs
- Export as FIT (original format)
- 💾 Save to `data/easy_runs/`

### 3️⃣ Rename files (IMPORTANT!)
**Format: `YYYY-MM-DD_day_easy.fit`**

**Examples:**
```
2026-04-16_thursday_easy.fit
2026-04-18_saturday_easy.fit
2026-04-23_thursday_easy.fit
2026-04-25_saturday_easy.fit
```

### 4️⃣ Run the analysis
```bash
# Ensure virtual env is active
.\.venv\Scripts\Activate.ps1

# Run tracker
uv run python hr_improvement_tracker.py
```

### 5️⃣ View results
✅ Console output with HR stats  
✅ CSV: `reports/hr_improvement_analysis.csv`  
✅ Plot: `reports/hr_improvement_plot.png`

---

## 📊 What You Get

| Metric | Meaning | Good Sign |
|--------|---------|-----------|
| Avg HR | Average HR during run | ⬇️ Decreasing over weeks |
| Max HR | Peak HR | ⬇️ Lower week-by-week |
| Std HR | HR variability | ⬇️ More stable |
| Trend | Overall HR change | **↓ Lower = Better fitness** |

---

## 🎯 Interpretation Guide

### ✅ Improving
- Avg HR is **decreasing** over time (same effort, lower HR)
- Max HR is **lower** week-by-week
- Trend shows **negative** percentage change

### ⚠️ Warning Signs
- Avg HR is **increasing** (fatigue, illness, or overtraining)
- High **HR variability** (inconsistent pacing)
- Elevated **resting HR** (need recovery day)

---

## 📁 File Structure
```
data/
├── easy_runs/
│   ├── 2026-04-16_thursday_easy.fit    ← Your FIT files go here
│   ├── 2026-04-18_saturday_easy.fit
│   └── ...
├── raw/
└── processed/

reports/
├── hr_improvement_analysis.csv          ← Generated CSV report
└── hr_improvement_plot.png              ← Generated 4-chart plot
```

---

## ⚡ Common Issues

| Issue | Solution |
|-------|----------|
| "No FIT files found" | Check files in `data/easy_runs/` with correct naming |
| "No HR data" | Enable HR on your watch, re-download from Garmin |
| Script errors | Run `.\.venv\Scripts\Activate.ps1` first |

---

## 📖 Learn More
See `HR_TRACKING_GUIDE.md` for complete details

---

## 💡 Tips
1. Start with 2-3 runs to test the pipeline
2. Re-run weekly to see progression
3. Compare Thursday vs Saturday trends
4. Share the plots with your coach!

**Ready to track your HR improvement? Download your FIT files and start! 🏃‍♂️**
