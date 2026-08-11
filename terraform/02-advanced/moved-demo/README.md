# Moved Block Mini-Lab

Goal: refactor a resource name without destroy/recreate.

## Steps

1. Copy `before.tf` to `main.tf`.
2. Run:

```powershell
terraform init
terraform apply
```

3. Replace `main.tf` with `after.tf`.
4. Run:

```powershell
terraform plan
```

Expected: Terraform shows address move, not a full recreate.

This is safer than deleting and recreating when only the resource address changed.
