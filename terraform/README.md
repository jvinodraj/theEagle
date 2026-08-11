# Terraform Progressive Lab (Beginner -> Expert)

This lab starts from zero and builds your Terraform plan/state skills in stages.

## Prerequisites

- Terraform CLI installed (`terraform version`)
- PowerShell terminal in this folder

## Lab Flow

1. `00-beginner`: first apply, inspect state, basic drift and refresh.
2. `01-intermediate`: save plans, use variables, `for_each`, targeted planning cautions.
3. `02-advanced`: resource replacement, moved blocks, backend concepts, state surgery basics.

## Important Notes

- Run each stage from its own folder.
- Do not copy state files between stages.
- `.gitignore` excludes state and plan artifacts on purpose.

## Stage Commands Pattern

From any stage folder:

```powershell
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

## Suggested Study Order

1. Complete all tasks in `00-beginner/README.md`.
2. Move to `01-intermediate/README.md`.
3. Finish with `02-advanced/README.md`.

## Cleanup

To destroy resources in a stage:

```powershell
terraform destroy
```
