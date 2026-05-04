#!/usr/bin/env python3
"""
Quick setup script for HR Improvement Tracker
Creates necessary directories and provides instructions
"""

from pathlib import Path
import sys

def setup():
    print("=" * 70)
    print("🏃 HR IMPROVEMENT TRACKER - SETUP")
    print("=" * 70)
    
    # Create directories
    easy_runs_dir = Path("data/easy_runs")
    reports_dir = Path("reports")
    
    easy_runs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ Created directories:")
    print(f"   • {easy_runs_dir}")
    print(f"   • {reports_dir}")
    
    # Check for FIT files
    fit_files = list(easy_runs_dir.glob("*.fit"))
    
    print(f"\n📁 FIT files found: {len(fit_files)}")
    if fit_files:
        for f in sorted(fit_files):
            print(f"   • {f.name}")
    else:
        print("   ⚠️  None yet. Follow the guide below...")
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print("""
1. Download FIT files from Garmin Connect
   • Go to https://connect.garmin.com
   • Find your easy runs (Thursday & Saturday)
   • Export as FIT file

2. Rename files to: YYYY-MM-DD_day_easy.fit
   Examples:
   • 2026-04-16_thursday_easy.fit
   • 2026-04-18_saturday_easy.fit

3. Save files in: data/easy_runs/

4. Run the analysis:
   $ uv run python hr_improvement_tracker.py

5. Check results in:
   • reports/hr_improvement_analysis.csv
   • reports/hr_improvement_plot.png

For detailed guide, see: HR_TRACKING_GUIDE.md
""")
    print("=" * 70)

if __name__ == "__main__":
    setup()
