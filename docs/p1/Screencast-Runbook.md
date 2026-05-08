# Screencast Runbook

Target Duration: 8 to 10 minutes
Goal: Show that the accelerator is real, modular, production-aware, and ready for pilot adoption.

## 1) Pre-Demo Setup Checklist

- Ensure environment variables are available:
  - PBI_TENANT_ID
  - PBI_CLIENT_ID
  - PBI_SECRET
- Verify config file exists: config/migration.json
- Keep one prepared mapping workbook in data/ with a few Select=YES rows.
- Keep logs/ visible in file explorer pane.
- Open Power BI/Fabric portal in browser (optional) for quick cross-check.

## 2) Storyline You Should Follow

- Start with the business pain: manual migration does not scale.
- Position this project as an automation framework with governance built in.
- Demonstrate one complete lifecycle on a small sample.
- End with realistic roadmap and pilot ask.

## 3) Minute-by-Minute Talk Track

### Minute 0-1: Project framing

Say:
- "This accelerator standardizes PBIRS to Fabric migration with action-based execution."
- "It separates configuration, credentials, and module logic for maintainability."

Show:
- Run-Migration.ps1
- modules/ folder layout
- config/migration.json

### Minute 1-3: Inventory phase

Run:

```powershell
.\Run-Migration.ps1 -Action Inventory
```

Say:
- "Inventory discovers PBIRS artifacts and creates a mapping workbook."
- "This gives us a controlled human validation gate before migration."

Show:
- data/PBIRS_Migration_Mapping.xlsx
- Mention Select=YES filtering.

### Minute 3-5: Download + Convert phase

Run:

```powershell
.\Run-Migration.ps1 -Action Download
.\Run-Migration.ps1 -Action Convert
```

Say:
- "Download handles larger files with streaming and retry logic."
- "Convert optionally transforms PBIX into PBIP project structure for source control readiness."

Show:
- downloads/ sample outputs
- powerbi/ generated PBIP folder structure

### Minute 5-7: Publish phase

Run:

```powershell
.\Run-Migration.ps1 -Action Publish
```

Say:
- "Publish uses SPN authentication and supports large-file upload strategy."
- "It selects upload mechanism based on configurable size thresholds."

Show:
- logs/ latest Publish_*.log
- Highlight import status progression in logs.

### Minute 7-8: Governance checks

Run:

```powershell
.\Run-Migration.ps1 -Action ListGroups
.\Run-Migration.ps1 -Action ListReports -WorkspaceName "<Workspace>"
.\Run-Migration.ps1 -Action ListDatasources -WorkspaceName "<Workspace>" -DatasetName "<Dataset>"
.\Run-Migration.ps1 -Action ListGateways
```

Say:
- "These checks provide migration confidence and post-migration observability."
- "We can quickly identify data source and gateway dependencies."

### Minute 8-10: Close with credibility

Say:
- "We have a working baseline, and we are transparent about what is planned next."
- "Next sprint should align docs with current actions and close missing action gaps."
- "Requesting approval for a controlled pilot workspace."

## 4) Leadership Questions You Should Be Ready For

Q: Is this secure?
A: Secrets are externalized to environment variables; no repository secret storage.

Q: Can this handle large enterprise reports?
A: Yes, download and upload paths include large-file handling with retry logic.

Q: What are current limitations?
A: A few roadmap actions are documented but not yet wired in the orchestrator.

Q: What is required for pilot?
A: SPN permissions, one target workspace, and a validated mapping sheet.

## 5) What Not To Do During Screencast

- Do not run with full production mapping workbook.
- Do not expose actual secret values or tenant identifiers.
- Do not spend time debugging live issues; use prepared sample rows.
- Do not claim roadmap items are already GA.

## 6) Optional Strong Finish (30-second summary)

"This accelerator turns migration from an ad-hoc manual effort into a governed engineering workflow. We already have real execution paths for inventory, download, publish, and governance inspection. With one focused sprint, we can close scope gaps and operationalize this as a repeatable enterprise migration product."
