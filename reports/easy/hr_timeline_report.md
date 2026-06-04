# Easy Run Endurance Analysis

Overall status: **improving**

- Efficiency Factor (EF, W/bpm — Joe Friel / TrainingPeaks standard): first run 1.536 W/bpm -> last run 1.657 W/bpm (+7.9%). Reference: <1.4 beginner, 1.4–1.8 recreational, 1.8+ trained.
- Aerobic Decoupling (Garmin / Joe Friel standard — <5% = aerobically fit run): median 7.0%, 3/14 runs below the 5% threshold. This metric is load-independent — valid for comparing 5 km and 10 km easy runs.
- Latest run score 62.9/100 (EF 68.8, decoupling 45.4, stability 84.0).

## Metric Availability

- Measured directly from current FIT exports: session totals, heart rate, power, cadence, stride length, stance time, vertical oscillation/ratio, Garmin training effect, Garmin zone target settings, and profile weight/resting HR.
- Measured from session metadata (mapped field): estimated sweat loss in mL/L.
- Estimated in this report: load focus category only. It is inferred from Garmin aerobic and anaerobic training effect, not read directly from the FIT file.
- Unavailable in the current FIT exports: Body Battery before run, HRV status, stress level, recovery-time recommendation, per-run sleep metrics, VO2 max, direct exercise load, and left/right balance.

## Longitudinal Tracking

| Date | Workout | km | Steady Pace | Steady HR | EF W/bpm | Drift % | Pace vs ref % | HR cost vs ref % | 3-run work kJ | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-04-16 | 45Min Easy | 6.03 | 7.47 | 151 | 1.536 | 7.2 | unavailable | unavailable | 621.3 | baseline |
| 2026-04-18 | 7k Easy | 7.01 | 7.42 | 158 | 1.474 | 2.5 | 0.7% | -3.5% | 1342.7 | improving |
| 2026-04-23 | 45min Easy | 6.14 | 7.37 | 152 | 1.565 | 5.0 | 0.7% | 4.8% | 1980.0 | improving |
| 2026-04-25 | 5k Easy | 5.01 | 7.39 | 156 | 1.532 | 5.4 | -0.3% | -2.6% | 1877.7 | steady |
| 2026-04-30 | 60min Easy | 8.24 | 7.29 | 156 | 1.563 | 7.1 | 1.4% | 0.9% | 2024.1 | steady |
| 2026-05-02 | 2026-05-02_saturday_easy | 10.01 | 7.35 | 155 | 1.538 | 9.8 | -0.8% | 0.2% | 2428.8 | fatigue_risk |
| 2026-05-07 | 60min Easy | 8.19 | 7.35 | 152 | 1.520 | 8.4 | 0.0% | 1.4% | 2744.2 | fatigue_risk |
| 2026-05-09 | 75min Easy | 10.22 | 7.37 | 150 | 1.538 | 8.4 | -0.3% | 1.1% | 2919.4 | fatigue_risk |
| 2026-05-14 | 75min Easy | 10.03 | 7.49 | 153 | 1.484 | 6.5 | -1.6% | -3.5% | 2897.8 | steady |
| 2026-05-21 | 90min Easy | 12.28 | 7.35 | 154 | 1.525 | 7.3 | 1.9% | 1.6% | 3325.2 | steady |
| 2026-05-23 | 12K Run | 12.01 | 6.95 | 156 | 1.564 | 4.6 | 5.8% | 4.6% | 3517.6 | improving |
| 2026-05-28 | 90min Easy | 12.24 | 7.37 | 156 | 1.543 | 7.9 | -5.7% | -5.7% | 3798.4 | fatigue_risk |
| 2026-06-02 | 75min Easy | 10.26 | 7.32 | 152 | 1.607 | 6.4 | 0.7% | 3.3% | 3639.4 | improving |
| 2026-06-04 | 90min Easy | 12.23 | 7.38 | 146 | 1.657 | 6.8 | -0.8% | 2.6% | 3715.3 | improving |

## Weekly Summary

| Week | Dates | Runs | Score | EF W/bpm | Decoupling % | Status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 15 | 2026-04-16 to 2026-04-18 | 2 | 60.5 | 1.505 | 4.9 | baseline |
| 16 | 2026-04-23 to 2026-04-25 | 2 | 64.0 | 1.548 | 5.2 | improving |
| 17 | 2026-04-30 to 2026-05-02 | 2 | 51.7 | 1.550 | 8.5 | fatigue_risk |
| 18 | 2026-05-07 to 2026-05-09 | 2 | 51.0 | 1.529 | 8.4 | fatigue_risk |
| 19 | 2026-05-14 to 2026-05-14 | 1 | 55.8 | 1.484 | 6.5 | fatigue_risk |
| 20 | 2026-05-21 to 2026-05-23 | 2 | 59.7 | 1.544 | 6.0 | improving |
| 21 | 2026-05-28 to 2026-05-28 | 1 | 51.9 | 1.543 | 7.9 | fatigue_risk |
| 22 | 2026-06-02 to 2026-06-04 | 2 | 62.2 | 1.632 | 6.6 | improving |

## Overall Observations Worth Tracking

- Steady-state easy pace changed +1.2% from the first comparable run to the latest run.
- Steady power-per-heartbeat changed +7.9% across the timeline, which is the cleanest aerobic-efficiency signal in this dataset.
- Aerobic decoupling moved -0.4 percentage points from the opening run to the latest run.
- 12 runs were recorded at 30 C or hotter; heat is a plausible confounder for drift and HR cost in this sample.
- 3/14 runs crossed the 8% decoupling line, which is the strongest within-run fatigue signal in these easy sessions.

## Per-Run Summaries

### 2026-04-16 - 45Min Easy

#### 1. Executive Summary

- 6.03 km in 45.0 min, average pace 7.47 min/km, steady pace 7.47 min/km.
- Average HR 148 bpm, steady HR 151 bpm, EF 1.536 W/bpm, aerobic decoupling 7.2%.
- Baseline run for this dataset segment; use later runs to judge adaptation.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 45.0 min | measured |
| Basic | Distance | 6.03 km | measured |
| Basic | Average pace | 7.47 min/km | measured |
| Basic | Moving pace | 7.46 min/km | measured |
| Basic | Best pace | 6.38 min/km | measured |
| Basic | Elevation gain/loss | 4.0 m / 2.0 m | measured |
| Environment | Average / max temperature | unavailable / unavailable | unavailable |
| Heart rate | Average / max HR | 148 / 158 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.6%, Z2 8.5%, Z3 89.9%, Z4 0.0%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 29.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 126.0 bpm | measured |
| Heart rate | Resting HR (profile) | 74.0 bpm | measured |
| Power | Average / max / normalized power | 230.0 W / 273.0 W / 231.0 W | measured |
| Power | Power zones | Z1 0.6%, Z2 97.8%, Z3 1.5%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.19 W/kg / 7.3% CV | measured |
| Dynamics | Cadence / stride length | 166 spm / 0.797 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 280.8 ms / 78.6 mm / 9.88% | measured |
| Aerobic | Training effect / anaerobic TE | 3.0 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 750.0 mL (0.750 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- This run is best interpreted against the same duration bucket rather than as a standalone benchmark.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.536 W/bpm and steady speed per HR was 0.01473 m/s/bpm.
- Aerobic decoupling was 7.2% and power-HR decoupling was 5.2%.
- Time spent in Garmin HR zone 2 was 3.8 min; pace inside that zone was 7.46 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 41.7/100 with steady HR rise 6.0 bpm. 
- Rolling 3-run load proxy: 621.3 kJ mechanical work and 3.0 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 103.1 J/m and average running economy was 103.1 W per m/s.
- Cadence stability was 6.1% CV and pace durability changed 1.1% from early to late thirds.

#### 7. Concerns or Risks

- No acute red flags stand out in this file beyond the usual Garmin power and training-effect uncertainty.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.

### 2026-04-18 - 7k Easy

#### 1. Executive Summary

- 7.01 km in 52.8 min, average pace 7.53 min/km, steady pace 7.42 min/km.
- Average HR 155 bpm, steady HR 158 bpm, EF 1.474 W/bpm, aerobic decoupling 2.5%.
- Reference comparison (2026-04-16): pace 0.7% better/worse depending on sign, EF -4.0%, drift delta -4.7 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 52.8 min | measured |
| Basic | Distance | 7.01 km | measured |
| Basic | Average pace | 7.53 min/km | measured |
| Basic | Moving pace | 7.43 min/km | measured |
| Basic | Best pace | 5.69 min/km | measured |
| Basic | Elevation gain/loss | 4.0 m / 4.0 m | measured |
| Environment | Average / max temperature | 31.0 C / 32.0 C | measured |
| Heart rate | Average / max HR | 155 / 167 bpm | measured |
| Heart rate | HR zone distribution | Z1 0.6%, Z2 4.2%, Z3 61.0%, Z4 34.2%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 29.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 130.0 bpm | measured |
| Heart rate | Resting HR (profile) | 73.0 bpm | measured |
| Power | Average / max / normalized power | 228.0 W / 324.0 W / 232.0 W | measured |
| Power | Power zones | Z1 1.6%, Z2 24.7%, Z3 73.6%, Z4 0.1%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.17 W/kg / 10.2% CV | measured |
| Dynamics | Cadence / stride length | 162 spm / 0.809 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 281.4 ms / 79.4 mm / 9.85% | measured |
| Aerobic | Training effect / anaerobic TE | 3.1 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 879.0 mL (0.879 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- The steady section stayed inside the usual aerobic-decoupling target, which supports durable easy-run metabolism for this duration.
- At nearly the same steady pace as the reference run, HR cost changed -4.1%.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.474 W/bpm and steady speed per HR was 0.01422 m/s/bpm.
- Aerobic decoupling was 2.5% and power-HR decoupling was 1.3%.
- Time spent in Garmin HR zone 2 was 1.6 min; pace inside that zone was 8.29 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 99.4/100 with steady HR rise 4.1 bpm. 
- Rolling 3-run load proxy: 1342.7 kJ mechanical work and 6.1 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 103.1 J/m and average running economy was 103.1 W per m/s.
- Cadence stability was 7.5% CV and pace durability changed -3.0% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 31.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 34.2% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.
- This is a good candidate benchmark run; keep conditions similar and use it to judge whether aerobic efficiency is actually improving.

### 2026-04-23 - 45min Easy

#### 1. Executive Summary

- 6.14 km in 45.0 min, average pace 7.33 min/km, steady pace 7.37 min/km.
- Average HR 149 bpm, steady HR 152 bpm, EF 1.565 W/bpm, aerobic decoupling 5.0%.
- Reference comparison (2026-04-18): pace 0.7% better/worse depending on sign, EF 6.2%, drift delta 2.4 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 45.0 min | measured |
| Basic | Distance | 6.14 km | measured |
| Basic | Average pace | 7.33 min/km | measured |
| Basic | Moving pace | 7.35 min/km | measured |
| Basic | Best pace | 6.62 min/km | measured |
| Basic | Elevation gain/loss | 3.0 m / 3.0 m | measured |
| Environment | Average / max temperature | 30.0 C / 31.0 C | measured |
| Heart rate | Average / max HR | 149 / 157 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.1%, Z2 7.0%, Z3 91.9%, Z4 0.0%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 31.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 124.0 bpm | measured |
| Heart rate | Resting HR (profile) | 66.0 bpm | measured |
| Power | Average / max / normalized power | 236.0 W / 271.0 W / 237.0 W | measured |
| Power | Power zones | Z1 0.1%, Z2 64.5%, Z3 35.4%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.26 W/kg / 5.7% CV | measured |
| Dynamics | Cadence / stride length | 164 spm / 0.821 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 284.2 ms / 81.0 mm / 9.87% | measured |
| Aerobic | Training effect / anaerobic TE | 3.0 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 750.0 mL (0.750 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- The steady section stayed inside the usual aerobic-decoupling target, which supports durable easy-run metabolism for this duration.
- At nearly the same steady pace as the reference run, HR cost changed +3.9%.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.565 W/bpm and steady speed per HR was 0.01490 m/s/bpm.
- Aerobic decoupling was 5.0% and power-HR decoupling was 3.4%.
- Time spent in Garmin HR zone 2 was 3.1 min; pace inside that zone was 7.31 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 78.5/100 with steady HR rise 2.1 bpm. 
- Rolling 3-run load proxy: 1980.0 kJ mechanical work and 9.1 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 103.8 J/m and average running economy was 103.8 W per m/s.
- Cadence stability was 4.2% CV and pace durability changed 0.6% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 30.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.
- This is a good candidate benchmark run; keep conditions similar and use it to judge whether aerobic efficiency is actually improving.

### 2026-04-25 - 5k Easy

#### 1. Executive Summary

- 5.01 km in 36.8 min, average pace 7.35 min/km, steady pace 7.39 min/km.
- Average HR 152 bpm, steady HR 156 bpm, EF 1.532 W/bpm, aerobic decoupling 5.4%.
- Reference comparison (2026-04-23): pace -0.3% better/worse depending on sign, EF -2.1%, drift delta 0.5 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 36.8 min | measured |
| Basic | Distance | 5.01 km | measured |
| Basic | Average pace | 7.35 min/km | measured |
| Basic | Moving pace | 7.34 min/km | measured |
| Basic | Best pace | 6.77 min/km | measured |
| Basic | Elevation gain/loss | 2.0 m / 3.0 m | measured |
| Environment | Average / max temperature | 31.0 C / 32.0 C | measured |
| Heart rate | Average / max HR | 152 / 161 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.8%, Z2 1.8%, Z3 90.0%, Z4 6.4%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 28.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 132.0 bpm | measured |
| Heart rate | Resting HR (profile) | 64.0 bpm | measured |
| Power | Average / max / normalized power | 235.0 W / 261.0 W / 237.0 W | measured |
| Power | Power zones | Z1 0.4%, Z2 65.7%, Z3 33.9%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.25 W/kg / 6.4% CV | measured |
| Dynamics | Cadence / stride length | 162 spm / 0.830 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 286.5 ms / 82.1 mm / 9.89% | measured |
| Aerobic | Training effect / anaerobic TE | 2.8 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 612.0 mL (0.612 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At nearly the same steady pace as the reference run, HR cost changed -2.3%.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.532 W/bpm and steady speed per HR was 0.01451 m/s/bpm.
- Aerobic decoupling was 5.4% and power-HR decoupling was 2.2%.
- Time spent in Garmin HR zone 2 was 0.7 min; pace inside that zone was 7.57 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 73.6/100 with steady HR rise 2.7 bpm. 
- Rolling 3-run load proxy: 1877.7 kJ mechanical work and 8.9 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 103.6 J/m and average running economy was 103.6 W per m/s.
- Cadence stability was 5.3% CV and pace durability changed 0.8% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 31.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-04-30 - 60min Easy

#### 1. Executive Summary

- 8.24 km in 60.1 min, average pace 7.30 min/km, steady pace 7.29 min/km.
- Average HR 152 bpm, steady HR 156 bpm, EF 1.563 W/bpm, aerobic decoupling 7.1%.
- Reference comparison (2026-04-25): pace 1.4% better/worse depending on sign, EF 2.0%, drift delta 1.7 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 60.1 min | measured |
| Basic | Distance | 8.24 km | measured |
| Basic | Average pace | 7.30 min/km | measured |
| Basic | Moving pace | 7.30 min/km | measured |
| Basic | Best pace | 5.65 min/km | measured |
| Basic | Elevation gain/loss | 9.0 m / 12.0 m | measured |
| Environment | Average / max temperature | 30.0 C / 31.0 C | measured |
| Heart rate | Average / max HR | 152 / 165 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.6%, Z2 5.0%, Z3 68.4%, Z4 24.9%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 35.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 123.0 bpm | measured |
| Heart rate | Resting HR (profile) | 63.0 bpm | measured |
| Power | Average / max / normalized power | 240.0 W / 338.0 W / 242.0 W | measured |
| Power | Power zones | Z1 0.3%, Z2 46.9%, Z3 51.7%, Z4 1.1%, Z5 0.1% | measured |
| Power | W/kg / stability | 3.31 W/kg / 8.0% CV | measured |
| Dynamics | Cadence / stride length | 164 spm / 0.828 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 284.3 ms / 81.5 mm / 9.85% | measured |
| Aerobic | Training effect / anaerobic TE | 3.2 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1001.0 mL (1.001 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed +1.4%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.563 W/bpm and steady speed per HR was 0.01464 m/s/bpm.
- Aerobic decoupling was 7.1% and power-HR decoupling was 5.0%.
- Time spent in Garmin HR zone 2 was 3.0 min; pace inside that zone was 7.57 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 52.9/100 with steady HR rise 4.3 bpm. 
- Rolling 3-run load proxy: 2024.1 kJ mechanical work and 9.0 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 105.1 J/m and average running economy was 105.1 W per m/s.
- Cadence stability was 4.6% CV and pace durability changed 0.1% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 30.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 24.9% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-05-02 - 2026-05-02_saturday_easy

#### 1. Executive Summary

- 10.01 km in 73.3 min, average pace 7.32 min/km, steady pace 7.35 min/km.
- Average HR 150 bpm, steady HR 155 bpm, EF 1.538 W/bpm, aerobic decoupling 9.8%.
- Reference comparison (2026-04-30): pace -0.8% better/worse depending on sign, EF -1.6%, drift delta 2.7 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 73.3 min | measured |
| Basic | Distance | 10.01 km | measured |
| Basic | Average pace | 7.32 min/km | measured |
| Basic | Moving pace | 7.33 min/km | measured |
| Basic | Best pace | 6.08 min/km | measured |
| Basic | Elevation gain/loss | 6.0 m / 9.0 m | measured |
| Environment | Average / max temperature | 32.0 C / 33.0 C | measured |
| Heart rate | Average / max HR | 150 / 164 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.0%, Z2 10.6%, Z3 67.4%, Z4 21.0%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 34.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 128.0 bpm | measured |
| Heart rate | Resting HR (profile) | 61.0 bpm | measured |
| Power | Average / max / normalized power | 237.0 W / 285.0 W / 238.0 W | measured |
| Power | Power zones | Z1 0.3%, Z2 69.0%, Z3 30.7%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.29 W/kg / 6.6% CV | measured |
| Dynamics | Cadence / stride length | 166 spm / 0.817 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 282.5 ms / 80.3 mm / 9.83% | measured |
| Aerobic | Training effect / anaerobic TE | 3.2 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1221.0 mL (1.221 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed -0.8%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.538 W/bpm and steady speed per HR was 0.01468 m/s/bpm.
- Aerobic decoupling was 9.8% and power-HR decoupling was 10.0%.
- Time spent in Garmin HR zone 2 was 7.8 min; pace inside that zone was 7.31 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 9.7/100 with steady HR rise 6.6 bpm. 
- Rolling 3-run load proxy: 2428.8 kJ mechanical work and 9.2 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 104.1 J/m and average running economy was 104.1 W per m/s.
- Cadence stability was 4.5% CV and pace durability changed 0.4% from early to late thirds.

#### 7. Concerns or Risks

- High aerobic decoupling at 9.8% suggests cardiovascular drift beyond a typical easy-run target.
- Average temperature was 32.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 21.0% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- Slow the first 15-20 minutes or insert brief walk resets so the steady section stays below the decoupling threshold.
- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-05-07 - 60min Easy

#### 1. Executive Summary

- 8.19 km in 60.1 min, average pace 7.34 min/km, steady pace 7.35 min/km.
- Average HR 149 bpm, steady HR 152 bpm, EF 1.520 W/bpm, aerobic decoupling 8.4%.
- Reference comparison (2026-05-02): pace 0.0% better/worse depending on sign, EF -1.2%, drift delta -1.4 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 60.1 min | measured |
| Basic | Distance | 8.19 km | measured |
| Basic | Average pace | 7.34 min/km | measured |
| Basic | Moving pace | 7.34 min/km | measured |
| Basic | Best pace | 6.29 min/km | measured |
| Basic | Elevation gain/loss | 1.0 m / 8.0 m | measured |
| Environment | Average / max temperature | 30.0 C / 31.0 C | measured |
| Heart rate | Average / max HR | 149 / 164 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.7%, Z2 6.8%, Z3 85.1%, Z4 6.4%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 35.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 129.0 bpm | measured |
| Heart rate | Resting HR (profile) | 63.0 bpm | measured |
| Power | Average / max / normalized power | 231.0 W / 267.0 W / 232.0 W | measured |
| Power | Power zones | Z1 0.1%, Z2 84.4%, Z3 15.5%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.25 W/kg / 5.3% CV | measured |
| Dynamics | Cadence / stride length | 166 spm / 0.818 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 282.9 ms / 80.6 mm / 9.86% | measured |
| Aerobic | Training effect / anaerobic TE | 3.1 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1001.0 mL (1.001 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed +0.0%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.520 W/bpm and steady speed per HR was 0.01487 m/s/bpm.
- Aerobic decoupling was 8.4% and power-HR decoupling was 7.9%.
- Time spent in Garmin HR zone 2 was 4.1 min; pace inside that zone was 7.74 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 25.9/100 with steady HR rise 6.4 bpm. 
- Rolling 3-run load proxy: 2744.2 kJ mechanical work and 9.5 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 101.7 J/m and average running economy was 101.7 W per m/s.
- Cadence stability was 2.3% CV and pace durability changed 0.1% from early to late thirds.

#### 7. Concerns or Risks

- High aerobic decoupling at 8.4% suggests cardiovascular drift beyond a typical easy-run target.
- Average temperature was 30.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- Slow the first 15-20 minutes or insert brief walk resets so the steady section stays below the decoupling threshold.
- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-05-09 - 75min Easy

#### 1. Executive Summary

- 10.22 km in 75.0 min, average pace 7.35 min/km, steady pace 7.37 min/km.
- Average HR 147 bpm, steady HR 150 bpm, EF 1.538 W/bpm, aerobic decoupling 8.4%.
- Reference comparison (2026-05-07): pace -0.3% better/worse depending on sign, EF 1.2%, drift delta -0.0 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 75.0 min | measured |
| Basic | Distance | 10.22 km | measured |
| Basic | Average pace | 7.35 min/km | measured |
| Basic | Moving pace | 7.35 min/km | measured |
| Basic | Best pace | 6.45 min/km | measured |
| Basic | Elevation gain/loss | 1.0 m / 8.0 m | measured |
| Environment | Average / max temperature | 29.0 C / 31.0 C | measured |
| Heart rate | Average / max HR | 147 / 160 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.4%, Z2 17.0%, Z3 81.4%, Z4 0.2%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 29.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 125.0 bpm | measured |
| Heart rate | Resting HR (profile) | 59.0 bpm | measured |
| Power | Average / max / normalized power | 232.0 W / 284.0 W / 232.0 W | measured |
| Power | Power zones | Z1 0.1%, Z2 87.9%, Z3 12.0%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.27 W/kg / 4.6% CV | measured |
| Dynamics | Cadence / stride length | 166 spm / 0.812 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 281.9 ms / 80.0 mm / 9.85% | measured |
| Aerobic | Training effect / anaerobic TE | 3.2 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1250.0 mL (1.250 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed -0.3%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.538 W/bpm and steady speed per HR was 0.01504 m/s/bpm.
- Aerobic decoupling was 8.4% and power-HR decoupling was 7.9%.
- Time spent in Garmin HR zone 2 was 12.8 min; pace inside that zone was 7.26 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 31.7/100 with steady HR rise 5.5 bpm. 
- Rolling 3-run load proxy: 2919.4 kJ mechanical work and 9.5 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 102.2 J/m and average running economy was 102.2 W per m/s.
- Cadence stability was 2.9% CV and pace durability changed 0.4% from early to late thirds.

#### 7. Concerns or Risks

- High aerobic decoupling at 8.4% suggests cardiovascular drift beyond a typical easy-run target.

#### 8. Recommendations

- Slow the first 15-20 minutes or insert brief walk resets so the steady section stays below the decoupling threshold.

### 2026-05-14 - 75min Easy

#### 1. Executive Summary

- 10.03 km in 75.1 min, average pace 7.49 min/km, steady pace 7.49 min/km.
- Average HR 150 bpm, steady HR 153 bpm, EF 1.484 W/bpm, aerobic decoupling 6.5%.
- Reference comparison (2026-05-09): pace -1.6% better/worse depending on sign, EF -3.5%, drift delta -1.9 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 75.1 min | measured |
| Basic | Distance | 10.03 km | measured |
| Basic | Average pace | 7.49 min/km | measured |
| Basic | Moving pace | 7.50 min/km | measured |
| Basic | Best pace | 6.62 min/km | measured |
| Basic | Elevation gain/loss | 3.0 m / 6.0 m | measured |
| Environment | Average / max temperature | 31.0 C / 32.0 C | measured |
| Heart rate | Average / max HR | 150 / 161 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.0%, Z2 3.8%, Z3 88.4%, Z4 6.9%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 35.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 123.0 bpm | measured |
| Heart rate | Resting HR (profile) | 55.0 bpm | measured |
| Power | Average / max / normalized power | 226.0 W / 270.0 W / 227.0 W | measured |
| Power | Power zones | Z1 0.1%, Z2 97.6%, Z3 2.3%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.18 W/kg / 4.4% CV | measured |
| Dynamics | Cadence / stride length | 166 spm / 0.796 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 282.6 ms / 79.0 mm / 9.93% | measured |
| Aerobic | Training effect / anaerobic TE | 3.1 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1251.0 mL (1.251 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed -1.6%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.484 W/bpm and steady speed per HR was 0.01451 m/s/bpm.
- Aerobic decoupling was 6.5% and power-HR decoupling was 7.0%.
- Time spent in Garmin HR zone 2 was 2.9 min; pace inside that zone was 7.35 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 59.0/100 with steady HR rise 4.5 bpm. 
- Rolling 3-run load proxy: 2897.8 kJ mechanical work and 9.4 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 101.6 J/m and average running economy was 101.6 W per m/s.
- Cadence stability was 3.1% CV and pace durability changed 0.0% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 31.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-05-21 - 90min Easy

#### 1. Executive Summary

- 12.28 km in 90.0 min, average pace 7.34 min/km, steady pace 7.35 min/km.
- Average HR 151 bpm, steady HR 154 bpm, EF 1.525 W/bpm, aerobic decoupling 7.3%.
- Reference comparison (2026-05-14): pace 1.9% better/worse depending on sign, EF 2.8%, drift delta 0.9 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 90.0 min | measured |
| Basic | Distance | 12.28 km | measured |
| Basic | Average pace | 7.34 min/km | measured |
| Basic | Moving pace | 7.34 min/km | measured |
| Basic | Best pace | 6.64 min/km | measured |
| Basic | Elevation gain/loss | 5.0 m / 10.0 m | measured |
| Environment | Average / max temperature | 31.0 C / 33.0 C | measured |
| Heart rate | Average / max HR | 151 / 163 bpm | measured |
| Heart rate | HR zone distribution | Z1 0.8%, Z2 4.4%, Z3 68.1%, Z4 26.7%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 31.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 130.0 bpm | measured |
| Heart rate | Resting HR (profile) | 49.0 bpm | measured |
| Power | Average / max / normalized power | 234.0 W / 273.0 W / 234.0 W | measured |
| Power | Power zones | Z1 0.2%, Z2 75.1%, Z3 24.7%, Z4 0.0%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.30 W/kg / 5.2% CV | measured |
| Dynamics | Cadence / stride length | 168 spm / 0.808 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 280.1 ms / 79.1 mm / 9.80% | measured |
| Aerobic | Training effect / anaerobic TE | 3.4 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1500.0 mL (1.500 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed +1.9%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.525 W/bpm and steady speed per HR was 0.01474 m/s/bpm.
- Aerobic decoupling was 7.3% and power-HR decoupling was 8.6%.
- Time spent in Garmin HR zone 2 was 4.0 min; pace inside that zone was 7.26 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 38.2/100 with steady HR rise 6.4 bpm. 
- Rolling 3-run load proxy: 3325.2 kJ mechanical work and 9.7 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 103.0 J/m and average running economy was 103.0 W per m/s.
- Cadence stability was 2.5% CV and pace durability changed 0.3% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 31.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 26.7% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-05-23 - 12K Run

#### 1. Executive Summary

- 12.01 km in 83.5 min, average pace 6.96 min/km, steady pace 6.95 min/km.
- Average HR 153 bpm, steady HR 156 bpm, EF 1.564 W/bpm, aerobic decoupling 4.6%.
- Reference comparison (2026-05-21): pace 5.8% better/worse depending on sign, EF 2.6%, drift delta -2.7 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 83.5 min | measured |
| Basic | Distance | 12.01 km | measured |
| Basic | Average pace | 6.96 min/km | measured |
| Basic | Moving pace | 6.96 min/km | measured |
| Basic | Best pace | 5.25 min/km | measured |
| Basic | Elevation gain/loss | 8.0 m / 10.0 m | measured |
| Environment | Average / max temperature | 31.0 C / 33.0 C | measured |
| Heart rate | Average / max HR | 153 / 169 bpm | measured |
| Heart rate | HR zone distribution | Z1 0.8%, Z2 1.2%, Z3 69.3%, Z4 28.6%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 30.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 131.0 bpm | measured |
| Heart rate | Resting HR (profile) | 51.0 bpm | measured |
| Power | Average / max / normalized power | 246.0 W / 341.0 W / 248.0 W | measured |
| Power | Power zones | Z1 0.7%, Z2 41.5%, Z3 57.1%, Z4 0.7%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.46 W/kg / 8.7% CV | measured |
| Dynamics | Cadence / stride length | 168 spm / 0.854 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 277.4 ms / 81.4 mm / 9.55% | measured |
| Aerobic | Training effect / anaerobic TE | 3.7 / 0.0 | measured |
| Aerobic | Load focus | high_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1392.0 mL (1.392 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- The steady section stayed inside the usual aerobic-decoupling target, which supports durable easy-run metabolism for this duration.
- At roughly the same steady HR as the reference run, pace changed +5.8%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.564 W/bpm and steady speed per HR was 0.01542 m/s/bpm.
- Aerobic decoupling was 4.6% and power-HR decoupling was 11.6%.
- Time spent in Garmin HR zone 2 was 1.0 min; pace inside that zone was 7.48 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 82.0/100 with steady HR rise 3.1 bpm. 
- Rolling 3-run load proxy: 3517.6 kJ mechanical work and 10.2 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 102.7 J/m and average running economy was 102.7 W per m/s.
- Cadence stability was 6.7% CV and pace durability changed -0.5% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 31.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 28.6% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.
- This is a good candidate benchmark run; keep conditions similar and use it to judge whether aerobic efficiency is actually improving.

### 2026-05-28 - 90min Easy

#### 1. Executive Summary

- 12.24 km in 90.1 min, average pace 7.36 min/km, steady pace 7.37 min/km.
- Average HR 152 bpm, steady HR 156 bpm, EF 1.543 W/bpm, aerobic decoupling 7.9%.
- Reference comparison (2026-05-23): pace -5.7% better/worse depending on sign, EF -1.3%, drift delta 3.3 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 90.1 min | measured |
| Basic | Distance | 12.24 km | measured |
| Basic | Average pace | 7.36 min/km | measured |
| Basic | Moving pace | 7.37 min/km | measured |
| Basic | Best pace | 6.05 min/km | measured |
| Basic | Elevation gain/loss | 5.0 m / 5.0 m | measured |
| Environment | Average / max temperature | 32.0 C / 34.0 C | measured |
| Heart rate | Average / max HR | 152 / 167 bpm | measured |
| Heart rate | HR zone distribution | Z1 1.0%, Z2 5.6%, Z3 51.6%, Z4 41.8%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 27.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 133.0 bpm | measured |
| Heart rate | Resting HR (profile) | 54.0 bpm | measured |
| Power | Average / max / normalized power | 241.0 W / 304.0 W / 241.0 W | measured |
| Power | Power zones | Z1 0.0%, Z2 60.7%, Z3 39.2%, Z4 0.1%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.25 W/kg / 4.6% CV | measured |
| Dynamics | Cadence / stride length | 168 spm / 0.806 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 281.0 ms / 79.1 mm / 9.81% | measured |
| Aerobic | Training effect / anaerobic TE | 3.3 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1501.0 mL (1.501 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At roughly the same steady HR as the reference run, pace changed -5.7%, which is direct evidence about aerobic development.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.543 W/bpm and steady speed per HR was 0.01454 m/s/bpm.
- Aerobic decoupling was 7.9% and power-HR decoupling was 9.0%.
- Time spent in Garmin HR zone 2 was 5.1 min; pace inside that zone was 7.72 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 25.9/100 with steady HR rise 7.3 bpm. 
- Rolling 3-run load proxy: 3798.4 kJ mechanical work and 10.4 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 106.4 J/m and average running economy was 106.4 W per m/s.
- Cadence stability was 2.3% CV and pace durability changed -1.7% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 32.0 C, so heat strain is a realistic contributor to elevated HR and drift.
- 41.8% of the run sat in HR zone 4 by Garmin max-HR zones, which is high for a nominal easy run.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-06-02 - 75min Easy

#### 1. Executive Summary

- 10.26 km in 75.1 min, average pace 7.32 min/km, steady pace 7.32 min/km.
- Average HR 148 bpm, steady HR 152 bpm, EF 1.607 W/bpm, aerobic decoupling 6.4%.
- Reference comparison (2026-05-28): pace 0.7% better/worse depending on sign, EF 4.1%, drift delta -1.5 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 75.1 min | measured |
| Basic | Distance | 10.26 km | measured |
| Basic | Average pace | 7.32 min/km | measured |
| Basic | Moving pace | 7.33 min/km | measured |
| Basic | Best pace | 4.98 min/km | measured |
| Basic | Elevation gain/loss | 3.0 m / 8.0 m | measured |
| Environment | Average / max temperature | 30.0 C / 31.0 C | measured |
| Heart rate | Average / max HR | 148 / 159 bpm | measured |
| Heart rate | HR zone distribution | Z1 2.4%, Z2 4.3%, Z3 87.3%, Z4 6.0%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 32.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 123.0 bpm | measured |
| Heart rate | Resting HR (profile) | 58.0 bpm | measured |
| Power | Average / max / normalized power | 245.0 W / 366.0 W / 246.0 W | measured |
| Power | Power zones | Z1 0.1%, Z2 44.1%, Z3 55.6%, Z4 0.2%, Z5 0.1% | measured |
| Power | W/kg / stability | 3.30 W/kg / 5.7% CV | measured |
| Dynamics | Cadence / stride length | 164 spm / 0.828 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 285.7 ms / 81.6 mm / 9.86% | measured |
| Aerobic | Training effect / anaerobic TE | 3.1 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1251.0 mL (1.251 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At nearly the same steady pace as the reference run, HR cost changed +2.7%.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.607 W/bpm and steady speed per HR was 0.01503 m/s/bpm.
- Aerobic decoupling was 6.4% and power-HR decoupling was 6.7%.
- Time spent in Garmin HR zone 2 was 3.2 min; pace inside that zone was 7.78 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 60.2/100 with steady HR rise 4.4 bpm. 
- Rolling 3-run load proxy: 3639.4 kJ mechanical work and 10.1 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 107.6 J/m and average running economy was 107.6 W per m/s.
- Cadence stability was 2.4% CV and pace durability changed 0.1% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 30.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- If the goal is true zone-2 development, reduce pace until more of the run stays inside Garmin zone 2 instead of zone 3-4.
- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

### 2026-06-04 - 90min Easy

#### 1. Executive Summary

- 12.23 km in 90.0 min, average pace 7.36 min/km, steady pace 7.38 min/km.
- Average HR 144 bpm, steady HR 146 bpm, EF 1.657 W/bpm, aerobic decoupling 6.8%.
- Reference comparison (2026-06-02): pace -0.8% better/worse depending on sign, EF 3.1%, drift delta 0.4 pts.

#### 2. Key Metrics Table

| Category | Metric | Value | Status |
| --- | --- | --- | --- |
| Basic | Duration | 90.0 min | measured |
| Basic | Distance | 12.23 km | measured |
| Basic | Average pace | 7.36 min/km | measured |
| Basic | Moving pace | 7.37 min/km | measured |
| Basic | Best pace | 5.97 min/km | measured |
| Basic | Elevation gain/loss | 13.0 m / 8.0 m | measured |
| Environment | Average / max temperature | 30.0 C / 32.0 C | measured |
| Heart rate | Average / max HR | 144 / 155 bpm | measured |
| Heart rate | HR zone distribution | Z1 2.0%, Z2 11.4%, Z3 86.7%, Z4 0.0%, Z5 0.0% | measured |
| Heart rate | Recovery HR at 120 s | 30.0 bpm | measured |
| Heart rate | Settled HR at 120 s (post-stop) | 123.0 bpm | measured |
| Heart rate | Resting HR (profile) | 59.0 bpm | measured |
| Power | Average / max / normalized power | 243.0 W / 320.0 W / 244.0 W | measured |
| Power | Power zones | Z1 0.2%, Z2 53.5%, Z3 46.2%, Z4 0.1%, Z5 0.0% | measured |
| Power | W/kg / stability | 3.27 W/kg / 5.9% CV | measured |
| Dynamics | Cadence / stride length | 168 spm / 0.808 m | measured |
| Dynamics | Ground contact / vertical oscillation / vertical ratio | 281.1 ms / 79.2 mm / 9.80% | measured |
| Aerobic | Training effect / anaerobic TE | 3.3 / 0.0 | measured |
| Aerobic | Load focus | low_aerobic_estimated | estimated |
| Recovery | Body Battery / HRV / stress / recovery time | unavailable / unavailable / unavailable / unavailable | unavailable |
| Recovery | Estimated sweat loss | 1500.0 mL (1.500 L) | measured |
| Recovery | Sleep profile window | 21:30:00 to 04:30:00 | measured |

#### 3. Physiological Interpretation

- Cardiac drift rose above the ideal easy-run range, suggesting either excessive intensity for the day, heat strain, or incomplete recovery.
- At nearly the same steady pace as the reference run, HR cost changed +3.4%.

#### 4. Aerobic Efficiency Analysis

- Steady-state EF was 1.657 W/bpm and steady speed per HR was 0.01541 m/s/bpm.
- Aerobic decoupling was 6.8% and power-HR decoupling was 7.0%.
- Time spent in Garmin HR zone 2 was 10.2 min; pace inside that zone was 7.35 min/km.

#### 5. Fatigue/Recovery Assessment

- Fatigue resilience score: 57.9/100 with steady HR rise 3.3 bpm. 
- Rolling 3-run load proxy: 3715.3 kJ mechanical work and 9.7 summed aerobic training effect.
- Recovery-specific Garmin wellness metrics were not embedded in these FIT files, so under-recovery can only be inferred indirectly from drift, HR cost, and temperature context.

#### 6. Running Economy Notes

- Mechanical energy cost was 107.3 J/m and average running economy was 107.3 W per m/s.
- Cadence stability was 2.9% CV and pace durability changed 0.7% from early to late thirds.

#### 7. Concerns or Risks

- Average temperature was 30.0 C, so heat strain is a realistic contributor to elevated HR and drift.

#### 8. Recommendations

- Treat this run as heat-adjusted data: compare it mainly against other warm runs and prioritize hydration/cooling over pace targets.

## Suggested Visualization Ideas

- Matched-duration slope chart: steady pace and steady HR for 45 min, 50-55 min, and 60+ min buckets.
- Heat-context scatter: average temperature vs aerobic decoupling, colored by fatigue resilience score.
- Pace vs HR-cost chart: steady pace on one axis, steady HR/speed on the other, with point size driven by duration.
- Running-dynamics trend panel: stride length, stance time, and vertical ratio against steady pace.

## Important Limitations

- Garmin running power, training effect, and normalized power are vendor-derived and should be treated as consistent heuristics, not laboratory truth.
- This dataset is small and weather is warm in several runs, so trend interpretation should prioritize repeated conditions and matched durations.
- Recovery and wellness conclusions are indirect because the relevant wellness metrics are not present in these FIT exports.