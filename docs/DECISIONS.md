# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.
- 2026-11-21: Add `weather_bad`: one-hot encoded indicator for BAD weather. Available at prediction time (weather measured same-day). Ridge validation R^2 0.6475 -> 0.6524 (+0.0049), below the 0.01 threshold and redundant with `weather_severity`, so the feature is not retained despite being leakage-safe.
- 2026-11-24: Restored the `ValueError` in `encode_weather` (seeded fault 3 had been left unrepaired) and added `test_unknown_weather_label_raises`. Removed `reports/` and `audit.jsonl` from `.gitignore` so `metrics.json` and `audit.jsonl` are committed.
- 2026-11-24: Exercise 4. Target `cnt - cnt_roll_7` (flag `--target-transform diff_roll7`, off by default) chosen on validation out of 4 transforms: HGB valid R^2 0.2185 -> 0.7147, Ridge 0.6475 -> 0.6569. Test touched once: HGB 0.6338 / MAE 831.5 vs persistence 0.5099 / 840.1. Defensible as detrending on a past-only level, but selected on validation and barely beats persistence on MAE; committed metrics.json stays untransformed.
- 2026-11-24: Test-set exposure during feature work. Commit 5ce03e4 put Ridge test R^2 (0.5833 -> 0.6155) in REPORT.md next to the validation delta. The keep/drop decision for `weather_bad` rests on validation alone (+0.0049 < 0.01), and the test column was removed from that comparison.
- 2026-11-24: Classify every raw column in `src/config.py` (`RAW_FEATURE_INPUTS`, `RAW_METADATA_COLS`) and add `test_all_raw_columns_are_classified`, so a column appended to the raw CSV fails `make test` instead of entering silently.
- 2026-11-24: CLAUDE.md updated: names the `/run-pipeline` skill, the Exercise 4 `--target-transform`/`--valid-only` flags, and the rule to classify new raw columns. No rule for `weather_bad`, since it was not kept.
- 2026-11-24: Exercise 5. Ridge is not recommended over persistence: on test it gains 0.07 R^2 (0.5833 vs 0.5099) but is 107 rides/day worse on MAE (947.1 vs 840.1). Its edge comes from fewer large misses, and it under-predicts by about 500 rides/day on validation.
