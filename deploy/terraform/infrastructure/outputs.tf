output "access-keys" {
  value = {
    "ksenya-portnova": {
        access_key = yandex_iam_service_account_static_access_key.ksenya-portnova-oc.access_key
        secret_key = yandex_iam_service_account_static_access_key.ksenya-portnova-oc.secret_key
    }
    "sergei-kiprin": {
        access_key = yandex_iam_service_account_static_access_key.sergei-kiprin-oc.access_key
        secret_key = yandex_iam_service_account_static_access_key.sergei-kiprin-oc.secret_key
    }
  }
  sensitive = true
}
