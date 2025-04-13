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
