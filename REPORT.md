# Report

## Results

Temporal split: train 2011 (348 days), validation H1 2012 (182 days), test H2 2012 (184 days). "Before" is the committed pipeline (`reports/metrics.json`, 14 features). "After" adds my Exercise 1 feature `weather_bad` (15 features; numbers from `make all` at commit `aeed231`). Test scores are reported here once and were not used to choose features.

| Model | Feature set | Valid R² | Valid MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| baseline_mean | Before | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| baseline_persistence | Before | 0.4507 | 900.6 | 0.5099 | 840.1 |
| ridge | Before | 0.6475 | 832.9 | 0.5833 | 947.1 |
| hgb | Before | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| baseline_mean | After | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| baseline_persistence | After | 0.4507 | 900.6 | 0.5099 | 840.1 |
| ridge | After | 0.6524 | 831.9 | 0.6155 | 905.2 |
| hgb | After | 0.2185 | 1296.6 | -0.4975 | 1972.6 |

**Feature (Exercise 1): `weather_bad`**, a 0/1 indicator for BAD weather.
- *Availability argument:* weather on day *d* is measured the same day and is available to a forecaster at prediction time, so this is not leakage.
- *Validation delta:* Ridge R² +0.0049 (0.6475 → 0.6524), MAE −1.0 rides. Gradient boosting is unchanged, because `weather_bad` is an exact function of the existing `weather_severity` (BAD ⇔ severity 2).
- *Decision:* dropped. The gain is below the 0.01 threshold, and with 182 validation days it is within the noise.
- *Caveat:* an earlier version of this report (commit `5ce03e4`) also showed the feature's test-set R². The decision rests on validation alone; see `docs/DECISIONS.md`.

## Headline finding

A model given `casual` and `registered` scores R² 1.000, and that score is invalid: those two columns sum to `cnt` exactly. Under a temporal split (train 2011, test H2 2012):
- The mean baseline scores test R² -2.1441, because ridership grew and the 2011 average no longer describes 2012.
- Ridge reaches 0.5833 against a persistence ("yesterday's count") baseline of 0.5099. It beats persistence by 0.07 R² but loses to it on MAE (947.1 vs 840.1 rides).
- Gradient boosting is negative (-0.4975, MAE 1972.6) because a tree cannot predict counts above the range it saw in 2011, but it still beats the mean baseline by 1.65 R².

So the honest result is that Ridge only narrowly beats persistence, and gradient boosting fails to extrapolate a growing trend. My feature, `weather_bad`, raised Ridge's validation R² by only 0.0049 and left gradient boosting unchanged, so I did not keep it.

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

Ridge is not worth deploying over "yesterday again". On test it beats persistence by 0.07 R² (0.5833 vs 0.5099) but is 107 rides/day worse on MAE (947.1 vs 840.1). R² squares errors, so Ridge's edge comes from a few large misses. On validation, Ridge misses by more than 2,000 rides on 7 days against persistence's 18, and its worst day is 3,536 off vs 5,597. On ordinary days persistence is closer: median absolute error 639 vs 726 on validation, and Ridge is closer on only 86 of 182 validation days. Ridge also under-predicts by about 500 rides/day on the H1 2012 validation set, because it learned 2011 levels. Its MAE advantage on validation (832.9 vs 900.6) reversed on test, which is consistent with, though not proof of, that bias growing further from 2011. For a 14-feature pipeline that loses to a one-line rule on the everyday metric, the improvement is not worth it. The case would change if large misses cost much more than small ones.

## Attribution

Model: qwen3.5:9b via Ollama (built as `bikeshare-coder`, 64k context) for Exercises 1–2. I then switched to Claude Code with Claude Opus 5.5 (hosted) for Exercises 3–5 and the final fixes, because I was running out of time.

**Decisions that were mine** (each has a line in `docs/DECISIONS.md`)
- Keep the starter's choices on what to predict, what counts as leakage, how to split, and which baselines to report.
- Add `weather_bad`, then drop it as below the 0.01 threshold.
- Accept the Exercise 4 transform `cnt − cnt_roll_7`. It was proposed by the agent; I judged it only partly defensible.
- Judge that Ridge is not worth deploying over persistence (Exercise 5).
