# Seeded Test Faults

This file documents tests written before implementation, per `/new-feature`.

## test_weather_bad_is_one_hot_encoded_for_bad_weather

**File:** `tests/test_leakage.py`  
**Category:** Feature encoding validation

The new feature `weather_bad` must be one-hot encoded: 1 when weather is 'BAD', 0 otherwise. This test will fail until the feature is implemented in `src/features.py`.
