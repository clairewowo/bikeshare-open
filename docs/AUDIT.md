### Audit against Teammate's repo

Teammate repo link: https://github.com/clairewowo/bikeshare-open/commits/kevin/exercises-1-2/. Note, this is a branch of my own repo because he didn't know we had to make our own repos. I used his latest commit on the kevin/exercises-1-2 branch and cloned it, so it is about the same as cloning a different repo. 


What the auditor found

All five of its checks passed:

1. Target leakage – pass. The model gets 15 features: temp, atemp, hum, windspeed, dayofweek, is_weekend, is_holiday, is_workday, month_sin, month_cos, weather_severity, cnt_lag_1, cnt_lag_7, cnt_roll_7 and cnt_roll_7_std. None is casual, registered, cnt, cnt_2d_bfr or a time index. The highest correlation with cnt is 0.849 (cnt_roll_7), from a lagged feature, so it's expected and not an identity.
2. Time order – pass. Every rolling feature shifts by one day before it aggregates. Kevin's new cnt_roll_7_std matched a recomputation from the 7 prior calendar days on all 714 rows. The split is by date: 348 train / 182 validation / 184 test. The scaler is fit on train only.
3. Calendar gaps – pass. The missing day, 2011-03-10, becomes an empty row before any lag is built.
4. Silent row loss – pass. 728 raw rows become 714. The 14 dropped are exactly the first-week warm-up and the 7 days after the gap.
5. Baselines – pass. Every model row in REPORT.md sits next to both the mean and persistence baselines.

I agree with these findings. 

Since these all passed here is what it ran:

```bash
$ cd /tmp/kb-pinned2 && source .venv/bin/activate && make all; make test
python -m src.ingest
OK ingest: 728 rows, 2011-01-03 -> 2012-12-31
python -m src.features
OK features: 714 rows, 15 features -> features.parquet
  temp, atemp, hum, windspeed, dayofweek, is_weekend, is_holiday, is_workday, month_sin, month_cos, weather_severity, cnt_lag_1, cnt_lag_7, cnt_roll_7, cnt_roll_7_std
python -m src.train
  "n_train": 348, "n_valid": 182, "n_test": 184,
  baseline_mean         valid: r2 -0.9318, mae 2002.2
  baseline_persistence  valid: r2  0.4507, mae  900.6
  ridge                 valid: r2  0.7224, mae  700.4
  hgb                   valid: r2  0.0977, mae 1381.6
EXIT=0
python -m pytest tests/ -q
.................                                                        [100%]
17 passed in 1.07s
```


