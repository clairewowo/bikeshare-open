# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.
- Add `weather_bad`: one-hot encoded indicator for BAD weather. Available at prediction time (weather measured same-day). Ridge validation R^2 0.6475 -> 0.6524 (+0.0049), below the 0.01 threshold and redundant with `weather_severity`, so the feature is not retained despite being leakage-safe.
- 2026-11-24: Restored the `ValueError` in `encode_weather` (seeded fault 3 had been left unrepaired) and added `test_unknown_weather_label_raises`. Removed `reports/` and `audit.jsonl` from `.gitignore` so `metrics.json` and `audit.jsonl` are committed.
