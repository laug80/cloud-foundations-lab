"""
Lab 10 — Estimador de costos mensual (100% local, sin nube, sin costo).

Lee finops/services.json (los servicios del proyecto + su uso mensual estimado)
y calcula:
  - Costo mensual on-demand (precio de lista)
  - Costo mensual optimizado (Savings Plan + Spot)
  - Comparación contra el presupuesto (--budget)

El objetivo es tomar la decisión de costos ANTES de tocar la infra, no al final
del mes cuando llega la factura.

Uso:
    python3 pricing.py
    python3 pricing.py --budget 15
    python3 pricing.py --services otro.json --budget 100

Notas técnicas:
- Solo usa stdlib. No hay que instalar nada.
- Descuentos referenciales: Savings Plan Compute 1 año = ~30% off, Spot = ~70% off.
  Los números reales varían por región, familia y período de commitment.
- Fuente oficial de precios: https://calculator.aws/
"""

import argparse
import json
import sys
from pathlib import Path

# Descuentos referenciales (mercado, us-east-1). En prod, calcular con datos reales.
SAVINGS_PLAN_DISCOUNT = 0.30   # Compute SP, 1 año, no upfront
SPOT_DISCOUNT = 0.70           # Spot típico (varía 50-90% según demanda)


def compute_row(service: dict) -> dict:
    """Calcula on-demand y optimizado por servicio.

    Reglas: Spot si spot_eligible. Si no, Savings Plan si sp_eligible.
    Si ninguno, precio on-demand.
    """
    ondemand = service["monthly_usage"] * service["unit_price"]

    if service.get("spot_eligible", False):
        optimized = ondemand * (1 - SPOT_DISCOUNT)
        strategy = "Spot"
    elif service.get("sp_eligible", False):
        optimized = ondemand * (1 - SAVINGS_PLAN_DISCOUNT)
        strategy = "SavingsPlan"
    else:
        optimized = ondemand
        strategy = "OnDemand"

    return {
        **service,
        "ondemand_cost": ondemand,
        "optimized_cost": optimized,
        "strategy": strategy,
        "monthly_savings": ondemand - optimized,
    }


def _print_row_ondemand(r: dict) -> None:
    print(
        f"  {r['name']:<20} {r['type']:<10} "
        f"{r['monthly_usage']:>8} {r['unit']:<8} "
        f"${r['unit_price']:>8.4f}  ${r['ondemand_cost']:>7.2f}"
    )


def _print_row_optimized(r: dict) -> None:
    print(
        f"  {r['name']:<20} {r['strategy']:<12} "
        f"${r['ondemand_cost']:>7.2f}  ${r['optimized_cost']:>8.2f}  "
        f"${r['monthly_savings']:>7.2f}"
    )


def report(rows: list, budget: float) -> None:
    print("─" * 78)
    print("On-Demand (precio de lista)")
    print("─" * 78)
    print(f"  {'Servicio':<20} {'Cargo':<10} {'Uso':>8} {'Unidad':<8} {'Precio':>10}  {'Costo':>8}")
    print()
    for r in rows:
        _print_row_ondemand(r)
    total_od = sum(r["ondemand_cost"] for r in rows)
    print()
    print(f"  {'TOTAL':<60}${total_od:>7.2f}")

    print()
    print("─" * 78)
    print("Optimizado (Savings Plan al baseline + Spot al interrumpible)")
    print("─" * 78)
    print(f"  {'Servicio':<20} {'Estrategia':<12} {'On-Demand':>8}  {'Optimizado':>10}  {'Ahorro':>7}")
    print()
    for r in rows:
        _print_row_optimized(r)
    total_opt = sum(r["optimized_cost"] for r in rows)
    saved = total_od - total_opt
    print()
    print(f"  {'TOTAL':<32} ${total_od:>7.2f}  ${total_opt:>8.2f}  ${saved:>7.2f}")

    print()
    print("=" * 78)
    print("Presupuesto vs realidad")
    print("=" * 78)
    print(f"  Presupuesto:      ${budget:>7.2f}")
    print(f"  On-Demand:        ${total_od:>7.2f}  ({total_od / budget * 100:>4.0f}% del budget)")
    print(f"  Optimizado:       ${total_opt:>7.2f}  ({total_opt / budget * 100:>4.0f}% del budget)")
    print(f"  Ahorro mensual:   ${saved:>7.2f}")

    if total_opt <= budget:
        print(f"  Estado:           ✓ entra en budget con optimización")
    elif total_od <= budget:
        print(f"  Estado:           ⚠ excede on-demand, entra optimizado")
    else:
        print(f"  Estado:           ✗ excede budget aún optimizado")
        # Sugerencia de qué mirar
        top = sorted(rows, key=lambda r: r["optimized_cost"], reverse=True)[:2]
        print(f"  Top 2 más caros:  {', '.join(t['name'] for t in top)}")
        print(f"  Pregunta:         ¿podés cambiar la arquitectura para reducirlos?")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimador de costos mensual (local, sin nube)."
    )
    parser.add_argument("--budget", type=float, default=20.0,
                        help="Presupuesto mensual USD (default 20)")
    parser.add_argument("--services", default="services.json",
                        help="Path al JSON de servicios (default: finops/services.json al lado de este script)")
    args = parser.parse_args()

    services_path = Path(args.services)
    if not services_path.is_absolute():
        services_path = Path(__file__).parent / args.services

    if not services_path.exists():
        print(f"ERROR: no encuentro {services_path}", file=sys.stderr)
        return 1

    data = json.loads(services_path.read_text())
    rows = [compute_row(s) for s in data["services"]]
    report(rows, args.budget)
    return 0


if __name__ == "__main__":
    sys.exit(main())
