resource "yandex_iam_service_account" "cloud-editor" {
  folder_id = var.folder_id
  name = "cloud-editor"
}

resource "yandex_resourcemanager_folder_iam_member" "storage-admin" {
  folder_id = var.folder_id
  member    = "serviceAccount:${yandex_iam_service_account.cloud-editor.id}"
  role      = "storage.admin"
}

resource "yandex_iam_service_account_static_access_key" "cloud-editor" {
  service_account_id = yandex_iam_service_account.cloud-editor.id
}

### Object Storage ###

resource "yandex_storage_bucket" "waste-detection" {
  bucket = "waste-detection"
  access_key = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key = yandex_iam_service_account_static_access_key.cloud-editor.secret_key
}
