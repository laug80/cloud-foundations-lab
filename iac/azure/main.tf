# Lab 09 — IaC contra el emulador Azure (cmarin78/azure-cloud-emulator).
#
# Honestidad técnica: el provider `azurerm` oficial habla con ARM (management
# API) y los emuladores Azure no la implementan en forma completa. Para que
# este lab corra contra el emulador local sin trampas, usamos `null_resource`
# con `local-exec` (llamadas curl).
#
# Eso muestra el patrón declarativo (tofu apply/destroy idempotente) sin fingir
# que un provider funciona. Para Azure REAL, ver el archivo `azurerm.tf.example`.

terraform {
  required_version = ">= 1.6"
}

# Crear el container — Azure shape: PUT /{account}.blob/{container}?restype=container
resource "null_resource" "container" {
  triggers = {
    endpoint  = var.azure_emulator_endpoint
    account   = var.storage_account
    container = var.container_name
  }

  provisioner "local-exec" {
    command = "curl -sf -X PUT '${var.azure_emulator_endpoint}/${var.storage_account}.blob/${var.container_name}?restype=container'"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "curl -sf -X DELETE '${self.triggers.endpoint}/${self.triggers.account}.blob/${self.triggers.container}?restype=container' || true"
  }
}

# Subir un blob seed — equivalente a aws_s3_object o google_storage_bucket_object
resource "null_resource" "hello" {
  triggers = {
    endpoint  = var.azure_emulator_endpoint
    account   = var.storage_account
    container = var.container_name
    content   = "hello from IaC — container ${var.container_name}"
  }

  depends_on = [null_resource.container]

  provisioner "local-exec" {
    command = "echo -n '${self.triggers.content}' | curl -sf -X PUT '${var.azure_emulator_endpoint}/${var.storage_account}.blob/${var.container_name}/hello.txt' -H 'x-ms-blob-type: BlockBlob' --data-binary @-"
  }
}
