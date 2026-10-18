# Evaluación en datos no vistos frente a baselines

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

## 04. Versión evaluada (elegida en validación)

Antes de abrir el held-out, la celda de selección del notebook comparó las dos versiones en **validación (2016)** con el criterio retorno acumulado / máximo drawdown:

| Estrategia (validación 2016) | Retorno | Máx. drawdown | Costos (USD) | Cambios de posición | Exposición media | Sharpe | Retorno / drawdown |
|---|---|---|---|---|---|---|---|
| RL v1 (simple) | −10,33 % | 15,88 % | 5.208 | 67 | 57,2 % | −0,64 | −0,65 |
| **RL v2 (log + drawdown)** | **+8,99 %** | **8,61 %** | 3.097 | 32 | 19,3 % | **1,02** | **1,04** |
| Comprar y mantener | +4,24 % | 13,53 % | 100 | 1 | 100 % | 0,31 | 0,31 |
| Aleatorio (media 20 semillas) | −9,17 % | 13,80 % | 10.753 | 168 | 51,6 % | −0,67 | −0,66 |

La versión elegida para el held-out fue **RL v2 (log + drawdown)**. En validación superó a comprar y mantener en retorno (+8,99 % frente a +4,24 %) y redujo el drawdown a casi la mitad (8,6 % frente a 13,5 %), con el agente en efectivo el 79,7 % de los días. Esta decisión quedó fija antes de ver el held-out.

## 05. Resultados en el held-out (2017 – 2018)

*Fuente: `results/metricas_heldout.csv`.*

| Estrategia | Retorno acumulado | Máximo drawdown | Costos (USD) | Cambios de posición | Exposición media | Sharpe |
|---|---|---|---|---|---|---|
| **RL v2 (log + drawdown)** · elegida | **+3,46 %** | **13,87 %** | 5.449 | 68 | 18,0 % | 0,26 |
| RL v1 (simple) · referencia | +31,99 % | 16,57 % | 10.540 | 94 | 61,4 % | 1,21 |
| Comprar y mantener | +56,36 % | 15,36 % | 100 | 1 | 100 % | 1,45 |
| Aleatorio (media 20 semillas) | +4,95 % | 14,72 % | 19.102 | 278 | 51,1 % | 0,27 |
| Aleatorio (semilla 42, la de la curva) | +31,51 % | 8,09 % | 22.124 | 278 | 49,4 % | 1,32 |

Lectura de la tabla:

- **Retorno.** El agente elegido ganó +3,46 %, frente a +56,36 % de comprar y mantener: quedó **52,9 puntos** por debajo. Incluso quedó por debajo del aleatorio promedio (+4,95 %).
- **Riesgo.** Su máximo drawdown (13,87 %) es apenas 1,5 puntos menor que el de comprar y mantener (15,36 %), pese a estar invertido solo el 18 % del tiempo. Reducir la exposición a una quinta parte no redujo el riesgo en la misma proporción. La sección 08 analiza por qué.
- **Costos.** Pagó 5.449 USD en costos, el 5,4 % del capital inicial y más que todo su retorno. Antes de costos su resultado habría sido cercano a +9 %, todavía muy lejos del baseline.
- **Sharpe.** 0,26, prácticamente igual al del aleatorio promedio (0,27). En términos de retorno por unidad de riesgo, el agente no se distingue del azar en este periodo.
- **El aleatorio con una sola semilla engaña.** La semilla 42 obtuvo +31,5 % y el menor drawdown de la tabla (8,1 %), pero el promedio de 20 semillas es +4,95 %. Por eso la comparación se hace contra el promedio, no contra una sola trayectoria.
- **Comprobación del baseline.** El activo subió 56,51 % en el periodo; comprar y mantener rindió 56,36 %, que es exactamente el retorno del activo después del costo de entrada del 0,1 %: 1,5651 × 0,999 − 1 = 0,5636.

## 06. Curva de capital y de drawdown

*Figura 09 · `results/09_curva_capital_heldout.png`.*

- **2017 (enero a diciembre).** GOOGL subió de forma casi continua y comprar y mantener llegó a ~132.000 USD. El agente v2 se quedó plano alrededor de 100.000 USD: estuvo en efectivo casi todo el año y solo entró en pocos días aislados.
- **Enero de 2018.** El activo tuvo su tramo más fuerte (comprar y mantener superó los 146.000 USD) y el agente siguió fuera del mercado.
- **Febrero a mayo de 2018.** El mercado se volvió turbulento y el agente empezó a entrar y salir. Ahí se concentró **todo su drawdown**: su valor cayó de ~106.000 a ~92.000 USD entre marzo y finales de abril.
- **Junio a agosto de 2018.** Recuperó parte de la pérdida y cerró en 103.464 USD.

La curva de drawdown muestra la diferencia de fondo. El drawdown de comprar y mantener se reparte en varios episodios cortos que se recuperan rápido. El del agente es casi nulo durante 14 meses y luego aparece de golpe en el periodo más volátil.

## 07. Posiciones del agente en el tiempo

*Figura 10 · `results/10_posiciones_heldout.png`.*

- **Acción dominante: efectivo.** El agente estuvo al 0 % la mayor parte del periodo, con una exposición media del 18 %. Es el mismo patrón que en validación (19,3 %), así que el comportamiento es estable entre periodos. Lo que cambió fue el mercado.
- **Entradas cortas y aisladas.** En 2017 solo tomó posiciones de 50 % o 100 % durante pocos días y salió rápido, sin acompañar la tendencia alcista del año.
- **Rotación concentrada en la turbulencia.** Entre marzo y mayo de 2018 cambió de posición decenas de veces. En todo el held-out hubo 21 idas y vueltas (A → B → A en tres días), la mayoría en ese periodo. Esas operaciones explican buena parte de los 5.449 USD en costos.
- **Comparación con v1.** La versión v1, no elegida, estuvo invertida el 61 % del tiempo, ganó +32 % y siguió mejor la tendencia, a cambio de un drawdown mayor (16,6 %) y del doble de costos.

## 08. Respuesta a la pregunta central

*¿Puede un agente de RL aprender una estrategia de inversión que se comporte mejor que comprar y mantener o que un agente aleatorio, en un periodo que nunca vio?*

**En este experimento, no.** El agente elegido (v2) obtuvo +3,46 % frente a +56,36 % de comprar y mantener. Redujo el máximo drawdown en solo 1,5 puntos (13,87 % frente a 15,36 %) y no superó al aleatorio promedio ni en retorno (+4,95 %) ni en Sharpe (0,26 frente a 0,27). Su único resultado mejor que el azar es el costo de operar, que fue menor.

Hay un hallazgo adicional que debe quedar explícito: la versión **descartada en validación (v1) habría sido mucho mejor en el held-out** (+32 %). No la usamos ni reajustamos nada al verlo, porque elegir la versión con el periodo de prueba invalidaría la evaluación. Que el orden de las versiones se invierta entre 2016 y 2017–2018 es una muestra directa de **no-estacionariedad**:

- En 2016 el activo apenas subió (+4,3 %) y tuvo caídas al inicio del año, de modo que quedarse fuera del mercado fue rentable.
- En 2017–2018 hubo un mercado alcista fuerte (+56 %), donde quedarse fuera tiene un costo de oportunidad enorme.

Un solo año de validación no basta para elegir con confianza entre estrategias que dependen tanto del régimen de mercado (ver la discusión en la sección 09).
