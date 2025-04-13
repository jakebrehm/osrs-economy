variable "credentials" {
  description = "GCP Credentials to use for the project."
  type        = string
  default     = "../cfg/gcp-credentials.json"
}

variable "project_id" {
  description = "GCP Project ID to use for the project."
  type        = string
  default     = ""
}

variable "region" {
  description = "GCP Region to use for the project."
  type        = string
  default     = "us-central1"
}

variable "storage_details_bucket_name" {
  description = "Name of the details storage bucket to create."
  type        = string
  default     = ""
}

variable "storage_prices_bucket_name" {
  description = "Name of the prices storage bucket to create."
  type        = string
  default     = ""
}

variable "storage_bucket_location" {
  description = "Location of the storage bucket to create."
  type        = string
  default     = "US"
}

variable "bigquery_dataset_name" {
  description = "Name of the BigQuery dataset to create."
  type        = string
  default     = ""
}

variable "bigquery_dataset_location" {
  description = "Location of the BigQuery dataset to create."
  type        = string
  default     = "US"
}
