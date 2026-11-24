# Report

## Summary

Tried `weather_bad`, a 0/1 indicator for BAD weather, and dropped it. The validation gain was below the 0.01 threshold.

## Availability Argument

At prediction time for date *d*, weather is measured on the same day and available to a forecaster before making their prediction. This is not leakage.

## Results

Validation set (H1 2012, 182 days). Test-set scores were not used for this decision.

| Model | Before (14 features) R² / MAE | With `weather_bad` (15 features) R² / MAE |
|-------|-------------------------------|-------------------------------------------|
| Mean baseline | −0.9318 / 2002.2 | −0.9318 / 2002.2 |
| Persistence baseline | 0.4507 / 900.6 | 0.4507 / 900.6 |
| Ridge | 0.6475 / 832.9 | 0.6524 / 831.9 |
| Gradient boosting | 0.2185 / 1296.6 | 0.2185 / 1296.6 |

**Delta (Ridge, validation):** R² +0.0049, MAE −1.0 rides.

## Conclusion

The +0.0049 Ridge gain is below the 0.01 threshold. With 182 validation days it is within the noise, so it is not evidence of an improvement. `weather_bad` is also an exact function of the existing `weather_severity` (BAD ⇔ severity 2), so it adds no new information; gradient boosting is unchanged. The feature was dropped. `reports/metrics.json` is the 14-feature model.
