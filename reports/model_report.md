# Model Performance Report

## Overview
This report documents the performance and feature importance of the initial running efficiency prediction model built using linear regression. The goal of this model is to identify the most effective combination of running metrics to predict running efficiency.

## Model Performance
- **Root Mean Squared Error (RMSE):** 0.28
    - Interpretation: On average, the model’s predictions are off by 0.28 min/km (~17 seconds/km).
- **R-squared (R²):** 0.96
    - Interpretation: The model explains 96% of the variance in running efficiency, demonstrating high accuracy and strong predictive capability.

## Feature Importance
This section shows the contribution of each feature to the model’s predictions:

| Feature           | Importance |
|------------------|------------|
| cadence_to_speed  | 0.341020   |
| power             | 0.036296   |
| power_to_weight   | 0.000504   |
| heart_rate        | -0.011036  |
| cadence           | -0.290619  |

**Interpretation:**
- **cadence_to_speed:** Most important predictor of running efficiency.
- **power:** Has some influence on running efficiency but is less impactful.
- **power_to_weight:** Minimal impact, may be considered for removal.
- **heart_rate:** Almost no influence on pace prediction.
- **cadence:** Negative impact, suggesting inefficient stride rate without proper speed alignment.

## Next Steps
- **Feature Engineering:** Consider refining or creating new features based on domain knowledge.
- **Model Tuning:** Explore regularization techniques or advanced models like Random Forest or Gradient Boosting.
- **Cross-validation:** Validate the model on different data splits for robustness.
- **Interpretability:** Visualize feature relationships and model predictions.

## Conclusion
This model provides a solid baseline with high accuracy and interpretable feature importance. Further experimentation can help refine feature selection and improve predictive performance.

