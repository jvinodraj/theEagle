terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "local" {}

resource "local_file" "old_name" {
  filename = "${path.module}/moved-demo.txt"
  content  = "This resource will be renamed.\n"
}
