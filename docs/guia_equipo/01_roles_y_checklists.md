# Roles de revisión y checklists

Cada rol es dueño de un criterio de la rúbrica. Para obtener el punto completo hay que cumplir **todo** lo de la columna "Excelente (1.0)". Marca cada casilla en tu PR o issue de revisión.

| # | Rol | Responsable | Criterio de la rúbrica | Secciones del notebook |
|---|---|---|---|---|
| 0 | Integración y entrega | Diego Ríos (`dialrigo`) | Todos | Todo el repositorio |
| 1 | Formulación | Andrés Díaz (`andresdila`) | Formulación del problema (estado y acciones) | 3 |
| 2 | Entorno y lookahead | Nicolás Gamboa (`JnicolasGh`) | Implementación del entorno | 4, `investor_env.py`, `investor_data.py` |
| 3 | Recompensa | `janayajoo` | Diseño de la recompensa | 5, 6 |
| 4 | Evaluación | Lorena Valero (`LorenaValero20`) | Evaluación en datos no vistos y baselines | 8, 9, `investor_eval.py` |
| 5 | Reproducibilidad | Marlon Umbarila (`Marlon-Umbarila`) | Reproducibilidad (parte del criterio 5) | 1, 12, README, `CONFIGURACION_KERNEL.md` |
| 6 | Discusión e informe | Nataly Valbuena (`natavalbuenal`) | Discusión y reflexión (parte del criterio 5) | 10, 11, informe |

Los roles son una propuesta; Diego puede reasignarlos.

---

## 0 · Integración y entrega (Diego)

- [ ] Repo en GitHub con los 7 colaboradores
- [ ] Corrida oficial con `RETRAIN = True` y `results/` versionado
- [ ] Se integran los PR de revisión y, si cambia algo, se repite la corrida oficial
- [ ] Entrega en Moodle: link del repo, informe (PDF o Word) y ZIP del código como respaldo

## 1 · Formulación: estado y acciones (Andrés)

**Excelente:** estado claro con indicadores justificados y acciones discretas e interpretables, coherentes con el objetivo de inversión.

- [ ] Cada indicador de la tabla 3.1 tiene cálculo, ventana y justificación
- [ ] Están respondidas las preguntas 8 a 11 (qué observa, qué periodo, por qué, cómo evita el futuro)
- [ ] Están respondidas las preguntas 12 a 15 (acciones, significado económico, granularidad, qué no puede hacer)
- [ ] La justificación conecta con el EDA (ej.: la volatilidad se agrupa → `vol_20`)
- [ ] Se explica por qué la posición actual está en el estado (propiedad de Markov y costos)
- [ ] Revisar `investor_data.FEATURES` contra la tabla: mismos nombres y mismo orden

## 2 · Entorno y lookahead (Nicolás)

**Excelente:** entorno funcional, con costo por operar, *lookahead-safe* y consistente con la formulación.

- [ ] Leer `investor_env.step` línea por línea: la acción se fija **antes** de usar `prices[t+1]`
- [ ] Las 4 pruebas de la sección 4 pasan (lookahead, costo de \$100, efectivo estable, held-out no registrado)
- [ ] Revisar a mano un paso: con `V = 100.000`, entrar al 100 % y precio +1 % → `V ≈ 100.000 − 100 = 99.900 × 1,01 = 100.899`
- [ ] La normalización usa **solo** estadísticas de train (`_table()` en `investor_data.py`)
- [ ] El desplazamiento de la posición (drift) del 50 % se cobra como un pequeño rebalanceo: ¿está documentado?
- [ ] Revisar que el número de días de cada periodo coincide con la tabla de la sección 2
- [ ] Documentar en el notebook cualquier supuesto que encuentres (ejecución al cierre, sin intereses, etc.)

## 3 · Recompensa (janayajoo)

**Excelente:** recompensa justificada e iterada; compara al menos dos alternativas y discute el comportamiento que induce.

- [ ] Está explícito el ciclo completo: v1 → entrenamiento → comportamiento observado → problema → v2 → nuevo entrenamiento → comparación
- [ ] El texto de "problemas identificados" (secc. 5) se ajusta a **lo que realmente pasó** en la corrida oficial, no a lo que esperábamos
- [ ] La comparación v1 vs v2 usa **validación**, no el held-out
- [ ] Se discute el reward hacking de cada versión (quedarse siempre invertido / salirse del mercado)
- [ ] Las 4 preguntas del bloque "Comparación de las recompensas" (secc. 6) están respondidas
- [ ] Opcional: si hay tiempo, probar `Investor-log-v0` (log sin penalización) como tercera variante para separar el efecto del log y el de la penalización

## 4 · Evaluación y baselines (Lorena)

**Excelente:** evalúa en held-out sin reajustar, con retorno acumulado y máximo drawdown claros, y compara contra comprar y mantener y aleatorio.

- [ ] La versión final se elige en la celda de selección **antes** de la sección 8
- [ ] La tabla del held-out tiene: retorno acumulado, máximo drawdown y costos de las 4 estrategias
- [ ] El aleatorio se reporta con una semilla (en la curva) y como media de 20 semillas (en la tabla)
- [ ] Curva de capital, curva de drawdown y posiciones del agente, cada una con su interpretación
- [ ] Al menos un comportamiento inesperado analizado (secc. 9)
- [ ] Verificar a mano un número: el retorno de comprar y mantener ≈ retorno del activo − 0,1 %
- [ ] La respuesta a la pregunta central es explícita y honesta

## 5 · Reproducibilidad (Marlon)

**Excelente:** código reproducible, con semillas fijas e instrucciones de ejecución.

- [ ] En una máquina distinta a la de Diego: clonar, `uv sync`, prueba de humo y Run All **siguiendo solo el README** y `CONFIGURACION_KERNEL.md`
- [ ] Anotar cada paso que falló o que no estaba claro y corregir la guía
- [ ] Comparar tu tabla del held-out con la oficial: ¿iguales? ¿diferencias solo en decimales?
- [ ] Semillas: 42 en `random`, NumPy, PyTorch, el config de SB3 y el sampler de Optuna
- [ ] Ninguna celda depende de rutas personales (`C:\Users\...`)

## 6 · Discusión, reflexión e informe (Nataly)

**Excelente:** discusión honesta (limitaciones, reward hacking, no-estacionariedad) y reflexión personal.

- [ ] La sección 10 menciona reward hacking, no-estacionariedad, datos escasos, supuestos del simulador y sesgo de supervivencia, conectados con **nuestros** resultados
- [ ] Las 7 reflexiones individuales están completas (5 preguntas cada una, voz propia)
- [ ] El informe cubre los 11 puntos del enunciado (ver `03_estructura_informe.md`)
- [ ] Las cifras del informe coinciden con `results/metricas_heldout.csv`
- [ ] Referencias en APA 7 (Sutton y Barto 2018; Mnih et al. 2015 para DQN; Raffin et al. 2021 para SB3)
