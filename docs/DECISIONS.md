# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- The agent did not see that 2011-03-10 was missing and identify casual and registered as leakage
- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.
- 2026-11-21 — Keep `cnt_roll_7_std` in the Exercises 1–2 pipeline because Ridge is the strongest model on validation and gains 0.0749 R² (0.6475 → 0.7224), with MAE 832.9 → 700.4. Its seven observations all precede the prediction date. Gradient boosting loses 0.1208 validation R² (0.2185 → 0.0977), so the gain is specific to Ridge. Both baselines are unchanged. The feature decision used validation only.
- 2026-11-21 — Added the weather-encoder and raw-column tests after reviewing the fault requirements. The weather test deliberately supplies an unknown label so a missing raise fails, and the schema test checks explicit classifications so a new numeric CSV field cannot pass verification silently. Updated `CLAUDE.md` with the corresponding rules.
