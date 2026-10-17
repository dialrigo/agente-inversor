# Evaluación en datos no vistos frente a baselines

| Dueño | Verifica | Fuente | Rúbrica |
|---|---|---|---|
| Lorena Valero (`LorenaValero20`) | janayajoo | Secc. 8 · `results/09`–`10` · `metricas_heldout.csv` | **4** |

> **Estado:** las secciones 01 a 03 describen el protocolo y no dependen de los resultados. Las secciones 04 a 07 se completan con la **corrida oficial** (`results/metricas_heldout.csv` y figuras 09–10). Las líneas marcadas con ⏳ se reemplazan por las cifras oficiales.

## 01. Protocolo de evaluación

La evaluación final usa el periodo **held-out**, del 3 de enero de 2017 al 29 de agosto de 2018 (418 días de negociación). Ninguna etapa anterior lo usó. La separación temporal se respetó en todo el proyecto:

| Periodo | Fechas | Uso | ¿Se usó para decidir algo? |
|---|---|---|---|
| Entrenamiento | 2009 – 2015 | El agente aprende | Sí: pesos de la red |
| Validación | 2016 | Comparar recompensas, elegir la versión final y, opcionalmente, ajustar hiperparámetros con Optuna | Sí: versión final e hiperparámetros |
| Held-out | 2017 – 2018-08 | Evaluación final, una sola vez | **No** |

La versión del agente que se evalúa queda fijada en validación **antes** de abrir el held-out, con el criterio retorno acumulado / máximo drawdown (sección 6 del notebook). Después de ver el held-out no se modificó la recompensa, ni los hiperparámetros, ni la arquitectura. Además, el periodo held-out no está registrado como entorno de Gymnasium: solo puede abrirse desde `investor_eval.run(..., "test")`, lo que evita usarlo por accidente durante el entrenamiento o el ajuste.

## 02. Condiciones comunes

Todas las estrategias se evalúan en el mismo entorno (`InvestorEnv`) y bajo las mismas condiciones:

- **Capital inicial:** 100.000 USD, todo en efectivo el primer día.
- **Costo por operar:** 0,1 % del monto negociado en cada cambio de posición, incluidos los rebalanceos diarios que exige mantener el 50 %.
- **Ejecución:** al precio de cierre del día en que se decide.
- **Mismo periodo y mismos datos:** 418 días del held-out, con los mismos indicadores normalizados con estadísticas de entrenamiento.

Las estrategias comparadas son:

| Estrategia | Regla |
|---|---|
| Agente RL (versión elegida en validación) | Política greedy de DQN, sin exploración |
| Agente RL (la otra versión) | Se reporta como referencia; no participó en la selección después de ver el held-out |
| Comprar y mantener | 100 % invertido desde el primer día hasta el final |
| Aleatorio | Elige 0 %, 50 % o 100 % al azar cada día; se reporta una semilla (42) en la curva y la **media de 20 semillas** en la tabla, porque una sola semilla puede ser engañosamente buena o mala |

## 03. Métricas y verificación de su cálculo

| Métrica | Definición | Para qué sirve |
|---|---|---|
| Retorno acumulado | V_final / V_inicial − 1 | Cuánto creció el capital |
| Máximo drawdown | Mayor caída del valor desde un máximo previo | Riesgo de pérdida que habría sufrido un inversionista |
| Costos | Suma de los costos pagados por operar | Cuánto se fue en operar |
| Cambios de posición | Veces que cambia la posición objetivo (0/50/100 %) | Actividad del agente |
| Exposición media | Fracción promedio del capital invertida | Cuánto tiempo estuvo "en el mercado" |
| Sharpe anual | √252 · media / desviación de los retornos diarios | Retorno por unidad de volatilidad |

El cálculo de las métricas se verificó con pruebas automáticas (`tests/test_metrics.py`):

- **Serie hecha a mano:** con valores 100 → 120 → 90 → 110, el retorno es +10 % y el máximo drawdown 25 % (la caída de 120 a 90), tal como se calcula a mano.
- **Casos borde:** una serie que solo sube tiene drawdown 0, y una cartera en efectivo tiene Sharpe 0, sin división por cero.
- **Baseline comprar y mantener:** su valor final es exactamente 100.000 × (1 − 0,001) × P_final / P_inicial, es decir, el retorno del activo menos el costo de entrada. La prueba usa el periodo de validación para no abrir el held-out.
- **Agente aleatorio:** con la misma semilla produce exactamente la misma trayectoria, así que es reproducible.

## 04. Resultados en el held-out

⏳ Copiar la tabla de `results/metricas_heldout.csv` con dos decimales:

| Estrategia | Retorno acumulado | Máximo drawdown | Costos | Cambios de posición | Exposición media | Sharpe |
|---|---|---|---|---|---|---|
| RL v1 (simple) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| RL v2 (log + drawdown) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Comprar y mantener | ⏳ | ⏳ | ⏳ | 1 | 100 % | ⏳ |
| Aleatorio (media 20 semillas) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

Versión elegida en validación: ⏳

## 05. Curva de capital y de drawdown

*Figura 09 · `results/09_curva_capital_heldout.png`.*

⏳ Describir: (a) en qué tramos el agente se separa de comprar y mantener, hacia arriba o hacia abajo; (b) si sus caídas son más cortas o menos profundas que las del activo; (c) dónde queda el aleatorio y por qué los costos explican buena parte de su resultado.

## 06. Posiciones del agente en el tiempo

*Figura 10 · `results/10_posiciones_heldout.png`.*

⏳ Describir: (a) qué acción usa más el agente; (b) si sale del mercado antes de las caídas reales o en momentos sin relación con el precio; (c) si cambia de posición con frecuencia, lo que encarece la estrategia.

## 07. Respuesta a la pregunta central

*¿Puede un agente de RL aprender una estrategia de inversión que se comporte mejor que comprar y mantener o que un agente aleatorio, en un periodo que nunca vio?*

⏳ Responder en tres frases, con las cifras de la tabla: (1) frente a comprar y mantener en retorno; (2) frente a comprar y mantener en riesgo (drawdown); (3) frente al aleatorio. Si el agente no supera a comprar y mantener, decirlo de forma explícita y conectar con la discusión: en el held-out el activo subió con fuerza y, en un mercado así, cualquier salida del mercado tiene un costo de oportunidad alto.
