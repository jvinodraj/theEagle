# How to Download and Place FIT Files

This guide explains how to export FIT files from Garmin Connect and place them into the correct project folders.

## 1. Download FIT Files from Garmin Connect (Web)

1. Sign in to Garmin Connect: https://connect.garmin.com
2. Open Activities.
3. Select one activity.
4. Click the gear icon (top right of activity details).
5. Choose Export Original.
6. Save the downloaded `.zip` or `.fit` file locally.

Notes:
- Export Original usually contains the original FIT payload.
- If Garmin gives you a `.zip`, extract it and keep the `.fit` file.

## 2. Optional Bulk Export

For larger backups:

1. In Garmin Connect web, go to Account Settings.
2. Use Export Your Data.
3. Download the archive when Garmin sends it.
4. Extract the archive and collect activity `.fit` files.

## 3. Map Each FIT File to a Workout Category

Use these folders in this repo:

- `data/activities/easy/raw`
- `data/activities/interval/raw`
- `data/activities/strength/raw`
- `data/activities/general/raw`

Recommended mapping:

- Easy/recovery/base runs -> `data/activities/easy/raw`
- Intervals/tempo/threshold/speed -> `data/activities/interval/raw`
- Strength or mixed strength-endurance sessions -> `data/activities/strength/raw`
- Anything uncategorized -> `data/activities/general/raw`

## 4. Suggested Naming Convention

Use a consistent filename format:

`YYYY-MM-DD_<session-type>.fit`

Examples:

- `2026-05-18_easy.fit`
- `2026-05-19_interval.fit`
- `2026-05-20_strength.fit`

## 5. Validate Before Parsing

Checklist:

1. File extension is `.fit`.
2. File is in exactly one raw category folder.
3. Filename is descriptive and date-prefixed.
4. You can open/inspect file metadata in Garmin or a FIT viewer if needed.

## 6. Next Commands

After placing files:

```powershell
uv run python main.py parse --category all
uv run python main.py easy-report
uv run python main.py interval-report
uv run python main.py strength-report
```

For full workflow details, see [How to Run](how-to-run.md).
