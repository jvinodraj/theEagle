terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "local" {}

locals {
  headers = {
    env   = var.environment
    owner = var.owner
  }
}

resource "local_file" "notes" {
  for_each = toset(var.note_names)

  filename = "${path.module}/${each.key}.txt"
  content  = <<-EOT
    note        : ${each.key}
    environment : ${local.headers.env}
    owner       : ${local.headers.owner}
  EOT
}

resource "local_file" "index" {
  filename = "${path.module}/index.txt"
  content  = join("\n", concat(
    ["generated files:"],
    [for key, value in local_file.notes : "- ${key}: ${value.filename}"]
  ))
}
