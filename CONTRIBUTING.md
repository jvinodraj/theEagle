# Contributing

## Development Environment

1. Install dependencies with `uv sync`.
2. For notebooks, ensure dev dependencies are present: `uv sync --dev`.
3. Run commands with `uv run ...`.

## Repository Conventions

1. Reusable code belongs in `src/`.
2. Operational/ad-hoc scripts belong in `scripts/`.
3. Tests belong in `tests/unit` or `tests/integration`.
4. Documentation belongs in `docs/`.
5. Do not add new Python scripts at repository root.

## Data and Reports

- Input FIT files: `data/activities/<category>/raw`
- Parsed outputs: `data/activities/<category>/processed`
- Reports: `reports/easy`, `reports/interval`, `reports/strength`

## Quality Checklist (Before Commit)

1. Run the relevant command path from `README.md`.
2. Verify notebook/model dependencies are pinned in `pyproject.toml`.
3. Keep generated artifacts/logs out of version control.
4. Update docs when behavior or folder usage changes.

## Documentation

- Usage guide: `docs/how-to-run.md`
- Structure standard: `docs/PROJECT_STRUCTURE.md`
