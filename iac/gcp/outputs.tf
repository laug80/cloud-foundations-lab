output "bucket_name" {
  description = "Nombre del bucket creado."
  value       = google_storage_bucket.app.name
}

output "bucket_url" {
  description = "URL gs:// del bucket."
  value       = google_storage_bucket.app.url
}

output "seed_object_url" {
  description = "URL del objeto seed."
  value       = "gs://${google_storage_bucket.app.name}/${google_storage_bucket_object.hello.name}"
}
