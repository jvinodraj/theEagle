# Stage 02 - Advanced

Goal: learn expert plan/state workflows for refactors, replacements, backends, and controlled state edits.

## Run Base Flow

```powershell
terraform init
terraform plan
terraform apply
```

## Exercise: Force Replace

```powershell
terraform plan -replace=local_file.config
```

Observe `-/+` behavior (replace).

## Exercise: Destroy Preview

```powershell
terraform plan -destroy
```

Use this before `terraform destroy` to avoid surprises.

## Exercise: State Inspection

```powershell
terraform state list
terraform state show local_file.config
terraform state pull
```

## Exercise: State Remove (Learning)

```powershell
terraform state rm local_file.report
terraform plan
```

Terraform will propose to recreate the removed address because config still declares it.

## Remote State Transition (Concept)

1. Create backend config from `backend.tf.example`.
2. Re-run:

```powershell
terraform init -migrate-state
```

This migrates local state to remote backend.

## Important Safety Rules

- Do not edit `terraform.tfstate` manually.
- Use state commands only with clear intent.
- Always review a plan before apply.
