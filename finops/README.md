# `finops/` — Lab 10: Cloud Economics & FinOps

Dos piezas en el mismo orden que la clase:

1. **Estimar** — costos antes de tocar la infra (`pricing.py` + `services.json`)
2. **Red de seguridad** — Budget con alertas antes de que llegue la factura (`budget.json` + `notify.json` + `create-budget.sh`)

## Archivos

| Archivo | Rol |
|---|---|
| `services.json` | Servicios de tu arquitectura + uso mensual (input del estimador) |
| `pricing.py` | Estimador local: on-demand vs optimizado + comparación al budget |
| `estimate.md` | Plantilla de la sección de costos del entregable del proyecto |
| `budget.json` | Definición del presupuesto mensual (formato `aws budgets create-budget`) |
| `notify.json` | Alertas: 80% ACTUAL y 100% FORECASTED, por mail |
| `create-budget.sh` | Crea el Budget con la AWS CLI |

## Uso rápido

```bash
# 1. Estimador local ($0, sin nube)
python3 pricing.py
python3 pricing.py --budget 15    # con otro budget

# 2. Budget en AWS real (editá primero el mail en notify.json)
./create-budget.sh
```

## LocalStack — importante

**AWS Budgets es Pro-only en LocalStack** (no incluido en Community). El `create-budget.sh` contra Community falla con `API not implemented`. Es una limitación del emulador — el budget de verdad se prueba contra AWS real, mismo criterio que el resto del módulo cuando algo depende de facturación/alertas.

## Precios referenciales

Los precios en `services.json` son de us-east-1 y sirven para el ejercicio. Los oficiales (con descuentos por región, familia y compromiso) se sacan de:
- https://calculator.aws/ — calculadora oficial
- https://aws.amazon.com/ec2/pricing/ — EC2
- https://aws.amazon.com/s3/pricing/ — S3
- https://aws.amazon.com/pricing/ — hub de precios

## El punto de fondo

El costo es una **decisión de arquitectura**, no algo que se descubre a fin de mes. Este lab pone la decisión antes: estimar, decidir con criterio, monitorear con un tope.
