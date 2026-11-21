# Bikeshare demand forecasting

## Results

Exercise 1 adds `cnt_roll_7_std`, the sample standard deviation of ridership across the seven calendar days before the forecast date. The new test uses July 11, 2011 and the counts from July 4–10. Both runs train on the same 348 usable days from 2011 and score on the same 182 validation days in January–June 2012.

| Model | Feature set | Validation R² | Validation MAE (rides) |
| --- | --- | ---: | ---: |
| Mean baseline | Before | −0.9318 | 2002.2 |
| Mean baseline | After | −0.9318 | 2002.2 |
| Persistence baseline | Before | 0.4507 | 900.6 |
| Persistence baseline | After | 0.4507 | 900.6 |
| Ridge | Before | 0.6475 | 832.9 |
| Ridge | After | 0.7224 | 700.4 |
| Gradient boosting | Before | 0.2185 | 1296.6 |
| Gradient boosting | After | 0.0977 | 1381.6 |

This comparison uses validation only. Add the held-out test scores after the remaining choices are locked.

## Headline finding

Weekly volatility helped Ridge on validation, raising R² by 0.0749 and reducing MAE by 132.5 rides. The same feature lowered gradient boosting R² by 0.1208. Both baselines stayed fixed, so we kept the feature for the stronger Ridge model. Exercise 2 checks and the hook outputs are in [the fault log](docs/SEEDED_FAULTS.md).

## Exercise 4: target transformation

Pending group work.

## Exercise 5: ridge vs persistence

Pending group work.

## Attribution

Local `qwen3.5:9b` via Ollama, using the course’s `bikeshare-coder` model with a 65,536-token context. The Exercises 1–2 runs used the same model. Codex helped write and run the tests, reviewed the proposed feature edit, and measured the validation results. The local agent proposed the feature implementation through `/new-feature`; Codex applied the reviewed edit when the restricted process could not create its temporary file.
