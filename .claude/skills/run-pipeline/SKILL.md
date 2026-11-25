---
name: run-pipeline
description: Run the entire pipeline of constructing a model and evaluating it
---

# Adding a feature: $ARGUMENTS
Do the steps in this order

1. Run make test. If anything fails, stop and show output. 
2. Run make all. If anything fails, stop and show output
3. Print one table of validation R2 and MAE for baseline_mean, baseline_persistence, ridge, and hgb in docs/REPORT.md. 
4. State whether ridge beats persistence on validation for R2 AND for MAE.
5. If the numbers changed but nothing in src/ explains it, tell the user. 