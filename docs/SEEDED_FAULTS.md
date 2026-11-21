# MA6 Exercise 2 fault evidence

Each code fault was made in a separate disposable checkout of the verified feature commit. For each fault I ran the named test, then ran the course's unchanged `PostToolUse` hook with the matching `Edit` event payload. The logs below are the actual test stdout and hook stderr. Pytest exited 1 and the hook exited 2 for each fault. The local Qwen agent received the hook output and a targeted request to repair the fault.

## Exercise 1 test-first evidence

The July 11 test was written before adding `cnt_roll_7_std`. The seven strictly earlier counts are 6043, 4665, 4629, 4592, 4040, 5336, and 4881. Their sample standard deviation is 640.0754419820928. The failing run ended with:

```text
                and any(isinstance(x, slice) for x in casted_key)
            ):
                raise InvalidIndexError(key) from err
>           raise KeyError(key) from err
E           KeyError: 'cnt_roll_7_std'

.venv/lib/python3.12/site-packages/pandas/core/indexes/base.py:3648: KeyError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_volatility_uses_strictly_prior_calendar_days
1 failed, 8 deselected in 0.42s
```

## 1. Forbidden model input

`casual` bypassed the filter and reintroduced a same-day component of the target.

```diff
diff --git a/src/features.py b/src/features.py
index e2a3eb2..00acef6 100644
--- a/src/features.py
+++ b/src/features.py
@@ -87,7 +87,7 @@ def build_features(df: pd.DataFrame) -> pd.DataFrame:
 def feature_columns(df: pd.DataFrame) -> list[str]:
     """Numeric columns that are safe to feed the model."""
     numeric = df.select_dtypes(include="number").columns
-    return [c for c in numeric if c not in FORBIDDEN]
+    return [c for c in numeric if c not in FORBIDDEN] + ["casual"]


 if __name__ == "__main__":
```

Red test:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
__________________________ test_no_forbidden_features __________________________
tests/test_leakage.py:31: in test_no_forbidden_features
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E   AssertionError: forbidden columns in feature set: {'casual'}
E   assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'cnt_roll_7_std', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed in 0.52s
```

Hook stderr:

```text
Leakage tests failed after editing src/features.py:
feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7 cnt_roll_7_std
0   2011-01-10     10.0  WINTER  ...     1...857     886.694316
713 2012-12-31    731.0  WINTER  ...      920.0  1531.428571     887.135250

[714 rows x 29 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'cnt_roll_7_std', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests/test_leakage.py:31: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 8 passed in 0.35s
```

Repair observation: The local agent cleared the failure in one editing turn. An independent rerun verified the repair.

```text
.........                                                                [100%]
9 passed in 0.63s
```

## 2. Unshifted rolling mean

The rolling window included the prediction day itself.

```diff
diff --git a/src/features.py b/src/features.py
index e2a3eb2..3bb90af 100644
--- a/src/features.py
+++ b/src/features.py
@@ -73,7 +73,7 @@ def build_features(df: pd.DataFrame) -> pd.DataFrame:
     # If you add a longer lag, raise LAG_WARMUP in src/config.py.
     out["cnt_lag_1"] = out[TARGET].shift(1)
     out["cnt_lag_7"] = out[TARGET].shift(LAG_WARMUP)
-    out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+    out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
     out["cnt_roll_7_std"] = (
         out[TARGET]
         .shift(1)  # shift to exclude today, then aggregate on prior values
```

Red test:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_rolling_mean_excludes_today _______________________
tests/test_leakage.py:57: in test_rolling_mean_excludes_today
    assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E   assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E
E     comparison failed
E     Obtained: 4389.0
E     Expected: 4414.857142857143 ± 0.00441486
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed in 0.52s
```

Hook stderr:

```text
Leakage tests failed after editing src/features.py:
[714 rows x 29 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests/test_leakage.py:57: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 8 passed in 0.35s
```

Repair observation: The local agent cleared the failure in one editing turn. An independent rerun verified the repair.

```text
.........                                                                [100%]
9 passed in 0.28s
```

## 3. Missing weather error

An unknown weather label could silently become a missing value and be dropped.

```diff
diff --git a/src/features.py b/src/features.py
index e2a3eb2..2023d67 100644
--- a/src/features.py
+++ b/src/features.py
@@ -26,8 +26,6 @@ def encode_weather(series: pd.Series) -> pd.Series:
     """
     known = series.dropna()
     unknown = set(known.unique()) - set(WEATHER_ORDER)
-    if unknown:
-        raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
     return series.map(WEATHER_ORDER).astype(float)
```

Red test:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_unknown_weather_label_fails_before_row_can_disappear ___________
tests/test_leakage.py:68: in test_unknown_weather_label_fails_before_row_can_disappear
    with pytest.raises(ValueError, match="unmapped weather labels:.*FUTURE_LABEL"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_unknown_weather_label_fails_before_row_can_disappear
1 failed in 0.48s
```

Hook stderr:

```text
Leakage tests failed after editing src/features.py:
......F..                                                                [100%]
=================================== FAILURES ===================================
__________ test_unknown_weather_label_fails_before_row_can_disappear ___________

    def test_unknown_weather_label_fails_before_row_can_disappear():
>       with pytest.raises(ValueError, match="unmapped weather labels:.*FUTURE_LABEL"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:68: Failed
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_unknown_weather_label_fails_before_row_can_disappear
1 failed, 8 passed in 0.34s
```

Repair observation: The local agent cleared the failure in one editing turn. An independent rerun verified the repair.

```text
.........                                                                [100%]
9 passed in 0.27s
```

## 4. Bash copy into raw data

Ran `cp` from Bash on the fourth disposable checkout to overwrite only its raw CSV with a synthetic copy that added an unclassified numeric column. The configured hook listens to `Edit|Write`, so a `Bash` event is outside its matcher. The copy succeeded, and the independent raw-schema test rejected the added column. The checksum verified restoration.

```text
Before SHA-256: a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc
Bash cp exit: 0
After SHA-256:  cbe24c25ca368042deb646f940e4a30040938e040e184238a0c2ae40f2dcdff0
PostToolUse matchers: ['Edit|Write']. Bash matches: [].
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________ test_all_raw_columns_are_classified ______________________
tests/test_contract.py:31: in test_all_raw_columns_are_classified
    assert not unknown, f"unclassified raw columns: {sorted(unknown)}"
E   AssertionError: unclassified raw columns: ['synthetic_unclassified']
E   assert not {'synthetic_unclassified'}
=========================== short test summary info ============================
FAILED tests/test_contract.py::test_all_raw_columns_are_classified - Assertio...
1 failed in 1.73s
Restored SHA-256: a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc
```

A read-only raw-data directory for the agent process would prevent this copy. A `make data` check against a pinned checksum would catch the change even if the replacement preserved the column schema, while the schema test catches this specific added column. No extra hook was added.
