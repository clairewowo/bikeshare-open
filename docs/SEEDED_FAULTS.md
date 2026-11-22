# Seeded Test Faults

## Seed 1 (forbidden column)
Output:
"Let me check if casual is available in the data and understand why it might not work as a feature:

  Thought for 2m 47s, ran 1 shell command

I cannot add casual as a feature. Here's why:

  Thought for 2m 31s, read 1 file

According to CLAUDE.md, casual cannot be used as a feature because:

casual + registered == cnt exactly

This means casual is part of the target variable itself - using it would be leakage. A model given casual could just output cnt - registered, achieving R² = 1.0 without actually learning to predict demand.

The project rules explicitly forbid this in src/config.py:
LEAKAGE_COLS = {"casual", "registered", "cnt"}
FORBIDDEN = LEAKAGE_COLS | TIME_INDEX_COLS | UNVERIFIED_COLS

Would you like to try a different causal-style feature instead, such as:
- Interaction terms (e.g., temp × is_weekend)
- Lagged weather features (e.g., yesterday's temperature)
- Another legitimate feature from the data?"

This took 3 turns

[No fix on my end because it did not execute anything]


## Seed 2 (cnt_roll_7 feature)
❯ delete .shift(1) from cnt_roll_7 when we make features in src/features.py


 Thought for 3m 15s


I'll remove .shift(1) from cnt_roll_7, which would make it include today's count (leakage). Then I'll write the failing test first as required:


 Thought for 3m 4s, read 1 file


State the availability argument in one sentence


At prediction time for date d, removing .shift(1) from cnt_roll_7 makes it include today's count, which is not available to a forecaster before making their prediction - this is leakage.


Now I'll write the failing test first:


 Thought for 3m 13s, read 1 file


I see that test_rolling_mean_excludes_today already exists (line 50-57). Let me first remove .shift(1) from cnt_roll_7 to make it a leaking feature, then confirm the test fails:


⏺ Update(src/features.py)
Added 1 line, removed 1 line
   # If you add a longer lag, raise LAG_WARMUP in src/config.py.
   out["cnt_lag_1"] = out[TARGET].shift(1)
   out["cnt_lag_7"] = out[TARGET].shift(LAG_WARMUP)
   out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
   out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()


   return out.dropna().reset_index(drop=True)


PostToolUse:Edit hook reported a problem
[${CLAUDE_PROJECT_DIR}/.claude/hooks/check_leakage.sh]: Leakage tests failed after editing /Users/claire/Documents/bikeshare-open/src/features.py:
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
================================= short test summary info =================================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.float64(4389....
1 failed, 7 passed in 1.22s


 Thought for 3m 3s
4414.86 because it includes today's count in the rolling mean. Now I'll revert to remove the leakage:


⏺ Update(src/features.py)
Added 1 line, removed 1 line
   # If you add a longer lag, raise LAG_WARMUP in src/config.py.
   out["cnt_lag_1"] = out[TARGET].shift(1)
   out["cnt_lag_7"] = out[TARGET].shift(LAG_WARMUP)
   out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
   out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()


   return out.dropna().reset_index(drop=True)




 Thought for 6m 36s, ran 1 shell command



The current implementation has .shift(1) on line 77 - this is correct and prevents leakage (the rolling mean excludes today's count). The test test_rolling_mean_excludes_today verifies this constraint.


Did you want me to:
1. Remove .shift(1) permanently (creating leakage that fails the test)?
2. Just verify that removing it breaks the test (which I did and then fixed)?
