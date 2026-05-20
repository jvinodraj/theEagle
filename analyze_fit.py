import os
import glob
from fitparse import FitFile
import math

def calculate_pearson(x, y):
    n = len(x)
    if n < 2: return 0
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_sq = sum(i * i for i in x)
    sum_y_sq = sum(j * j for j in y)
    p_sum = sum(i * j for i, j in zip(x, y))
    num = p_sum - (sum_x * sum_y / n)
    den = math.sqrt((sum_x_sq - sum_x**2 / n) * (sum_y_sq - sum_y**2 / n))
    if den == 0: return 0
    return num / den

def median(lst):
    n = len(lst)
    if n == 0: return 0
    s = sorted(lst)
    return s[n // 2] if n % 2 != 0 else (s[n // 2 - 1] + s[n // 2]) / 2

files = glob.glob("**/*.fit", recursive=True)
data = []

for f in files:
    try:
        ff = FitFile(f)
        for session in ff.get_messages("session"):
            sd = session.get_values()
            u178 = sd.get("unknown_178")
            time = sd.get("total_timer_time") # seconds
            cals = sd.get("total_calories")
            sport = sd.get("sport")
            subsport = sd.get("sub_sport")
            
            if u178 is not None and time and time > 0:
                per_hour = u178 / (time / 3600.0)
                data.append({
                    "file": os.path.basename(f),
                    "u178": u178,
                    "time": time,
                    "cals": cals if cals is not None else 0,
                    "sport": f"{sport}/{subsport}",
                    "per_hour": per_hour
                })
    except Exception:
        continue

if not data:
    print("No data found.")
else:
    u178_vals = [d["u178"] for d in data]
    ph_vals = [d["per_hour"] for d in data]
    time_vals = [d["time"] for d in data]
    cal_vals = [d["cals"] for d in data]
    
    print(f"Total Sessions: {len(data)}")
    print(f"Overall u178_per_hour: Min={min(ph_vals):.2f}, Median={median(ph_vals):.2f}, Max={max(ph_vals):.2f}")
    
    by_sport = {}
    for d in data:
        by_sport.setdefault(d["sport"], []).append(d["per_hour"])
    
    print("\nBy Sport/Subsport (Median u178_per_hour):")
    for s, vals in by_sport.items():
        print(f"  {s}: {median(vals):.2f} (n={len(vals)})")
        
    corr_time = calculate_pearson(u178_vals, time_vals)
    corr_cals = calculate_pearson(u178_vals, cal_vals)
    print(f"\nCorrelation u178 vs Time: {corr_time:.4f}")
    print(f"Correlation u178 vs Calories: {corr_cals:.4f}")
    
    print("\nSample Rows:")
    print(f"{'Filename':<30} | {'Dur(m)':<6} | {'Cals':<5} | {'u178':<5} | {'ph':<6}")
    for d in data[:5]:
        print(f"{d['file'][:30]:<30} | {d['time']/60:<6.1f} | {d['cals']:<5} | {d['u178']:<5} | {d['per_hour']:.1f}")
