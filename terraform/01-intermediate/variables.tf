variable "environment" {
  description = "Environment label"
  type        = string
}

variable "owner" {
  description = "Owner name"
  type        = string
}

variable "note_names" {
  description = "Names of note files to create"
  type        = list(string)
}
