# Report

## Results (Exercise 1)

Tried `weather_bad`, a 0/1 indicator for BAD weather, and dropped it. The validation gain was below the 0.01 threshold.

### Availability Argument

At prediction time for date *d*, weather is measured on the same day and available to a forecaster before making their prediction. This is not leakage.

### Results

Validation set (H1 2012, 182 days). Test-set scores were not used for this decision.

| Model | Before (14 features) R² / MAE | With `weather_bad` (15 features) R² / MAE |
|-------|-------------------------------|-------------------------------------------|
| Mean baseline | −0.9318 / 2002.2 | −0.9318 / 2002.2 |
| Persistence baseline | 0.4507 / 900.6 | 0.4507 / 900.6 |
| Ridge | 0.6475 / 832.9 | 0.6524 / 831.9 |
| Gradient boosting | 0.2185 / 1296.6 | 0.2185 / 1296.6 |

**Delta (Ridge, validation):** R² +0.0049, MAE −1.0 rides.

### Conclusion

The +0.0049 Ridge gain is below the 0.01 threshold. With 182 validation days it is within the noise, so it is not evidence of an improvement. `weather_bad` is also an exact function of the existing `weather_severity` (BAD ⇔ severity 2), so it adds no new information; gradient boosting is unchanged. The feature was dropped. `reports/metrics.json` is the 14-feature model.

## Exercise 4: target transformation

**Problem.** Gradient boosting scores validation R² 0.2185, against Ridge's 0.6475, because trees cannot predict outside the target range they were trained on. The 2011 training mean is 3,493 rides/day and the H1-2012 validation mean is 5,152. 71 of the 182 validation days exceed the highest count in training (6,043).

**What was tried (validation only).** Four target transformations were fit to Ridge and gradient boosting, with predictions converted back to rides before scoring. The baselines are untransformed.

| Target | Ridge R² / MAE | Gradient boosting R² / MAE |
|---|---|---|
| `cnt` (untransformed) | 0.6475 / 832.9 | 0.2185 / 1296.6 |
| `log1p(cnt)` | 0.1042 / 1180.8 | 0.1352 / 1363.6 |
| `cnt − cnt_lag_1` | 0.6475 / 832.4 | 0.6079 / 834.3 |
| `cnt − cnt_roll_7` | 0.6569 / 819.3 | 0.7147 / 731.2 |
| `cnt / cnt_roll_7` | 0.3881 / 1092.9 | 0.7454 / 687.2 |

Persistence baseline, validation: 0.4507 / 900.6.

**Choice, made before the test set was touched: `cnt − cnt_roll_7`** (`python -m src.train --target-transform diff_roll7`). Moving-block bootstrap on validation (7-day blocks, 2,000 resamples) gives these 95% intervals:
- Gradient boosting on this target beats untransformed Ridge by +0.078 R² [+0.015, +0.152].
- It beats Ridge on the same target by +0.067 [+0.007, +0.136].
- The ratio target's extra +0.033 for gradient boosting has an interval that includes 0 [−0.012, +0.080], and it drops Ridge to 0.39, so it was not chosen.

**Test set, touched once at the end** (2026-11-24, one run, `reports/metrics_diff_roll7.json`):

| Model | Test R² | Test MAE |
|---|---|---|
| Mean baseline | −2.1441 | 2847.7 |
| Persistence baseline | 0.5099 | 840.1 |
| Ridge, untransformed (`reports/metrics.json`) | 0.5833 | 947.1 |
| Gradient boosting, untransformed (`reports/metrics.json`) | −0.4975 | 1972.6 |
| Ridge, `cnt − cnt_roll_7` | 0.5910 | 933.6 |
| Gradient boosting, `cnt − cnt_roll_7` | 0.6338 | 831.5 |

**Is it defensible?** Partly.
- **For:** `cnt_roll_7` is shifted, past-only and already a tested feature, so the transform adds no leakage. It is chosen to fix the specific failure diagnosed above (predicting levels never seen in training), and it is applied to both models and compared on the same target, not given to the tree model alone.
- **Against:**
  - Five candidates were compared on 182 validation days, so the winner is partly selected.
  - On test, transformed gradient boosting beats persistence by only 8.6 rides of MAE (831.5 vs 840.1). Most of what the transformed model "knows" is last week's level, which is close to what persistence already uses.
  - This makes the tree model competitive with Ridge; it does not show either model clearly beats "yesterday again."

`reports/metrics.json` remains the untransformed pipeline; the transform is behind a flag that defaults to off.

## Exercise 5: Ridge vs Persistence
Ridge is not worth deploying over "yesterday again" because the 0.07 advantage in R2 is driven by outliers (squaring an error weights large errors heavier). Ridge also consistently underestimates in 2011 (about −500 rides/ day). It is a more complex model as well and the pipeline is not worth the improvement. 

## Attribution
I used the 16 GB ollama model for the first 2 exercises and after exercise 3, used the NRP hosted version of Qwen
