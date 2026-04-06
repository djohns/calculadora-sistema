# ⚽ Calculadora de Apuestas de Sistema

Herramienta Python de uso personal para calcular y optimizar **apuestas de sistema** en casas como Betano.

---

## ¿Qué es una apuesta de sistema?

Una apuesta de sistema `k/N` toma **N selecciones** y genera **todas las combinaciones posibles de k de ellas**, cada una como un parlay independiente. A diferencia del parley clásico (donde todas deben acertar), aquí **ganas parcialmente aunque fallen algunas selecciones**.

**Ejemplo**: sistema `2/3` con 3 selecciones genera 3 dobles (C(3,2) = 3 parlays).

---

## Características

- ✅ Sistemas personalizados `k/N` (cualquier combinación)
- ✅ Sistemas nombrados: Trixie, Patent, Yankee, Lucky 15/31/63, Heinz y más
- ✅ Tabla de escenarios (retorno por cantidad de aciertos: mejor/peor/promedio)
- ✅ Comparativa automática de todos los sistemas posibles
- ✅ Análisis de EV (valor esperado) si tienes probabilidades propias estimadas
- ✅ Detalle de cada parlay individual
- ✅ Modo interactivo y modo CLI por argumentos
- ✅ Sin dependencias externas (solo Python estándar)

---

## Instalación

```bash
git clone https://github.com/tu-usuario/sistema-apuestas.git
cd sistema-apuestas
# No requiere pip install — solo Python 3.9+
```

---

## Uso

### Modo interactivo (recomendado para empezar)
```bash
python calculadora_sistema.py
```
Te guía paso a paso: cuotas, nombres, stake, sistema.

---

### Modo CLI

```bash
# Sistema 2/3 con 3 selecciones, $50.000 CLP
python calculadora_sistema.py -c 1.85 2.10 3.40 -s 50000 -k 2

# Con nombres para cada selección
python calculadora_sistema.py \
  -c 1.85 2.10 3.40 \
  -n "Real Madrid G" "City G" "PSG G" \
  -s 50000 -k 2

# Sistema nombrado Yankee (4 selecciones)
python calculadora_sistema.py \
  -c 1.80 2.20 2.80 3.50 \
  -s 100000 \
  --sistema yankee

# Con probabilidades propias para análisis de EV
python calculadora_sistema.py \
  -c 1.85 2.10 3.40 \
  -s 50000 -k 2 \
  -p 0.57 0.50 0.32

# Mostrar detalle completo de todos los parlays
python calculadora_sistema.py -c 1.85 2.10 3.40 -s 50000 -k 2 --detalle
```

---

## Sistemas nombrados disponibles

| Sistema      | Selecciones | Descripción                                     | Apuestas |
|-------------|-------------|------------------------------------------------|----------|
| `trixie`    | 3           | Todos los dobles + 1 treble                    | 4        |
| `patent`    | 3           | Singles + dobles + treble                      | 7        |
| `yankee`    | 4           | Dobles + trebles + 1 cuádruple                 | 11       |
| `lucky15`   | 4           | Todas las combinaciones (inc. singles)         | 15       |
| `lucky31`   | 5           | Todas las combinaciones                        | 31       |
| `lucky63`   | 6           | Todas las combinaciones                        | 63       |
| `heinz`     | 6           | Dobles hasta séxtuple                          | 57       |
| `superheinz`| 7           | Dobles hasta séptuple                          | 120      |
| `goliath`   | 8           | Dobles hasta óctuple                           | 247      |

---

## Lógica matemática

```
Probabilidad implícita: p_i = 1 / cuota_i
Cuota combinada parlay: Q = ∏(cuotas_seleccionadas)
Stake por parlay: s = stake_total / num_parlays
Retorno si aciertas combo C: s × Q_C
Ganancia neta: retorno - stake_total
ROI: (ganancia_neta / stake_total) × 100
EV selección: stake × (cuota × prob_real - 1)
Edge: prob_real% - prob_implícita%
```

---

## Output de ejemplo

```
── RESUMEN DEL SISTEMA 2/3 ──
  Selecciones    : 3
  Parlays totales: 3
  Stake total    : $50,000 CLP
  Stake/parlay   : $16,667 CLP
  Retorno máximo : $207,334 CLP
  ROI máximo     : +314.7%
  Mín. aciertos para ROI > 0: 2/3

── TABLA DE ESCENARIOS ──
  0/3 aciert.   1 combos    $0 CLP      -100%    $0 CLP      -100%
  1/3 aciert.   3 combos    $30,834 CLP  -38%    $30,834 CLP  -38%
  2/3 aciert.   3 combos    $65,167 CLP  +30%    $57,167 CLP  +14%
  3/3 aciert.   1 combos    $207,334 CLP +315%   $207,334 CLP +315%
```

---

## Uso programático (como módulo)

```python
from calculadora_sistema import CalculadoraSistema

calc = CalculadoraSistema(
    cuotas=[1.85, 2.10, 3.40],
    stake_total=50_000,
    nombres=["Real Madrid G", "City G", "PSG G"],
    min_k=2,
    probs_estimadas=[0.57, 0.50, 0.32],  # opcional
)

resumen = calc.resumen()
escenarios = calc.tabla_escenarios()
parlays = calc.detalle_parlays()
ev = calc.analisis_ev()
```

---

## Estrategia recomendada

1. **Selecciona 3-5 partidos** con cuotas entre 1.70 y 2.50 (más predecibles)
2. **Usa sistema 2/N** para seguridad (rentable con solo 2 aciertos)
3. **Verifica el EV** con tus probabilidades estimadas antes de apostar
4. **Nunca apuestes más del 5%** de tu bankroll total por sesión
5. **Lleva registro** de tus aciertos reales para calibrar tu modelo

---

## Aviso

Esta herramienta es de uso personal y educativo. Las apuestas deportivas implican riesgo de pérdida económica. Juega responsablemente.
