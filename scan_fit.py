import glob
import fitparse
import statistics
import os

files = glob.glob("data/**/*.fit", recursive=True)
header = ["file", "sport", "sub_sport", "total_timer_time", "total_calories", "avg_heart_rate", "max_heart_rate", "unknown_178", "unknown_196", "unknown_188", "unknown_184", "total_training_effect", "total_anaerobic_training_effect"]
print(",".join(header))

data = []
for fp in files:
    try:
        ff = fitparse.FitFile(fp)
        sessions = list(ff.get_messages("session"))
        if not sessions:
            continue
        s = sessions[0]
        row = {"file": fp}
        for field_name in header[1:]:
            row[field_name] = s.get_value(field_name)
        
        data.append(row)
        print(",".join(str(row.get(h, "")) for h in header))
    except Exception:
        pass

u178_values = [d["unknown_178"] for d in data if d.get("unknown_178") is not None]

print("\n--- Summary ---")
print(f"Files with unknown_178 not None: {len(u178_values)}")
if u178_values:
    print(f"Min unknown_178: {min(u178_values)}")
    print(f"Max unknown_178: {max(u178_values)}")
    print(f"Median unknown_178: {statistics.median(u178_values)}")

    top_10 = sorted(data, key=lambda x: x.get("unknown_178") if x.get("unknown_178") is not None else -1, reverse=True)[:10]
    print("Top 10 highest unknown_178:")
    for i, d in enumerate(top_10):
        print(f"{i+1}. {d['file']}: {d['unknown_178']}")

strength_files = [d for d in data if d.get("sport") == "strength"]
run_cycle_files = [d for d in data if d.get("sport") in ["running", "cycling"]]

u178_strength = [d for d in strength_files if d.get("unknown_178") is not None]
u178_run_cycle = [d for d in run_cycle_files if d.get("unknown_178") is not None]

print(f"Strength: {len(u178_strength)}/{len(strength_files)} have unknown_178")
print(f"Run/Cycle: {len(u178_run_cycle)}/{len(run_cycle_files)} have unknown_178")
