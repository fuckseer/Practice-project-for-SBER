### IAM ###

resource "yandex_iam_service_account" "cloud-editor" {
  folder_id = var.folder_id
  name      = "cloud-editor"
}

resource "yandex_resourcemanager_folder_iam_member" "storage-admin" {
  folder_id = var.folder_id
  member    = "serviceAccount:${yandex_iam_service_account.cloud-editor.id}"
  role      = "storage.admin"
}

resource "yandex_iam_service_account_static_access_key" "cloud-editor" {
  service_account_id = yandex_iam_service_account.cloud-editor.id
}

resource "yandex_iam_service_account" "sergei-kiprin" {
  folder_id = var.folder_id
  name      = "sergei-kiprin"
}

resource "yandex_iam_service_account_static_access_key" "sergei-kiprin-oc" {
  service_account_id = yandex_iam_service_account.sergei-kiprin.id
}

resource "yandex_iam_service_account" "ksenya-portnova" {
  folder_id = var.folder_id
  name      = "ksenya-portnova"
}

resource "yandex_iam_service_account_static_access_key" "ksenya-portnova-oc" {
  service_account_id = yandex_iam_service_account.ksenya-portnova.id
}

### Object Storage ###

resource "yandex_storage_bucket" "waste-detection" {
  bucket     = "waste"
  access_key = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key = yandex_iam_service_account_static_access_key.cloud-editor.secret_key

  grant {
    id          = yandex_iam_service_account.sergei-kiprin.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }

  grant {
    id          = yandex_iam_service_account.ksenya-portnova.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
}
