# Cardiovascular Drift Longitudinal Research Summary

## Study Question
Which field-derived variables most strongly explain cardiovascular drift during easy running, and is there evidence of longitudinal adaptation across the observed training block?

## Cohort and Methods
- Observation window: 2026-04-16 to 2026-05-23
- Easy runs analyzed for the primary outcome: 11
- Interval or threshold sessions used as antecedent exposure context: 5
- Strength sessions used as antecedent exposure context: 10
- Primary outcome: aerobic decoupling percentage from the easy-run steady section
- Statistical workflow: descriptive profiling, Spearman and Pearson correlation analysis, regularized regression, random-forest feature importance, linear trend testing, and early-versus-late non-parametric comparison

## Descriptive Findings
- Median aerobic drift was 7.12% across the easy-run timeline.
- Median efficiency factor was 1.536 W/bpm.
- 9/11 easy runs occurred at 30 C or hotter, indicating repeated thermal stress exposure.
- 3/11 easy runs exceeded the 8% high-drift threshold.

## Strongest Associations With Drift
- fatigue_resilience_score: Spearman r = -1.00 (negative), p = <0.001
- avg_running_cadence: Spearman r = 0.40 (positive), p = 0.218
- recovery_hr_120s_bpm: Spearman r = 0.36 (positive), p = 0.281
- thermal_strain_index: Spearman r = 0.35 (positive), p = 0.318
- steady_avg_power: Spearman r = -0.28 (negative), p = 0.401

## Regression and Feature Importance
- Leave-one-out Ridge model: n = 10, alpha = 0.5422, MAE = 1.77, RMSE = 2.10, R2 = -0.04.
- fatigue_resilience_score: standardized coefficient -1.78, random-forest importance 0.601.
- estimated_sweat_loss_l: standardized coefficient -0.05, random-forest importance 0.060.
- duration_min: standardized coefficient -0.05, random-forest importance 0.054.
- settled_hr_120s_bpm: standardized coefficient -0.10, random-forest importance 0.049.
- steady_avg_power: standardized coefficient +0.22, random-forest importance 0.049.

## Longitudinal Trend Analysis
- aerobic_drift_pct: slope +0.276 units per week, r = 0.24, p = 0.478
- steady_power_per_hr: slope +0.002 units per week, r = 0.09, p = 0.785
- recovery_hr_120s_bpm: slope +0.437 units per week, r = 0.28, p = 0.399
- settled_hr_120s_bpm: slope +0.253 units per week, r = 0.14, p = 0.686
- avg_running_cadence: slope +0.874 units per week, r = 0.76, p = 0.006
- fatigue_resilience_score: slope -3.278 units per week, r = -0.22, p = 0.525

## Early-versus-Late Adaptation Test
- aerobic_drift_pct: early median 5.40, late median 7.85, delta +2.45, p = 0.126
- steady_power_per_hr: early median 1.54, late median 1.53, delta -0.00, p = 0.784
- recovery_hr_120s_bpm: early median 29.00, late median 32.50, delta +3.50, p = 0.263
- steady_pace_min_per_km: early median 7.39, late median 7.35, delta -0.04, p = 0.356

## Physiological Interpretation
Cardiovascular drift in this dataset appears to be multi-factorial rather than explained by a single determinant. The most plausible mechanistic candidates are thermoregulatory strain, hydration stress proxy, incomplete autonomic recovery, and residual fatigue from preceding hard training. Variables linked to movement economy and external power production should be interpreted as modulators rather than sole drivers.

When higher drift co-occurs with slower recovery heart-rate kinetics, higher settled post-exercise heart rate, higher temperature, and recent hard-session exposure, the pattern is most compatible with incomplete recovery and elevated cardiovascular strain. When drift falls over time alongside stable or improving efficiency factor, the pattern is more consistent with aerobic adaptation.

## Limitations
- Sample size is small, so all inferential results are exploratory.
- Garmin-derived running power, training effect, and some threshold-related values are vendor estimates rather than laboratory measurements.
- Heat and hydration are proxied from field data rather than direct core temperature or fluid-balance testing.
- Causal inference is not justified from this observational design alone.

## Practical Endurance-Science Conclusion
The working interpretation is that cardiovascular drift is most likely amplified by the interaction of heat exposure, sweat-loss burden, incomplete recovery kinetics, and recent hard training load. Longitudinal adaptation should be monitored primarily through repeated reductions in aerobic decoupling at matched durations, together with stable or improving efficiency factor and improved post-run heart-rate recovery.

## Output Artifacts
- Poster-style figure panel: C:\Users\A717631\repo\theEagle\reports\easy\cardiovascular_drift_research_panels.png
- Markdown summary: C:\Users\A717631\repo\theEagle\reports\easy\cardiovascular_drift_research_summary.md
