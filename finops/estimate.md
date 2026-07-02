# Estimación de costos — {{PROJECT_NAME}}

**Presupuesto mensual objetivo:** USD {{BUDGET}}
**Región:** us-east-1
**Fecha:** {{FECHA}}

Este archivo es la sección de costos del entregable del proyecto. **No es opción-múltiple** — cada respuesta requiere que hayas mirado el output, la arquitectura, y hayas decidido.

---

## Preguntas para el arranque (con el `services.json` de ejemplo)

Corré `python3 pricing.py` sobre el ejemplo tal como viene y respondé:

**Q1.** ¿Cuál es el costo mensual total on-demand?
> _completar con el número del output_

**Q2.** Listá los top 3 servicios por costo, con % del total:
1. _servicio_ — $__ (__% del total)
2. _servicio_ — $__ (__% del total)
3. _servicio_ — $__ (__% del total)

**Q3.** De esos top 3, ¿cuántos son **compute**? ¿Cuántos son **storage** o **network**?
> _respuesta_

**Q4.** Aplicá Savings Plan y Spot: ¿cuánto ahorrás sobre el total?
> _número_

**Q5.** ¿La optimización SP + Spot alcanza para entrar en tu budget de {{BUDGET}}?
> _sí / no_

---

## Desafío 1 — Cambiar la arquitectura, no el descuento

**Contexto:** el NAT Gateway es de lejos el servicio más caro del ejemplo (~$32/mes solo por estar prendido 24/7). No hay Savings Plan ni Spot para NAT. Pero en el lab 07 vimos que **VPC endpoints** pueden reemplazarlo cuando el tráfico privado va sólo a AWS (ej. a S3).

**Q6.** Editá `services.json`: reemplazá la línea del `nat-gateway` por un **VPC endpoint para S3** (unit_price ~$0.01/hora * 730hs = ~$7.3/mes). Corré `pricing.py` de nuevo.

- Costo mensual total nuevo (optimizado): $___
- Ahorro vs. el original: $___
- ¿Ahora entra en el budget? Sí / No

**Q7.** ¿Qué tipo de tráfico **rompería** esta decisión? (pista: los VPC endpoints Gateway solo sirven para S3 y DynamoDB)
> _respuesta_

---

## Desafío 2 — Ajustar a un budget agresivo

**Contexto:** el equipo te dice que el proyecto tiene que caber en **$25/mes**. Con lo que vimos, no hay forma con la arquitectura del ejemplo. Hay que decidir tradeoffs.

**Q8.** Diseñá 2 opciones para entrar en $25:

**Opción A — recortar servicios:**
- Qué sacás:
- Qué se pierde en producto:
- Costo final estimado:

**Opción B — cambiar dimensionamiento:**
- Qué instance class bajás:
- Qué storage class cambiás (Standard → IA/Glacier):
- Qué uso mensual reducís:
- Costo final estimado:

**Q9.** ¿Cuál elegirías y por qué? (una decisión, no las dos)
> _respuesta_

---

## Desafío 3 — Escalar para producción

**Contexto:** el proyecto pasó a producción. Requerimientos: Multi-AZ en la DB, 3x el tráfico, 5x el storage en S3, ELB con health checks.

**Q10.** Escribí un `services.production.json` con las siguientes modificaciones sobre el ejemplo:
- `rds-db-t3-micro`: Multi-AZ (duplicar unit_price a $0.034)
- `s3-data-lake`: 500 GB
- `s3-requests`: 1500 k-req
- `data-egress`: 150 GB
- Agregar un `alb`: 730 hs * $0.0225/hs + 1 LCU/mes * $0.008/LCU-hs

**Q11.** ¿Qué budget mínimo necesitás para prod? _$__
**Q12.** ¿Cuánto más caro es prod vs dev? Xn/veces

---

## Tu proyecto real

**Q13.** Reemplazá los servicios del ejemplo por los del **stack real de tu proyecto final**. Ajustá `unit_price` con la [calculadora AWS oficial](https://calculator.aws/) y `monthly_usage` con la estimación real del equipo.

Salida final de `python3 pricing.py --budget {{BUDGET}}`:

```
_pegar aquí el output completo_
```

**Q14.** ¿Cumple el budget? Si sí, ¿con qué margen? Si no, ¿qué decidieron cambiar?
> _respuesta con justificación_

---

## Red de seguridad configurada

- [ ] `create-budget.sh` corrido contra AWS real
- [ ] Alerta al 80% ACTUAL confirmada (mail recibido de test)
- [ ] Alerta al 100% FORECASTED activa
- [ ] Mail del grupo (no default)

---

## Fuentes usadas

- [AWS Pricing Calculator](https://calculator.aws/)
- [EC2 pricing](https://aws.amazon.com/ec2/pricing/)
- [S3 pricing](https://aws.amazon.com/s3/pricing/)
- [NAT Gateway pricing](https://aws.amazon.com/vpc/pricing/)
- Otras: _completar_
