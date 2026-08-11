# Stage 00 - Beginner

Goal: learn what Terraform plan and state are by observing simple file resources.

## Steps

1. Copy vars file:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` and set your name.

3. Run the first lifecycle:

```powershell
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

4. Inspect state:

```powershell
terraform state list
terraform state show local_file.greeting
terraform state show local_file.summary
```

## What to Observe

- `plan` before first apply should show `2 to add`.
- `plan` after apply should show `No changes`.
- `terraform.tfstate` now maps both resource addresses.

## Exercise: Create Drift

1. Open `greeting.txt` and change a line manually.
2. Run:

```powershell
terraform plan
```

3. You should see Terraform wants to restore desired content.

## Exercise: Refresh-Only

```powershell
terraform plan -refresh-only
```

Use this when you want to sync state with real world observation without changing config intent.
