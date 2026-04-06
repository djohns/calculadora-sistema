"""
Ejemplos de uso de la Calculadora de Apuestas de Sistema.
Ejecuta este archivo para ver demos de distintos escenarios.
"""

from calculadora_sistema import (
    CalculadoraSistema,
    recomendar_sistema,
    imprimir_resumen,
    imprimir_tabla_escenarios,
    imprimir_selecciones,
    imprimir_recomendaciones,
    imprimir_detalle_parlays,
    imprimir_analisis_ev,
    imprimir_banner,
    VERDE, BOLD, CYAN, RESET, AZUL
)


def demo_1_sistema_basico():
    """Sistema 2/3: tres partidos de fútbol europeo."""
    print(f"\n{BOLD}{AZUL}{'═'*60}")
    print("  DEMO 1: Sistema 2/3 — Premier League")
    print(f"{'═'*60}{RESET}")

    calc = CalculadoraSistema(
        cuotas=[1.85, 2.10, 3.40],
        stake_total=50_000,
        nombres=["Man City G", "Arsenal G", "Brighton G"],
        min_k=2,
    )
    imprimir_selecciones(calc)
    imprimir_resumen(calc)
    imprimir_tabla_escenarios(calc)
    imprimir_detalle_parlays(calc)


def demo_2_yankee():
    """Sistema Yankee: 4 selecciones, 11 apuestas."""
    print(f"\n{BOLD}{AZUL}{'═'*60}")
    print("  DEMO 2: Sistema Yankee (4 selecciones)")
    print(f"{'═'*60}{RESET}")

    calc = CalculadoraSistema(
        cuotas=[1.80, 2.20, 2.70, 3.10],
        stake_total=100_000,
        nombres=["Bayern G", "Dortmund G", "Leverkusen G", "Leipzig G"],
        min_k=2,
        max_k=4,
    )
    imprimir_selecciones(calc)
    imprimir_resumen(calc)
    imprimir_tabla_escenarios(calc)
    imprimir_detalle_parlays(calc, max_mostrar=11)


def demo_3_con_ev():
    """Sistema 2/4 con análisis de EV (tienes tus propias probabilidades)."""
    print(f"\n{BOLD}{AZUL}{'═'*60}")
    print("  DEMO 3: Sistema 2/4 + Análisis de EV")
    print(f"{'═'*60}{RESET}")

    calc = CalculadoraSistema(
        cuotas=[1.90, 2.05, 2.40, 3.20],
        stake_total=80_000,
        nombres=["Napoli G", "Milan G", "Inter G", "Roma G"],
        min_k=2,
        probs_estimadas=[0.56, 0.52, 0.44, 0.35],  # tus estimaciones
    )
    imprimir_selecciones(calc)
    imprimir_resumen(calc)
    imprimir_tabla_escenarios(calc)
    imprimir_analisis_ev(calc)


def demo_4_comparativa():
    """Comparativa de todos los sistemas posibles para las mismas cuotas."""
    print(f"\n{BOLD}{AZUL}{'═'*60}")
    print("  DEMO 4: Comparativa de sistemas para 5 selecciones")
    print(f"{'═'*60}{RESET}")

    cuotas = [1.75, 1.90, 2.20, 2.60, 3.00]
    stake = 150_000

    print(f"\n  Cuotas: {cuotas}")
    print(f"  Stake : ${stake:,} CLP\n")
    imprimir_recomendaciones(cuotas, stake)


def demo_5_uso_programatico():
    """Uso del módulo como librería en tu propio script."""
    print(f"\n{BOLD}{AZUL}{'═'*60}")
    print("  DEMO 5: Uso programático (como librería)")
    print(f"{'═'*60}{RESET}")

    calc = CalculadoraSistema(
        cuotas=[1.85, 2.10, 2.90],
        stake_total=60_000,
        nombres=["Bayer G", "PSG G", "Porto G"],
        min_k=2,
    )

    resumen = calc.resumen()
    print(f"\n  Stake/parlay    : ${resumen['stake_por_parlay']:,}")
    print(f"  Número de parlays: {resumen['num_parlays']}")
    print(f"  Retorno máximo  : ${resumen['max_retorno_posible']:,}")
    print(f"  ROI máximo      : +{resumen['max_roi_posible']}%")
    print(f"  Mín. aciertos rentable: {resumen['min_aciertos_para_rentabilidad']}/3")

    print("\n  Escenario si aciertas 2 de 3 (peor caso):")
    escenarios = calc.tabla_escenarios()
    fila_2 = escenarios[2]
    print(f"    Retorno peor  : ${fila_2['retorno_peor']:,}")
    print(f"    Retorno mejor : ${fila_2['retorno_mejor']:,}")
    print(f"    ROI peor      : {fila_2['roi_peor']}%")


if __name__ == "__main__":
    imprimir_banner()
    demo_1_sistema_basico()
    demo_2_yankee()
    demo_3_con_ev()
    demo_4_comparativa()
    demo_5_uso_programatico()
    print(f"\n{VERDE}{BOLD}✓ Todos los demos ejecutados correctamente.{RESET}\n")
