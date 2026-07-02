output "container_name" {
  description = "Nombre del container creado."
  value       = var.container_name
}

output "container_url" {
  description = "URL del container en el emulador (formato Azure path-style)."
  value       = "${var.azure_emulator_endpoint}/${var.storage_account}.blob/${var.container_name}"
}

output "seed_object_url" {
  description = "URL del blob seed."
  value       = "${var.azure_emulator_endpoint}/${var.storage_account}.blob/${var.container_name}/hello.txt"
}
