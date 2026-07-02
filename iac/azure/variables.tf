variable "azure_emulator_endpoint" {
  type        = string
  description = "Endpoint del emulador Azure (cmarin78/azure-cloud-emulator)."
  default     = "http://localhost:10000"
}

variable "storage_account" {
  type        = string
  description = "Storage account. En Azure real lo crearías con azurerm_storage_account; en el emulador ya existe."
  default     = "devstoreaccount1"
}

variable "container_name" {
  type        = string
  description = "Nombre del container de Blob Storage."
  default     = "lab-09-app-container"
}
