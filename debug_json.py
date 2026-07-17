import json
from pathlib import Path

# Use absolute path
json_path = Path(r'C:\Users\A717631\repo\theEagle\reports\health_snapshots\health_snapshots_raw_2026-04-11_to_2026-07-20.json')

with open(json_path) as f:
    data = json.load(f)
    
print(f"Total records: {len(data)}")
print("\nFirst 3 records to understand structure:")

for i, rec in enumerate(data[:3]):
    print(f"\n=== Record {i} ===")
    print(f"Date: {rec.get('date')}")
    stats = rec.get('get_stats_and_body', {})
    print(f"bb_high: {stats.get('bodyBatteryHighestValue')}")
    print(f"bb_low: {stats.get('bodyBatteryLowestValue')}")
    print(f"bb_most_recent: {stats.get('bodyBatteryMostRecentValue')}")
    print(f"avg_stress_level: {stats.get('averageStressLevel')}")
    print(f"max_stress_level: {stats.get('maxStressLevel')}")

print("\n\n=== Looking for Jul 4-10 problematic values ===")
for rec in data:
    date = rec.get('date', '')
    if '2026-07-04' in str(date) or '2026-07-10' in str(date):
        print(f"\nDate: {date}")
        stats = rec.get('get_stats_and_body', {})
        print(f"  bb_high: {stats.get('bodyBatteryHighestValue')}")
        print(f"  bb_low: {stats.get('bodyBatteryLowestValue')}")
        print(f"  bb_most_recent: {stats.get('bodyBatteryMostRecentValue')}")
        print(f"  avg_stress: {stats.get('averageStressLevel')}")
        print(f"  Full stats keys: {list(stats.keys())}")
