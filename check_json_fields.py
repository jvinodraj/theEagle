import json
from pathlib import Path

# Read the JSON file
json_path = Path(r'C:\Users\A717631\repo\theEagle\reports\health_snapshots\health_snapshots_raw_2026-04-11_to_2026-07-20.json')

with open(json_path) as f:
    snapshots = json.load(f)

# Check the problematic dates
problem_dates = ['2026-07-05', '2026-07-10']

for rec in snapshots:
    date = rec.get('date')
    if date in problem_dates:
        print(f"\n=== {date} ===")
        stats = rec.get('get_stats_and_body', {})
        
        print(f"bodyBatteryHighestValue: {stats.get('bodyBatteryHighestValue')}")
        print(f"bodyBatteryLowestValue: {stats.get('bodyBatteryLowestValue')}")
        print(f"bodyBatteryMostRecentValue: {stats.get('bodyBatteryMostRecentValue')}")
        print(f"bodyBatteryAtWakeTime: {stats.get('bodyBatteryAtWakeTime')}")
        print(f"bodyBatteryDuringSleep: {stats.get('bodyBatteryDuringSleep')}")
        print(f"bodyBatteryChargedValue: {stats.get('bodyBatteryChargedValue')}")
        print(f"bodyBatteryDrainedValue: {stats.get('bodyBatteryDrainedValue')}")
        
        # Also check if there's a daily_body_battery object
        if 'get_daily_body_battery' in rec:
            print(f"\nget_daily_body_battery: {rec['get_daily_body_battery']}")
