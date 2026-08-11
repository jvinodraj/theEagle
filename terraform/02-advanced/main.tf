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

variable "label" {
  description = "Tag label for generated content"
  type        = string
  default     = "advanced-lab"
}

resource "local_file" "config" {
  filename = "${path.module}/config.txt"
  content  = "label=${var.label}\n"

  lifecycle {
    prevent_destroy = false
  }
}

resource "local_file" "report" {
  filename = "${path.module}/report.txt"
  content  = <<-EOT
    resource : ${local_file.config.filename}
    label    : ${var.label}
  EOT
}
