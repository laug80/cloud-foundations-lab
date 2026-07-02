variable "project_id" {
  type        = string
  description = "GCP project id (cualquier string para el emulador, real en GCP)."
  default     = "lab-09-project"
}

variable "region" {
  type        = string
  description = "Región GCP."
  default     = "us-central1"
}

variable "bucket_name" {
  type        = string
  description = "Nombre del bucket de Cloud Storage."
  default     = "lab-09-app-bucket-gcp"
}

variable "gcp_emulator_endpoint" {
  type        = string
  description = "Endpoint del emulador GCP (cmarin78/gcp-emulator). Para GCP real, vacío y quitar los custom_endpoint del provider."
  default     = "http://localhost:8443"
}
