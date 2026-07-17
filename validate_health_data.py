#!/usr/bin/env python3
"""
Validation and repair script for Garmin health snapshot data.
Identifies and removes records with invalid body battery values.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup paths
repo_root = Path(__file__).parent
raw_path = repo_root / 'reports' / 'health_snapshots' / 'health_snapshots_raw_2026-04-11_to_2026-07-20.json'

print("=" * 75)
print("GARMIN HEALTH SNAPSHOT DATA VALIDATION REPORT")
print("=" * 75)
print()

# Load data
with raw_path.open('r', encoding='utf-8') as f:
    snapshots = json.load(f)

print(f"✓ Loaded {len(snapshots)} snapshot records from {raw_path.name}")
print()

# Extract rows
def first_dict(value):
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item
    return value if isinstance(value, dict) else {}

rows = []
for rec in snapshots:
    stats = rec.get('get_stats_and_body') or rec.get('get_stats') or {}
    stress_data = rec.get('get_stress_data') or rec.get('get_all_day_stress') or {}
    body_battery = first_dict(rec.get('get_body_battery'))
    body_battery_day = first_dict(rec.get('get_daily_body_battery'))

    rows.append({
        'date': rec.get('date') or stats.get('calendarDate'),
        'avg_stress_level': stats.get('averageStressLevel', stress_data.get('avgStressLevel')),
        'max_stress_level': stats.get('maxStressLevel', stress_data.get('maxStressLevel')),
        'bb_high': stats.get('bodyBatteryHighestValue', body_battery_day.get('bodyBatteryHighestValue')),
        'bb_low': stats.get('bodyBatteryLowestValue', body_battery_day.get('bodyBatteryLowestValue')),
        'bb_most_recent': stats.get('bodyBatteryMostRecentValue', body_battery_day.get('bodyBatteryMostRecentValue')),
        'bb_drained': stats.get('bodyBatteryDrainedValue', body_battery.get('drainedValue')),
        'stress_qualifier': stats.get('stressQualifier'),
    })

df = pd.DataFrame(rows)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

numeric_cols = [c for c in df.columns if c not in ['date', 'stress_qualifier']]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.sort_values('date').reset_index(drop=True)

# Validation logic
removed_dates = []
reason_counts = {}

for idx in df.index:
    bb_high = df.loc[idx, 'bb_high']
    bb_low = df.loc[idx, 'bb_low']
    bb_drained = df.loc[idx, 'bb_drained']
    date = df.loc[idx, 'date']
    
    should_remove = False
    reason = ""
    
    # Rule 1: Narrow range + minimal drain = incomplete data capture
    if (pd.notna(bb_high) and pd.notna(bb_low) and pd.notna(bb_drained)):
        bb_range = bb_high - bb_low
        if bb_range < 5 and bb_drained < 3:
            should_remove = True
            reason = "incomplete (narrow range + no drain)"
    
    # Rule 2: Very low battery ceiling (<25) with minimal drain = suspect data
    if not should_remove and pd.notna(bb_high) and pd.notna(bb_drained) and bb_high < 25 and bb_drained < 10:
        should_remove = True
        reason = "suspect (very low max BB)"
    
    if should_remove:
        removed_dates.append((date, reason, bb_high, bb_low, bb_drained))
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        # Clear body battery fields for this record
        df.loc[idx, ['bb_high', 'bb_low', 'bb_most_recent', 'bb_drained']] = None

# Report results
print("-" * 75)
print("VALIDATION RESULTS")
print("-" * 75)
print()

if removed_dates:
    print(f"⚠️  FOUND {len(removed_dates)} RECORDS WITH INVALID/INCOMPLETE DATA:")
    print()
    
    for date, reason, bb_high, bb_low, bb_drained in removed_dates:
        date_str = date.strftime('%Y-%m-%d') if pd.notna(date) else 'UNKNOWN'
        bb_high_str = f"{bb_high:.0f}" if pd.notna(bb_high) else 'N/A'
        bb_low_str = f"{bb_low:.0f}" if pd.notna(bb_low) else 'N/A'
        bb_drained_str = f"{bb_drained:.0f}" if pd.notna(bb_drained) else 'N/A'
        print(f"   {date_str}")
        print(f"      Reason: {reason}")
        print(f"      Values: BB_high={bb_high_str}, BB_low={bb_low_str}, Drained={bb_drained_str}")
        print()
    
    print("-" * 75)
    print("BREAKDOWN BY REASON:")
    print("-" * 75)
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        print(f"  • {reason}: {count} record(s)")
    print()
else:
    print("✓ No invalid records found - all data appears valid")
    print()

# Summary statistics
print("-" * 75)
print("DATA SUMMARY AFTER CLEANUP")
print("-" * 75)
print()
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Total records: {len(df)}")
print(f"Records removed: {len(removed_dates)}")
print(f"Records kept: {len(df) - len(removed_dates)}")
print()

# Show what to do
print("-" * 75)
print("ACTION REQUIRED")
print("-" * 75)
print()

if removed_dates:
    print("The notebook 'garmin_stress_body_battery_trend.ipynb' contains validation code")
    print("that automatically removes these invalid records when you run it.")
    print()
    print("✓ Run the notebook cell with the data loading code")
    print("✓ Look for the ⚠️  warning output showing removed records")
    print("✓ The invalid body battery fields will be set to NaN")
    print("✓ All downstream analyses will skip records with missing body battery data")
    print()
else:
    print("No action needed - all data is valid!")
    print()

print("=" * 75)
