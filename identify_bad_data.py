import json
import pandas as pd
from pathlib import Path

# Identify problematic records
json_path = Path(r'C:\Users\A717631\repo\theEagle\reports\health_snapshots\health_snapshots_raw_2026-04-11_to_2026-07-20.json')

with open(json_path) as f:
    snapshots = json.load(f)

rows = []
for rec in snapshots:
    stats = rec.get('get_stats_and_body', {}) or rec.get('get_stats', {}) or {}
    stress_data = rec.get('get_stress_data', {}) or rec.get('get_all_day_stress', {}) or {}
    
    bb_high = stats.get('bodyBatteryHighestValue')
    bb_low = stats.get('bodyBatteryLowestValue')
    bb_drained = stats.get('bodyBatteryDrainedValue')
    
    # Identify suspect data
    suspect = False
    reason = ""
    
    # Rule 1: BB high and low are suspiciously close (range < 5)
    if bb_high is not None and bb_low is not None and (bb_high - bb_low) < 5 and bb_drained is not None and bb_drained < 3:
        suspect = True
        reason = "narrow_range_no_drain"
    
    # Rule 2: Very low max battery (<25) with minimal drain (incomplete data)
    if bb_high is not None and bb_high < 25 and bb_drained is not None and bb_drained < 10:
        suspect = True
        reason = "very_low_battery"
    
    rows.append({
        'date': rec.get('date'),
        'bb_high': bb_high,
        'bb_low': bb_low,
        'bb_drained': bb_drained,
        'stress': stats.get('averageStressLevel', stress_data.get('avgStressLevel')),
        'suspect': suspect,
        'reason': reason
    })

df = pd.DataFrame(rows)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

suspect_df = df[df['suspect']].copy()
if not suspect_df.empty:
    print("=== SUSPECT/INVALID DATA RECORDS ===\n")
    for _, row in suspect_df.iterrows():
        print(f"{row['date'].strftime('%Y-%m-%d')}: BB range {row['bb_low']}-{row['bb_high']}, Drained={row['bb_drained']}, Reason: {row['reason']}")
else:
    print("No suspect records found")
