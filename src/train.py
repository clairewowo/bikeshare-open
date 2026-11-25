"""Stage 3: temporal split, fit, evaluate, write metrics.

Two baselines and two models, on purpose.

  baseline_mean         predict the 2011 average for every day
  baseline_persistence  predict yesterday's count (cnt_lag_1)
  ridge                 standardised linear model on the audited features
  hgb                   gradient-boosted trees on the same features

The mean baseline shows what "the distribution moved" costs. Persistence
is the baseline that actually matters: ridge's features are dominated by
lagged demand, so if it cannot beat "yesterday again" it has learned
nothing worth reporting. The booster is there because it fails, and the
reason it fails is the headline result.

Run: python -m src.train
"""
import json

import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import METRICS, PROCESSED, TARGET, TRAIN_END, VALID_END
from src.features import feature_columns


class PersistenceBaseline(BaseEstimator, RegressorMixin):
    """Predict a single lagged column unchanged. Nothing is fit."""

    def __init__(self, column: str = "cnt_lag_1"):
        self.column = column

    def fit(self, X, y=None):
        if self.column not in X.columns:
            raise ValueError(f"persistence baseline needs column {self.column!r}")
        return self

    def predict(self, X):
        return X[self.column].to_numpy(dtype=float)


MODELS = {
    "baseline_mean": DummyRegressor(strategy="mean"),
    "baseline_persistence": PersistenceBaseline("cnt_lag_1"),
    "ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    "hgb": HistGradientBoostingRegressor(random_state=0, max_iter=300),
}


def temporal_split(df: pd.DataFrame):
    """Split by date, never at random. A random split on a time series
    puts tomorrow in train and today in test."""
    train = df[df.dteday <= TRAIN_END]
    valid = df[(df.dteday > TRAIN_END) & (df.dteday <= VALID_END)]
    test = df[df.dteday > VALID_END]
    return train, valid, test


# Exercise 4: optional target transformations, OFF by default. Each maps a
# name to the past-only "anchor" column subtracted from cnt before fitting
# and added back to the prediction, so models learn the deviation from a
# level already known at prediction time instead of the level itself (which
# grew ~65% from 2011 to 2012, beyond anything a tree saw in training).
# Baselines are never transformed. The committed reports/metrics.json is
# always the untransformed pipeline; a transformed run writes its own file.
TARGET_TRANSFORMS = {"none": None, "diff_roll7": "cnt_roll_7"}
TRANSFORMED_MODELS = {"ridge", "hgb"}


def fit_and_score(transform: str = "none", splits=("valid", "test")) -> dict:
    anchor = TARGET_TRANSFORMS[transform]
    df = pd.read_parquet(PROCESSED)
    cols = feature_columns(df)
    train, valid, test = temporal_split(df)
    parts = {"valid": valid, "test": test}

    # The untransformed run must write the exact same metrics.json as before.
    results = {"target_transform": transform} if anchor else {}
    results |= {
        "n_features": len(cols),
        "features": cols,
        "n_train": len(train),
        "n_valid": len(valid),
        "n_test": len(test),
    }
    for name, model in MODELS.items():
        shift = anchor if (anchor and name in TRANSFORMED_MODELS) else None
        offset = (lambda X: X[shift]) if shift else (lambda X: 0.0)
        model.fit(train[cols], train[TARGET] - offset(train[cols]))
        results[name] = {}
        for split in splits:
            part = parts[split]
            pred = model.predict(part[cols]) + offset(part[cols])
            results[name][split] = {
                "r2": round(float(r2_score(part[TARGET], pred)), 4),
                "mae": round(float(mean_absolute_error(part[TARGET], pred)), 1),
            }
    return results


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--target-transform", choices=sorted(TARGET_TRANSFORMS), default="none")
    ap.add_argument("--valid-only", action="store_true",
                    help="score validation only; use while iterating so test stays untouched")
    ns = ap.parse_args()
    splits = ("valid",) if ns.valid_only else ("valid", "test")
    res = fit_and_score(ns.target_transform, splits)
    out = METRICS if ns.target_transform == "none" else METRICS.with_name(
        f"metrics_{ns.target_transform}.json")
    if ns.valid_only:
        out = out.with_name(out.stem + "_valid.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "features"}, indent=2))
