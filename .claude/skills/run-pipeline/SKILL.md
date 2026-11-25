---
name: run-pipeline
description: Run the entire pipeline of constructing a model and evaluating it. Takes an optional target transform (none or diff_roll7).
---

# Running the pipeline with target transform: $ARGUMENTS
Treat an empty argument as `none`. Do the steps in this order

1. Run make test. If anything fails, stop and show output. 
2. Run make all. If anything fails, stop and show output
3. If the transform is not `none`, also run
   `python -m src.train --target-transform $ARGUMENTS --valid-only`.
   It must not change reports/metrics.json; check with `git diff --stat reports/metrics.json`.
4. Print one table, in the chat (do not edit REPORT.md), of validation R2 and MAE for baseline_mean, baseline_persistence, ridge, and hgb. Never print or quote test-set numbers.
5. State whether ridge beats persistence on validation for R2 AND for MAE.
6. If the numbers changed but nothing in src/ explains it, tell the user. 
