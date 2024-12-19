locals {
  main_zone = "ru-central1-b"
}

variable "user_id" {
  type = string
}

variable "iam_token" {
  type = string
  sensitive = true
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
