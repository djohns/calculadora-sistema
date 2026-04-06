"""
╔══════════════════════════════════════════════════════════════════╗
║          CALCULADORA DE APUESTAS DE SISTEMA  v1.0               ║
║          Para uso personal en Betano y similares                 ║
╚══════════════════════════════════════════════════════════════════╝

Lógica matemática:
  - Una apuesta de sistema k/N genera C(N,k) parlays independientes.
  - Cada parley tiene cuota combinada = ∏(cuotas de las k selecciones).
  - El stake se distribuye igualmente entre todos los parlays.
  - Ganas parcialmente aunque fallen algunas selecciones.

Sistemas nombrados soportados:
  Trixie   = 3 selecciones, todos los dobles + el treble   (4 apuestas)
  Patent   = 3 selecciones, singles + dobles + treble      (7 apuestas)
  Yankee   = 4 selecciones, dobles + trebles + cuádruple   (11 apuestas)
  Lucky 15 = 4 selecciones, singles + dobles + trebles + cuádruple (15)
  Lucky 31 = 5 selecciones, todas las combinaciones        (31)
  Lucky 63 = 6 selecciones, todas las combinaciones        (63)
  Heinz    = 6 selecciones, dobles hasta séxtuple          (57)

Autor: uso personal
"""

from itertools import combinations
from math import comb
from typing import Optional
import argparse
import sys

# ─────────────────────────────────────────────────────────────────
# CONSTANTES: Sistemas nombrados
# ─────────────────────────────────────────────────────────────────

NAMED_SYSTEMS = {
    "trixie":   {"n": 3, "min_k": 2, "include_singles": False},
    "patent":   {"n": 3, "min_k": 1, "include_singles": True},
    "yankee":   {"n": 4, "min_k": 2, "include_singles": False},
    "lucky15":  {"n": 4, "min_k": 1, "include_singles": True},
    "lucky31":  {"n": 5, "min_k": 1, "include_singles": True},
    "lucky63":  {"n": 6, "min_k": 1, "include_singles": True},
    "heinz":    {"n": 6, "min_k": 2, "include_singles": False},
    "superheinz": {"n": 7, "min_k": 2, "include_singles": False},
    "goliath":  {"n": 8, "min_k": 2, "include_singles": False},
}

NAMED_DESCRIPTIONS = {
    "trixie":     "3 sel → 3 dobles + 1 treble (4 apuestas)",
    "patent":     "3 sel → 3 singles + 3 dobles + 1 treble (7 apuestas)",
    "yankee":     "4 sel → 6 dobles + 4 trebles + 1 cuádruple (11 apuestas)",
    "lucky15":    "4 sel → 15 apuestas (todas combinaciones + singles)",
    "lucky31":    "5 sel → 31 apuestas (todas combinaciones)",
    "lucky63":    "6 sel → 63 apuestas (todas combinaciones)",
    "heinz":      "6 sel → 57 apuestas (dobles hasta séxtuple)",
    "superheinz": "7 sel → 120 apuestas (dobles hasta séptuple)",
    "goliath":    "8 sel → 247 apuestas (dobles hasta óctuple)",
}


# ─────────────────────────────────────────────────────────────────
# FUNCIONES MATEMÁTICAS CORE
# ─────────────────────────────────────────────────────────────────

def generar_parlays(indices: list, cuotas: list, min_k: int, max_k: int) -> list[dict]:
    """
    Genera todos los parlays posibles para las combinaciones
    desde min_k hasta max_k selecciones.

    Retorna lista de dicts con:
      - 'indices': qué selecciones incluye
      - 'cuota_combinada': producto de las cuotas
      - 'k': tamaño de la combinación
    """
    parlays = []
    for k in range(min_k, max_k + 1):
        for combo in combinations(indices, k):
            cuota_combinada = 1.0
            for i in combo:
                cuota_combinada *= cuotas[i]
            parlays.append({
                "indices": list(combo),
                "cuota_combinada": round(cuota_combinada, 4),
                "k": k,
            })
    return parlays


def calcular_retorno_escenario(
    parlays: list[dict],
    stake_por_parlay: float,
    aciertos: set,
) -> float:
    """
    Dado un conjunto de índices acertados, calcula el retorno total
    sumando solo los parlays donde TODOS sus índices están en 'aciertos'.
    """
    retorno = 0.0
    for p in parlays:
        if all(i in aciertos for i in p["indices"]):
            retorno += stake_por_parlay * p["cuota_combinada"]
    return round(retorno, 2)


def escenario_minimo_aciertos(
    parlays: list[dict],
    stake_por_parlay: float,
    stake_total: float,
    n_selecciones: int,
) -> int:
    """
    Devuelve el número mínimo de aciertos para no perder dinero
    (retorno >= stake_total), asumiendo el mejor conjunto posible
    de aciertos de ese tamaño.
    """
    for n_ac in range(1, n_selecciones + 1):
        # Mejor caso: los n_ac con las cuotas más altas
        indices = list(range(n_selecciones))
        for combo in combinations(indices, n_ac):
            aciertos = set(combo)
            retorno = calcular_retorno_escenario(parlays, stake_por_parlay, aciertos)
            if retorno >= stake_total:
                return n_ac
    return n_selecciones + 1  # nunca rompe par


def calcular_probabilidad_implicita(cuota: float) -> float:
    """Probabilidad implícita de la casa: 1 / cuota."""
    return round(1.0 / cuota * 100, 2)


def calcular_ev(
    cuota: float,
    prob_estimada: float,
    stake: float,
) -> float:
    """
    Valor esperado (EV) de una selección simple.
    prob_estimada: tu probabilidad real estimada (0.0 a 1.0)
    """
    return round(stake * (cuota * prob_estimada - 1), 2)


# ─────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

class CalculadoraSistema:
    """
    Calculadora de apuestas de sistema.

    Parámetros
    ----------
    cuotas : list[float]
        Cuotas decimales de cada selección (ej: [1.85, 2.10, 3.40])
    nombres : list[str], optional
        Nombres para cada selección (ej: ["Real Madrid G", "City G", "PSG G"])
    stake_total : float
        Monto total a invertir en CLP (u otra moneda)
    min_k : int
        Tamaño mínimo de combinación (usualmente 2)
    max_k : int
        Tamaño máximo de combinación (usualmente = len(cuotas))
    probs_estimadas : list[float], optional
        Tus probabilidades reales estimadas (0-1). Si se proveen,
        se calcula el EV de cada selección.
    """

    def __init__(
        self,
        cuotas: list[float],
        stake_total: float,
        nombres: Optional[list[str]] = None,
        min_k: int = 2,
        max_k: Optional[int] = None,
        probs_estimadas: Optional[list[float]] = None,
    ):
        assert len(cuotas) >= 2, "Se necesitan al menos 2 selecciones."
        assert all(c > 1.0 for c in cuotas), "Todas las cuotas deben ser > 1.0"
        assert stake_total > 0, "El stake total debe ser positivo."

        self.cuotas = cuotas
        self.n = len(cuotas)
        self.stake_total = stake_total
        self.nombres = nombres or [f"Selección {i+1}" for i in range(self.n)]
        self.min_k = max(1, min_k)
        self.max_k = max_k if max_k is not None else self.n
        self.probs_estimadas = probs_estimadas

        # Generar todos los parlays del sistema
        self.parlays = generar_parlays(
            list(range(self.n)), self.cuotas, self.min_k, self.max_k
        )
        self.num_parlays = len(self.parlays)
        self.stake_por_parlay = round(stake_total / self.num_parlays, 2)

    # ── Análisis por escenario ──────────────────────────────────

    def tabla_escenarios(self) -> list[dict]:
        """
        Genera una tabla con el retorno para cada cantidad posible de aciertos.
        Para cada cantidad de aciertos, muestra:
          - Mejor caso (los N aciertos con mejores cuotas)
          - Peor caso (los N aciertos con peores cuotas)
          - Caso promedio (media de todos los combos de ese tamaño)
        """
        indices = list(range(self.n))
        filas = []

        for n_ac in range(0, self.n + 1):
            combos_ac = list(combinations(indices, n_ac))
            retornos = []

            for combo in combos_ac:
                aciertos = set(combo)
                r = calcular_retorno_escenario(
                    self.parlays, self.stake_por_parlay, aciertos
                )
                retornos.append(r)

            if retornos:
                mejor = max(retornos)
                peor = min(retornos)
                promedio = round(sum(retornos) / len(retornos), 2)
            else:
                mejor = peor = promedio = 0.0

            ganancia_mejor = round(mejor - self.stake_total, 2)
            ganancia_peor = round(peor - self.stake_total, 2)
            ganancia_prom = round(promedio - self.stake_total, 2)

            filas.append({
                "aciertos": n_ac,
                "num_combos": len(combos_ac),
                "retorno_mejor": mejor,
                "retorno_peor": peor,
                "retorno_promedio": promedio,
                "ganancia_mejor": ganancia_mejor,
                "ganancia_peor": ganancia_peor,
                "ganancia_promedio": ganancia_prom,
                "roi_mejor": round(ganancia_mejor / self.stake_total * 100, 1),
                "roi_peor": round(ganancia_peor / self.stake_total * 100, 1),
            })

        return filas

    def detalle_parlays(self) -> list[dict]:
        """Devuelve todos los parlays individuales del sistema."""
        resultado = []
        for i, p in enumerate(self.parlays):
            sel_nombres = [self.nombres[j] for j in p["indices"]]
            resultado.append({
                "num": i + 1,
                "selecciones": " × ".join(sel_nombres),
                "k": p["k"],
                "cuota_combinada": p["cuota_combinada"],
                "stake": self.stake_por_parlay,
                "retorno_potencial": round(self.stake_por_parlay * p["cuota_combinada"], 2),
                "ganancia_potencial": round(
                    self.stake_por_parlay * p["cuota_combinada"] - self.stake_por_parlay, 2
                ),
            })
        return resultado

    def resumen(self) -> dict:
        """Resumen ejecutivo del sistema."""
        max_retorno = round(
            self.stake_por_parlay * sum(p["cuota_combinada"] for p in self.parlays
                                        if set(p["indices"]) == set(range(self.n))),
            2
        )
        # Retorno máximo: todos los aciertos
        aciertos_todos = set(range(self.n))
        max_retorno = calcular_retorno_escenario(
            self.parlays, self.stake_por_parlay, aciertos_todos
        )
        min_aciertos_rentable = escenario_minimo_aciertos(
            self.parlays, self.stake_por_parlay, self.stake_total, self.n
        )

        prob_imp = [calcular_probabilidad_implicita(c) for c in self.cuotas]

        return {
            "num_selecciones": self.n,
            "min_k": self.min_k,
            "max_k": self.max_k,
            "num_parlays": self.num_parlays,
            "stake_total": self.stake_total,
            "stake_por_parlay": self.stake_por_parlay,
            "max_retorno_posible": max_retorno,
            "max_ganancia_posible": round(max_retorno - self.stake_total, 2),
            "max_roi_posible": round((max_retorno - self.stake_total) / self.stake_total * 100, 1),
            "min_aciertos_para_rentabilidad": min_aciertos_rentable,
            "probabilidades_implicitas": prob_imp,
        }

    def analisis_ev(self) -> Optional[list[dict]]:
        """
        Análisis de valor esperado por selección si se proveyeron
        probabilidades estimadas propias.
        """
        if not self.probs_estimadas:
            return None
        resultado = []
        for i, (c, p, nombre) in enumerate(
            zip(self.cuotas, self.probs_estimadas, self.nombres)
        ):
            ev = calcular_ev(c, p, self.stake_por_parlay)
            prob_imp = calcular_probabilidad_implicita(c)
            edge = round((p * 100) - prob_imp, 2)
            resultado.append({
                "seleccion": nombre,
                "cuota": c,
                "prob_implicita_%": prob_imp,
                "prob_estimada_%": round(p * 100, 2),
                "edge_%": edge,
                "ev_clp": ev,
                "tiene_valor": edge > 0,
            })
        return resultado


# ─────────────────────────────────────────────────────────────────
# FUNCIONES DE RECOMENDACIÓN
# ─────────────────────────────────────────────────────────────────

def recomendar_sistema(cuotas: list[float], stake: float) -> list[dict]:
    """
    Evalúa múltiples configuraciones de sistema para las cuotas dadas
    y recomienda la óptima según equilibrio riesgo/retorno.
    """
    n = len(cuotas)
    opciones = []

    for min_k in range(2, n + 1):
        calc = CalculadoraSistema(
            cuotas=cuotas,
            stake_total=stake,
            min_k=min_k,
            max_k=n,
        )
        res = calc.resumen()
        escenarios = calc.tabla_escenarios()

        # Probabilidad de al menos min_aciertos (usa probs implícitas como proxy)
        probs_imp = [1 / c for c in cuotas]
        min_ac = res["min_aciertos_para_rentabilidad"]

        opciones.append({
            "sistema": f"{min_k}/{n}",
            "descripcion": f"Mínimo {min_k} de {n} selecciones por parlay",
            "num_parlays": res["num_parlays"],
            "stake_por_parlay": res["stake_por_parlay"],
            "max_retorno": res["max_retorno_posible"],
            "max_roi_%": res["max_roi_posible"],
            "min_aciertos_rentable": min_ac,
            "riesgo": "ALTO" if min_ac >= n - 1 else ("MEDIO" if min_ac >= n // 2 else "BAJO"),
        })

    return opciones


# ─────────────────────────────────────────────────────────────────
# PRESENTACIÓN EN CONSOLA
# ─────────────────────────────────────────────────────────────────

VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color_valor(valor: float, positivo_es_bueno: bool = True) -> str:
    """Colorea un valor según sea positivo o negativo."""
    if valor > 0:
        c = VERDE if positivo_es_bueno else ROJO
    elif valor < 0:
        c = ROJO if positivo_es_bueno else VERDE
    else:
        c = AMARILLO
    signo = "+" if valor > 0 else ""
    return f"{c}{signo}{valor:,.0f}{RESET}"


def formatear_clp(valor: float) -> str:
    return f"${valor:,.0f} CLP"


def imprimir_banner():
    print(f"\n{BOLD}{AZUL}{'═'*65}")
    print("   ⚽  CALCULADORA DE APUESTAS DE SISTEMA  ⚽")
    print(f"{'═'*65}{RESET}\n")


def imprimir_resumen(calc: CalculadoraSistema):
    res = calc.resumen()
    print(f"{BOLD}{CYAN}── RESUMEN DEL SISTEMA {res['min_k']}/{res['num_selecciones']} ──{RESET}")
    print(f"  Selecciones    : {res['num_selecciones']}")
    print(f"  Tamaño mínimo  : {res['min_k']} (dobles o más)")
    print(f"  Tamaño máximo  : {res['max_k']}")
    print(f"  Parlays totales: {BOLD}{res['num_parlays']}{RESET}")
    print(f"  Stake total    : {BOLD}{formatear_clp(res['stake_total'])}{RESET}")
    print(f"  Stake/parlay   : {formatear_clp(res['stake_por_parlay'])}")
    print(f"  Retorno máximo : {VERDE}{BOLD}{formatear_clp(res['max_retorno_posible'])}{RESET}")
    print(f"  ROI máximo     : {VERDE}{BOLD}+{res['max_roi_posible']}%{RESET}")
    min_ac = res["min_aciertos_para_rentabilidad"]
    ac_color = VERDE if min_ac <= res["num_selecciones"] // 2 + 1 else AMARILLO
    print(f"  Mín. aciertos para ROI > 0: {ac_color}{BOLD}{min_ac}/{res['num_selecciones']}{RESET}")


def imprimir_selecciones(calc: CalculadoraSistema):
    res = calc.resumen()
    print(f"\n{BOLD}{CYAN}── SELECCIONES ──{RESET}")
    header = f"  {'#':<3} {'Selección':<28} {'Cuota':>7} {'Prob. Impl.':>12}"
    print(header)
    print(f"  {'─'*55}")
    for i, (nombre, cuota, prob) in enumerate(
        zip(calc.nombres, calc.cuotas, res["probabilidades_implicitas"])
    ):
        print(f"  {i+1:<3} {nombre:<28} {cuota:>7.2f} {prob:>11.1f}%")


def imprimir_tabla_escenarios(calc: CalculadoraSistema):
    print(f"\n{BOLD}{CYAN}── TABLA DE ESCENARIOS (por cantidad de aciertos) ──{RESET}")
    n = calc.n
    stake = calc.stake_total

    header = (
        f"  {'Aciertos':<10} {'Combos':<8} "
        f"{'Retorno Mejor':>14} {'ROI Mejor':>10} "
        f"{'Retorno Peor':>14} {'ROI Peor':>10}"
    )
    print(header)
    print(f"  {'─'*68}")

    for fila in calc.tabla_escenarios():
        ac = fila["aciertos"]
        nc = fila["num_combos"]
        rm = fila["retorno_mejor"]
        rp = fila["retorno_peor"]
        roi_m = fila["roi_mejor"]
        roi_p = fila["roi_peor"]

        rm_str = f"{VERDE}{formatear_clp(rm)}{RESET}" if rm >= stake else f"{ROJO}{formatear_clp(rm)}{RESET}"
        rp_str = f"{VERDE}{formatear_clp(rp)}{RESET}" if rp >= stake else f"{ROJO}{formatear_clp(rp)}{RESET}"
        roi_m_str = f"{VERDE}+{roi_m}%{RESET}" if roi_m >= 0 else f"{ROJO}{roi_m}%{RESET}"
        roi_p_str = f"{VERDE}+{roi_p}%{RESET}" if roi_p >= 0 else f"{ROJO}{roi_p}%{RESET}"

        print(
            f"  {ac}/{n} aciert.   {nc:<8} "
            f"{rm_str:>24} {roi_m_str:>20} "
            f"{rp_str:>24} {roi_p_str:>20}"
        )


def imprimir_detalle_parlays(calc: CalculadoraSistema, max_mostrar: int = 20):
    detalle = calc.detalle_parlays()
    print(f"\n{BOLD}{CYAN}── DETALLE DE PARLAYS ({len(detalle)} total) ──{RESET}")
    if len(detalle) > max_mostrar:
        print(f"  {AMARILLO}(Mostrando primeros {max_mostrar} de {len(detalle)}){RESET}")
        detalle = detalle[:max_mostrar]

    header = (
        f"  {'#':<4} {'Selecciones':<42} "
        f"{'Cuota':>8} {'Stake':>12} {'Retorno':>12}"
    )
    print(header)
    print(f"  {'─'*82}")
    for p in detalle:
        nombre_trunc = p["selecciones"][:40]
        print(
            f"  {p['num']:<4} {nombre_trunc:<42} "
            f"{p['cuota_combinada']:>8.3f} "
            f"{formatear_clp(p['stake']):>12} "
            f"{VERDE}{formatear_clp(p['retorno_potencial'])}{RESET}"
        )


def imprimir_analisis_ev(calc: CalculadoraSistema):
    ev_data = calc.analisis_ev()
    if not ev_data:
        return
    print(f"\n{BOLD}{CYAN}── ANÁLISIS DE VALOR ESPERADO (EV) ──{RESET}")
    header = (
        f"  {'Selección':<28} {'Cuota':>6} "
        f"{'P.Impl.':>8} {'P.Est.':>8} {'Edge':>8} {'EV':>10}"
    )
    print(header)
    print(f"  {'─'*72}")
    for ev in ev_data:
        edge_str = f"{VERDE}+{ev['edge_%']}%{RESET}" if ev["tiene_valor"] else f"{ROJO}{ev['edge_%']}%{RESET}"
        ev_str = color_valor(ev["ev_clp"])
        print(
            f"  {ev['seleccion']:<28} {ev['cuota']:>6.2f} "
            f"{ev['prob_implicita_%']:>7.1f}% {ev['prob_estimada_%']:>7.1f}% "
            f"{edge_str:>18} {ev_str:>18}"
        )


def imprimir_recomendaciones(cuotas: list[float], stake: float):
    print(f"\n{BOLD}{CYAN}── COMPARATIVA DE SISTEMAS DISPONIBLES ──{RESET}")
    opciones = recomendar_sistema(cuotas, stake)

    header = (
        f"  {'Sistema':<10} {'Parlays':>8} {'$/Parlay':>12} "
        f"{'Retorno Máx.':>14} {'ROI Máx.':>10} "
        f"{'Mín.Ac.':>8} {'Riesgo':>8}"
    )
    print(header)
    print(f"  {'─'*75}")

    for op in opciones:
        r_color = VERDE if op["riesgo"] == "BAJO" else (AMARILLO if op["riesgo"] == "MEDIO" else ROJO)
        print(
            f"  {op['sistema']:<10} {op['num_parlays']:>8} "
            f"{formatear_clp(op['stake_por_parlay']):>12} "
            f"{VERDE}{formatear_clp(op['max_retorno'])}{RESET:>14} "
            f"{VERDE}+{op['max_roi_%']}%{RESET:>10} "
            f"{op['min_aciertos_rentable']:>8} "
            f"{r_color}{op['riesgo']:>8}{RESET}"
        )


# ─────────────────────────────────────────────────────────────────
# MODO INTERACTIVO
# ─────────────────────────────────────────────────────────────────

def modo_interactivo():
    """Flujo guiado por consola para ingresar datos."""
    imprimir_banner()
    print(f"{BOLD}¡Bienvenido! Ingresa tus selecciones paso a paso.{RESET}\n")

    # Sistemas nombrados
    print(f"{CYAN}Sistemas conocidos disponibles:{RESET}")
    for key, desc in NAMED_DESCRIPTIONS.items():
        print(f"  {BOLD}{key:<12}{RESET} → {desc}")
    print()

    # Cuotas
    cuotas_input = input(
        f"{BOLD}Ingresa las cuotas separadas por coma (ej: 1.85,2.10,3.40):\n> {RESET}"
    ).strip()
    cuotas = [float(x.strip()) for x in cuotas_input.split(",")]
    n = len(cuotas)

    # Nombres opcionales
    nombres_input = input(
        f"\n{BOLD}Nombres para cada selección (opcional, Enter para omitir):\n"
        f"(ej: RealMadridG,CityG,PSG_G)\n> {RESET}"
    ).strip()
    if nombres_input:
        nombres = [x.strip() for x in nombres_input.split(",")]
        if len(nombres) != n:
            nombres = [f"Sel.{i+1}" for i in range(n)]
    else:
        nombres = [f"Sel.{i+1}" for i in range(n)]

    # Probabilidades estimadas (EV)
    probs_input = input(
        f"\n{BOLD}¿Tienes probabilidades estimadas propias? (ej: 0.55,0.48,0.32)\n"
        f"(Enter para omitir análisis EV):\n> {RESET}"
    ).strip()
    probs = None
    if probs_input:
        probs = [float(x.strip()) for x in probs_input.split(",")]
        if len(probs) != n:
            probs = None
            print(f"{AMARILLO}Número incorrecto de probabilidades, se omite EV.{RESET}")

    # Stake
    stake_input = input(f"\n{BOLD}Monto total a invertir (CLP):\n> ${RESET}").strip()
    stake = float(stake_input.replace(".", "").replace(",", ""))

    # Sistema
    print(f"\n{BOLD}Configuración del sistema:{RESET}")
    print(f"  Tienes {n} selecciones. El sistema k/{n} juega todos los parlays de k selecciones.")
    print(f"  Sistema 2/{n} = todos los dobles (recomendado para seguridad)")
    print(f"  Sistema {n}/{n} = solo el parlay completo (máximo riesgo)")
    sistema_input = input(
        f"\n  Ingresa el sistema (ej: '2' para 2/{n}, o un nombre como 'trixie'):\n> "
    ).strip().lower()

    # Resolver sistema
    if sistema_input in NAMED_SYSTEMS:
        cfg = NAMED_SYSTEMS[sistema_input]
        if len(cuotas) != cfg["n"]:
            print(
                f"{ROJO}El sistema '{sistema_input}' requiere exactamente {cfg['n']} selecciones.{RESET}"
            )
            sys.exit(1)
        min_k = cfg["min_k"]
        max_k = cfg["n"]
    else:
        try:
            min_k = int(sistema_input)
        except ValueError:
            min_k = 2
        max_k = n

    # Calcular y mostrar
    calc = CalculadoraSistema(
        cuotas=cuotas,
        stake_total=stake,
        nombres=nombres,
        min_k=min_k,
        max_k=max_k,
        probs_estimadas=probs,
    )

    print(f"\n{'═'*65}")
    imprimir_selecciones(calc)
    imprimir_resumen(calc)
    imprimir_tabla_escenarios(calc)
    imprimir_recomendaciones(cuotas, stake)
    imprimir_detalle_parlays(calc, max_mostrar=15)
    if probs:
        imprimir_analisis_ev(calc)
    print(f"\n{AZUL}{'═'*65}{RESET}\n")


# ─────────────────────────────────────────────────────────────────
# CLI / ARGUMENTOS
# ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculadora de Apuestas de Sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python calculadora_sistema.py -c 1.85 2.10 3.40 -s 50000 -k 2
  python calculadora_sistema.py -c 1.80 2.20 2.80 3.50 -s 100000 -k 2 --sistema yankee
  python calculadora_sistema.py  (modo interactivo)
        """,
    )
    parser.add_argument(
        "-c", "--cuotas", nargs="+", type=float,
        help="Cuotas decimales de cada selección"
    )
    parser.add_argument(
        "-n", "--nombres", nargs="+", type=str,
        help="Nombres de cada selección"
    )
    parser.add_argument(
        "-s", "--stake", type=float,
        help="Monto total a invertir"
    )
    parser.add_argument(
        "-k", "--min-k", type=int, default=2,
        help="Tamaño mínimo de combinación (default: 2)"
    )
    parser.add_argument(
        "--sistema", type=str, choices=list(NAMED_SYSTEMS.keys()),
        help="Sistema nombrado (trixie, yankee, lucky15, etc.)"
    )
    parser.add_argument(
        "-p", "--probs", nargs="+", type=float,
        help="Probabilidades estimadas propias (0-1) para cálculo de EV"
    )
    parser.add_argument(
        "--detalle", action="store_true",
        help="Mostrar detalle completo de todos los parlays"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Modo interactivo si no hay cuotas
    if not args.cuotas:
        modo_interactivo()
        return

    cuotas = args.cuotas
    stake = args.stake or 50000.0
    nombres = args.nombres
    probs = args.probs

    # Resolver sistema
    if args.sistema and args.sistema in NAMED_SYSTEMS:
        cfg = NAMED_SYSTEMS[args.sistema]
        if len(cuotas) != cfg["n"]:
            print(
                f"{ROJO}El sistema '{args.sistema}' requiere {cfg['n']} selecciones.{RESET}"
            )
            sys.exit(1)
        min_k = cfg["min_k"]
        max_k = cfg["n"]
    else:
        min_k = args.min_k
        max_k = len(cuotas)

    calc = CalculadoraSistema(
        cuotas=cuotas,
        stake_total=stake,
        nombres=nombres,
        min_k=min_k,
        max_k=max_k,
        probs_estimadas=probs,
    )

    imprimir_banner()
    imprimir_selecciones(calc)
    imprimir_resumen(calc)
    imprimir_tabla_escenarios(calc)
    imprimir_recomendaciones(cuotas, stake)
    if args.detalle or len(calc.parlays) <= 20:
        imprimir_detalle_parlays(calc)
    if probs:
        imprimir_analisis_ev(calc)
    print(f"\n{AZUL}{'═'*65}{RESET}\n")


if __name__ == "__main__":
    main()
