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

# storage-editor

resource "yandex_iam_service_account" "storage-editor" {
  folder_id = var.folder_id
  name      = "storage-editor"
}

resource "yandex_iam_service_account_static_access_key" "storage-editor" {
  service_account_id = yandex_iam_service_account.storage-editor.id
}

# team1

resource "yandex_iam_service_account" "team1" {
  folder_id = var.folder_id
  name      = "team1"
}

resource "yandex_iam_service_account_static_access_key" "team1" {
  service_account_id = yandex_iam_service_account.team1.id
}

# team2

resource "yandex_iam_service_account" "team2" {
  folder_id = var.folder_id
  name      = "team2"
}

resource "yandex_iam_service_account_static_access_key" "team2" {
  service_account_id = yandex_iam_service_account.team2.id
}

# team3

resource "yandex_iam_service_account" "team3" {
  folder_id = var.folder_id
  name      = "team3"
}

resource "yandex_iam_service_account_static_access_key" "team3" {
  service_account_id = yandex_iam_service_account.team3.id
}

# mlflow

resource "yandex_iam_service_account" "mlflow" {
  folder_id = var.folder_id
  name      = "mlflow"
}

resource "yandex_iam_service_account_static_access_key" "mlflow" {
  service_account_id = yandex_iam_service_account.mlflow.id
}

# app

resource "yandex_iam_service_account" "app" {
  folder_id = var.folder_id
  name      = "app"
}

resource "yandex_iam_service_account_static_access_key" "app" {
  service_account_id = yandex_iam_service_account.app.id
}

# label-studio

resource "yandex_iam_service_account" "label-studio" {
  folder_id = var.folder_id
  name      = "label-studio"
}

resource "yandex_iam_service_account_static_access_key" "label-studio" {
  service_account_id = yandex_iam_service_account.label-studio.id
}

### Object Storage ###

resource "yandex_storage_bucket" "waste-detection" {
  bucket     = "waste"
  access_key = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key = yandex_iam_service_account_static_access_key.cloud-editor.secret_key

  grant {
    id          = yandex_iam_service_account.storage-editor.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }

  grant {
    id          = yandex_iam_service_account.team1.id
    type        = "CanonicalUser"
    permissions = ["READ"]
  }

  grant {
    id          = yandex_iam_service_account.team2.id
    type        = "CanonicalUser"
    permissions = ["READ"]
  }

  grant {
    id          = yandex_iam_service_account.team3.id
    type        = "CanonicalUser"
    permissions = ["READ"]
  }

  grant {
    id          = yandex_iam_service_account.label-studio.id
    type        = "CanonicalUser"
    permissions = ["READ"]
  }

  anonymous_access_flags {
    read = true
  }

  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["http://waste.sergei-kiprin.ru"]
  }
}

resource "yandex_storage_bucket" "mlflow" {
  bucket_prefix = "mlflow-storage"
  access_key    = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key    = yandex_iam_service_account_static_access_key.cloud-editor.secret_key

  grant {
    id          = yandex_iam_service_account.mlflow.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
    
  grant {
    id          = yandex_iam_service_account.storage-editor.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
  
  grant {
    id          = yandex_iam_service_account.app.id
    type        = "CanonicalUser"
    permissions = ["READ"]
  }
}

resource "yandex_storage_bucket" "app-storage" {
  bucket_prefix = "app-storage"
  access_key    = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key    = yandex_iam_service_account_static_access_key.cloud-editor.secret_key

  grant {
    id          = yandex_iam_service_account.app.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }

  anonymous_access_flags {
    read = true
  }
}

resource "yandex_storage_bucket" "app" {
  bucket = "waste-detection"
  access_key    = yandex_iam_service_account_static_access_key.cloud-editor.access_key
  secret_key    = yandex_iam_service_account_static_access_key.cloud-editor.secret_key

  grant {
    id          = yandex_iam_service_account.storage-editor.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }

  website {
    index_document = "index.html"
  }
}

### Virtual Private Cloud ###

data "yandex_vpc_network" "default" {
  name = "default"
}

data "yandex_vpc_subnet" "default" {
  subnet_id = data.yandex_vpc_network.default.subnet_ids[0]
}

resource "yandex_vpc_address" "label-studio" {
  name = "label-studio"

  external_ipv4_address {
    zone_id = data.yandex_vpc_subnet.default.zone
  }
}

### Compute Cloud ###

data "yandex_compute_image" "container-optimized-image" {
  image_id = "fd8d61mhumda10cb33vm"
}

resource "yandex_compute_instance" "label-studio" {
  name               = "label-studio"
  service_account_id = yandex_iam_service_account.label-studio.id
  platform_id        = "standard-v3"
  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.container-optimized-image.id
      size = 50
    }
  }
  network_interface {
    subnet_id      = data.yandex_vpc_subnet.default.id
    nat            = true
    nat_ip_address = yandex_vpc_address.label-studio.external_ipv4_address[0].address
  }
  resources {
    cores         = 2
    memory        = 2
    core_fraction = 50
  }
  scheduling_policy {
    preemptible = true
  }
  metadata = {
    docker-compose = templatefile("docker-compose.yaml", {
      mlflow_s3_bucket     = yandex_storage_bucket.mlflow.id
      mlflow_s3_key_id     = yandex_iam_service_account_static_access_key.mlflow.access_key
      mlflow_s3_key_secret = yandex_iam_service_account_static_access_key.mlflow.secret_key
      app_s3_bucket     = yandex_storage_bucket.app-storage.id
      app_s3_key_id     = yandex_iam_service_account_static_access_key.app.access_key
      app_s3_key_secret = yandex_iam_service_account_static_access_key.app.secret_key
    })
    ssh-keys = "angstorm:${var.ssh_pub}"
  }
  allow_stopping_for_update = true
}
