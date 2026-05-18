# Project Structure Standard

This project follows a Python `src` layout with category-based data/report separation.

## Recommended Industrial Structure

```text
theEagle/
  src/                     # Application/library source code
  tests/                   # Automated tests (unit/integration)
  scripts/                 # Operator and ad-hoc runnable scripts
  docs/                    # User and engineering documentation
  configs/                 # Environment/config templates
  notebooks/               # Exploratory notebooks
  data/                    # Raw/processed datasets (local)
  reports/                 # Generated analytics reports
  models/                  # Trained model artifacts (if any)
  pyproject.toml           # Build/dependency metadata
  uv.lock                  # Reproducible dependency lockfile
```

## Current Implementation in This Repo

- Core code is under `src/`.
- Data is organized under `data/activities/<category>/raw|processed`.
- Reports are separated by type under `reports/easy|interval|strength`.
- Notebooks are under `notebooks/`.
- Root-level one-off scripts currently exist for historical analysis workflows.

## Migration Rules for New Work

1. New reusable code must go in `src/`.
2. New one-off runnable programs must go in `scripts/`.
3. New tests must go in `tests/unit` or `tests/integration`.
4. New docs should go in `docs/` and be linked from `README.md`.
5. Generated logs and temporary outputs should not be committed.

## Legacy Root Scripts Policy

Existing root scripts are kept for compatibility. Do not add new root scripts.
When touching a legacy root script, prefer moving/refactoring logic into `src/` and keeping a thin wrapper in `scripts/`.
