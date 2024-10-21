locals {
  main_zone = "ru-central1-b"
}

variable "iam_token" {
  type = string
}

variable "cloud_id" {
  type = string
}

variable "folder_id" {
  type = string
}

variable "ssh_pub" {
  type = string
}
