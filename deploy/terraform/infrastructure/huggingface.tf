# terraform {
#   required_providers {
#     huggingface-spaces = {
#       source = "registry.terraform.io/strickvl/huggingface-spaces"
#     }
#   }
# }

# variable "huggingface_api_token" {
#   type      = string
#   sensitive = true
# }

# provider "huggingface-spaces" {
#   token = var.huggingface_api_token
# }

# locals {
#   user_name  = "angstorm"
#   space_name = "ocean-waste-detection"
# }

# resource "huggingface-spaces_space" "ocean_waste_detection" {
#   name     = local.space_name
#   private  = false
#   sdk      = "docker"
#   hardware = "cpu-basic"

#   secrets = {
#     AWS_ACCESS_KEY_ID     = yandex_iam_service_account_static_access_key.mlflow.access_key
#     AWS_SECRET_ACCESS_KEY = yandex_iam_service_account_static_access_key.mlflow.secret_key
#   }

#   variables = {
#     MLFLOW_S3_ENDPOINT_URL = "https://storage.yandexcloud.net/"
#     DOWNLOAD_MODEL         = "true"
#     MLFLOW_URL             = "http://waste.sergei-kiprin.ru:5000"
#     APP_URL                = "https://${local.user_name}-${local.space_name}.hf.space/predict"
#   }
# }

# data "huggingface-spaces_space" "ocean_waste_detection" {
#   id = huggingface-spaces_space.ocean_waste_detection.id
# }

# output "hf_space_repo_ssh_link" {
#   value = "git@hf.co:spaces/${data.huggingface-spaces_space.ocean_waste_detection.author}/${data.huggingface-spaces_space.ocean_waste_detection.name}"
# }
