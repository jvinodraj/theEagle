import glob
import fitparse
import statistics
import os

files = glob.glob("data/**/*.fit", recursive=True)

data = []
for fp in files:
    try:
        ff = fitparse.FitFile(fp)
        sessions = list(ff.get_messages("session"))
        if not sessions:
            continue
        s = sessions[0]
        row = {"file": fp}
        
        # Get standard fields
        for field_name in ["sport", "sub_sport", "total_timer_time", "total_calories", "avg_heart_rate", "max_heart_rate", "total_training_effect", "total_anaerobic_training_effect"]:
            row[field_name] = s.get_value(field_name)
        
        # Look for the unknown fields by ID
        # unknown_178 -> Field ID 178
        # unknown_196 -> Field ID 196
        # unknown_188 -> Field ID 188
        # unknown_184 -> Field ID 184
        for field in s.fields:
            if field.def_num == 178: row["unknown_178"] = field.value
            if field.def_num == 196: row["unknown_196"] = field.value
            if field.def_num == 188: row["unknown_188"] = field.value
            if field.def_num == 184: row["unknown_184"] = field.value
        
        data.append(row)
    except Exception:
        pass

header = ["file", "sport", "sub_sport", "total_timer_time", "total_calories", "avg_heart_rate", "max_heart_rate", "unknown_178", "unknown_196", "unknown_188", "unknown_184", "total_training_effect", "total_anaerobic_training_effect"]
print(",".join(header))
for d in data:
    print(",".join(str(d.get(h, "")) for h in header))

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

def is_strength(d):
    return d.get("sport") == "strength" or d.get("sport") == 62 or d.get("sub_sport") == "strength_training"

strength_files = [d for d in data if is_strength(d)]
run_cycle_files = [d for d in data if d.get("sport") in ["running", "cycling"]]

u178_strength = [d for d in strength_files if d.get("unknown_178") is not None]
u178_run_cycle = [d for d in run_cycle_files if d.get("unknown_178") is not None]

print(f"Strength: {len(u178_strength)}/{len(strength_files)} have unknown_178")
print(f"Run/Cycle: {len(u178_run_cycle)}/{len(run_cycle_files)} have unknown_178")
