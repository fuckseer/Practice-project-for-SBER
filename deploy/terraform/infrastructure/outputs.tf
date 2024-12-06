output "access-keys" {
  value = {
    "storage-editor" : {
      access_key = yandex_iam_service_account_static_access_key.storage-editor.access_key
      secret_key = yandex_iam_service_account_static_access_key.storage-editor.secret_key
    },
    "team1" : {
      access_key = yandex_iam_service_account_static_access_key.team1.access_key
      secret_key = yandex_iam_service_account_static_access_key.team1.secret_key
    }
    "team2" : {
      access_key = yandex_iam_service_account_static_access_key.team2.access_key
      secret_key = yandex_iam_service_account_static_access_key.team2.secret_key
    }
    "team3" : {
      access_key = yandex_iam_service_account_static_access_key.team3.access_key
      secret_key = yandex_iam_service_account_static_access_key.team3.secret_key
    }
    "mlflow" : {
      access_key = yandex_iam_service_account_static_access_key.mlflow.access_key
      secret_key = yandex_iam_service_account_static_access_key.mlflow.secret_key
    }
    "app" : {
      access_key = yandex_iam_service_account_static_access_key.app.access_key
      secret_key = yandex_iam_service_account_static_access_key.app.secret_key
    }
    "label-studio" : {
      access_key = yandex_iam_service_account_static_access_key.label-studio.access_key
      secret_key = yandex_iam_service_account_static_access_key.label-studio.secret_key
    }
  }
  sensitive = true
}
