import json
import pandas as pd
from pathlib import Path

# Read the JSON file
json_path = Path(r'C:\Users\A717631\repo\theEagle\reports\health_snapshots\health_snapshots_raw_2026-04-11_to_2026-07-20.json')

with open(json_path) as f:
    snapshots = json.load(f)

# Extract data for analysis
rows = []
for rec in snapshots:
    stats = rec.get('get_stats_and_body', {}) or rec.get('get_stats', {}) or {}
    stress_data = rec.get('get_stress_data', {}) or rec.get('get_all_day_stress', {}) or {}
    
    rows.append({
        'date': rec.get('date'),
        'avg_stress_level': stats.get('averageStressLevel', stress_data.get('avgStressLevel')),
        'bb_high': stats.get('bodyBatteryHighestValue'),
        'bb_low': stats.get('bodyBatteryLowestValue'),
        'bb_most_recent': stats.get('bodyBatteryMostRecentValue'),
    })

df = pd.DataFrame(rows)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Filter for June 20 to July 15
df_filtered = df[(df['date'] >= '2026-06-20') & (df['date'] <= '2026-07-15')].copy()
df_filtered['date_str'] = df_filtered['date'].dt.strftime('%b %d')

# Print in a nice format
print("Date\tStress\tBB_Low\tBB_High")
print("-" * 40)
for _, row in df_filtered.iterrows():
    date_str = row['date_str']
    stress = int(row['avg_stress_level']) if pd.notna(row['avg_stress_level']) else 'N/A'
    bb_low = int(row['bb_low']) if pd.notna(row['bb_low']) else 'N/A'
    bb_high = int(row['bb_high']) if pd.notna(row['bb_high']) else 'N/A'
    print(f"{date_str}\t{stress}\t{bb_low}\t{bb_high}")

# Check for obviously wrong values (body battery should be 0-100)
print("\n\n=== CHECKING FOR INVALID VALUES ===")
invalid = df[(df['bb_high'] < 0) | (df['bb_high'] > 100) | 
             (df['bb_low'] < 0) | (df['bb_low'] > 100) |
             (df['bb_most_recent'] < 0) | (df['bb_most_recent'] > 100) |
             (df['avg_stress_level'] < 0) | (df['avg_stress_level'] > 100)]

if not invalid.empty:
    print("INVALID VALUES FOUND:")
    print(invalid[['date', 'avg_stress_level', 'bb_low', 'bb_high', 'bb_most_recent']])
else:
    print("No invalid values found (all body battery values 0-100, stress 0-100)")
