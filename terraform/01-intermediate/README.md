# Stage 01 - Intermediate

Goal: make plan review reproducible and understand how state addresses look with `for_each`.

## Setup

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
```

## Main Workflow

1. Generate a saved plan:

```powershell
terraform plan -out=tfplan
```

2. Apply exactly what was reviewed:

```powershell
terraform apply tfplan
```

3. Inspect resource addresses:

```powershell
terraform state list
```

You should see addresses like:

- `local_file.notes["plan"]`
- `local_file.notes["state"]`

## Exercise: Change Collection

1. Add one more entry in `note_names`.
2. Run `terraform plan`.
3. Observe one additional create.

## Exercise: Detailed Exit Code

```powershell
terraform plan -detailed-exitcode
```

Interpretation:

- `0`: no changes
- `1`: error
- `2`: changes present

## Exercise: Target (For Learning Only)

```powershell
terraform plan -target=local_file.index
```

This is useful for debugging emergencies, but avoid normal use because it can produce partial graph behavior.
