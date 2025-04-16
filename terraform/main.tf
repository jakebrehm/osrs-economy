terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.29.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project_id
  region      = var.region
}

resource "google_storage_bucket" "osrs_details" {
  name          = var.storage_details_bucket_name
  location      = var.storage_bucket_location
  force_destroy = true
}

resource "google_storage_bucket" "osrs_prices" {
  name          = var.storage_prices_bucket_name
  location      = var.storage_bucket_location
  force_destroy = true
}

resource "google_bigquery_dataset" "osrs_economy" {
  dataset_id = var.bigquery_dataset_name
  location   = var.bigquery_dataset_location
}

resource "google_bigquery_table" "item_details" {
  table_id   = var.bigquery_items_table_name
  dataset_id = google_bigquery_dataset.osrs_economy.dataset_id

  schema = file(var.bigquery_items_table_schema)
}

resource "google_bigquery_table" "item_prices" {
  table_id   = var.bigquery_bronze_prices_table_name
  dataset_id = google_bigquery_dataset.osrs_economy.dataset_id
  schema     = file(var.bigquery_bronze_prices_table_schema)
}
