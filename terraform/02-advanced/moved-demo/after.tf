terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "local" {}

moved {
  from = local_file.old_name
  to   = local_file.new_name
}

resource "local_file" "new_name" {
  filename = "${path.module}/moved-demo.txt"
  content  = "This resource has a new address without recreation.\n"
}
