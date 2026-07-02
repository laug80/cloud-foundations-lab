# `iac/` — Infrastructure as Code (multi-cloud)

La misma intención (un bucket/container con un objeto seed) declarada en HCL contra los 3 proveedores. Cada carpeta es un stack independiente con su propio state.

```
iac/
├── aws/      ← provider AWS hacia LocalStack (default del lab)
├── gcp/      ← provider Google hacia cmarin78/gcp-emulator
└── azure/    ← null_resource + curl hacia cmarin78/azure-cloud-emulator
```

## Cuál usar

**Para el lab 09 obligatorio: `iac/aws/`.** El resto es opcional para entender qué cambia entre clouds.

```bash
cd iac/aws/
tofu init && tofu plan && tofu apply
```

**Para el lab opcional multi-cloud:** levantar los 3 emuladores (`docker compose --profile multicloud up -d`) y correr `tofu apply` en cada carpeta. Ver `docs/lab-opcional-multi-cloud.md` para el contexto pedagógico.

## La misma idea, tres formas

| Concepto | AWS | GCP | Azure (emulador) |
|---|---|---|---|
| Provider | `hashicorp/aws` | `hashicorp/google` | `null_resource` + curl |
| Recurso bucket/container | `aws_s3_bucket` | `google_storage_bucket` | curl PUT `?restype=container` |
| Objeto seed | `aws_s3_object` | `google_storage_bucket_object` | curl PUT con `x-ms-blob-type` |
| Versioning | `aws_s3_bucket_versioning` | dentro del `google_storage_bucket` | no soportado en el emulador |
| Endpoint custom | `endpoints {}` en provider | `*_custom_endpoint` en provider | URL directa en el resource |

## ¿Por qué Azure con null_resource?

El provider `azurerm` oficial habla con **ARM (Azure Resource Manager)**, que el emulador no implementa en forma completa. En lugar de fingir que `azurerm` corre contra el emulador, usamos `null_resource` con `local-exec` — feo pero honesto: muestra el patrón declarativo (`tofu apply/destroy` idempotente) sin trampas.

`iac/azure/azurerm.tf.example` muestra cómo se vería en Azure real para que el alumno aprenda la sintaxis correcta. No es ejecutable contra el emulador.

## Workflow estándar (en cualquier stack)

```bash
tofu init      # baja providers
tofu plan      # diff antes de aplicar
tofu apply     # crea/modifica recursos
tofu destroy   # baja todo
```

Para que un cambio de stack no se mezcle con otro, cada carpeta tiene su propio `terraform.tfstate`. Los 3 pueden coexistir sin colisión.

## De emulador a cloud real

Cada `main.tf` tiene comentado qué borrar para pasar a producción:
- **AWS**: quitar bloque `endpoints {}` del provider
- **GCP**: quitar `*_custom_endpoint` y poner credenciales reales (`gcloud auth application-default login`)
- **Azure**: usar `azurerm.tf.example` con `az login`
