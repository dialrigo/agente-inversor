# Diseño del entorno de simulación

## Interfaz Gymnasium (reset / step) y por qué permite usar Stable-Baselines3

El simulador se implementó como la clase `InvestorEnv` (`src/rl_games_sb/investor_env.py`), que hereda de `gymnasium.Env` y respeta su contrato. Este contrato tiene cuatro piezas:

| Elemento | Definición en `InvestorEnv` |
|---|---|
| Espacio de observación | `Box(-5, 5, (8,), float32)`: los siete indicadores normalizados, en el orden de `investor_data.FEATURES`, y la posición actual |
| Espacio de acciones | `Discrete(3)`: la acción k fija la fracción objetivo `ACTIONS[k]` ∈ {0 %, 50 %, 100 %} |
| `reset(seed)` | Inicia el episodio con 100.000 USD en efectivo (posición 0) y devuelve el estado S_0 y `info = {"value": 100000}` |
| `step(a)` | Ejecuta la acción y devuelve `(S_{t+1}, R_{t+1}, terminated, truncated, info)`, con `info` = valor, posición, costo y fracción negociada |

Se optó por esta interfaz, en lugar de programar un ciclo de entrenamiento propio, porque Stable-Baselines3 entrena cualquier entorno que la cumpla. Por eso el DQN del proyecto (`MlpPolicy`) se conecta al simulador sin código adicional, y lo mismo vale para Optuna y para las herramientas de registro del repositorio base del curso. El entorno se registra en Gymnasium con un identificador por combinación de recompensa y periodo (`envs.py`): `Investor-<r>-v0` para entrenamiento y `Investor-<r>-val-v0` para validación, con `<r>` ∈ {`simple`, `log`, `log_dd`}. Por lo tanto, basta con cambiar el identificador en el archivo de configuración para entrenar con otra recompensa. El periodo de prueba no tiene identificador, a propósito. Además, `investor_eval.py` usa la misma clase para evaluar al agente y a los baselines, de modo que todas las estrategias se miden con las mismas reglas de costo, capital y ejecución.

## Cronología de un paso: cuándo se decide, a qué precio se ejecuta

Cada llamada a `step` corresponde a un día de negociación y sigue el esquema S_t → A_t → R_{t+1}, S_{t+1} descrito en la formulación:

1. **Observación.** Al cierre del día t, el agente ve los indicadores de t, calculados con precios hasta ese cierre, y la fracción w_t que tiene invertida en ese momento.
2. **Decisión y ejecución.** El agente elige la fracción objetivo a_t. La orden se ejecuta al precio de cierre de t (supuesto *market on close*) y en ese momento se descuenta el costo de transacción.
3. **Movimiento del precio.** El precio pasa de P_t a P_{t+1}, y el valor del portafolio se actualiza según la fracción elegida.
4. **Retroalimentación.** Con el nuevo valor V_{t+1} se calcula la recompensa R_{t+1} y se entrega la observación S_{t+1}.

El orden del código garantiza que el precio de t+1 solo se consulta después de que la acción quedó fija: `step` lee `prices[t+1]` para actualizar el valor, pero la acción ya llegó como argumento y la observación siguiente se construye con los indicadores de t+1. Así, el entorno no le entrega al agente información del día siguiente antes de que decida.

## Fórmula del valor del portafolio y del costo (0,1 %)

Sean V_t el valor del portafolio, w_t la fracción invertida antes de decidir, a_t la fracción objetivo y c = 0,001 la tasa de costo. El costo de la orden es proporcional al monto negociado:

$$\text{costo}_t = c \cdot |a_t - w_t| \cdot V_t$$

Con el retorno del activo r_{t+1} = P_{t+1}/P_t − 1, el valor al cierre siguiente es:

$$V_{t+1} = (V_t - \text{costo}_t)\,\bigl(1 + a_t \cdot r_{t+1}\bigr)$$

Es decir, el costo se descuenta primero y después la parte invertida gana o pierde con el precio, mientras que la parte en efectivo no cambia. Si el agente ya está en la fracción elegida, |a_t − w_t| = 0 y no paga nada.

**Ejemplo numérico** (prueba 4). Con 100.000 USD en efectivo, el agente elige el 100 % y el precio sube 1 %:

| Paso | Cálculo | Valor |
|---|---|---|
| Costo de entrar | 0,001 × \|1 − 0\| × 100.000 | 100 USD |
| Valor después del costo | 100.000 − 100 | 99.900 USD |
| Valor al cierre siguiente | 99.900 × (1 + 1 × 0,01) | 100.899 USD |
| Recompensa simple (×100) | (100.899 / 100.000 − 1) × 100 | 0,899 puntos porcentuales |

Como el costo ya está descontado de V_{t+1}, todas las variantes de recompensa, que se calculan a partir de ese valor, incluyen los costos de forma automática (véase la sección de diseño de la recompensa).

## Desplazamiento de la posición del 50 %

Después del movimiento del precio, la fracción invertida ya no es exactamente la que se eligió, porque la parte invertida cambia de valor y el efectivo no:

$$w_{t+1} = \frac{a_t\,(1 + r_{t+1})}{1 + a_t \cdot r_{t+1}}$$

Para a_t = 0 % y a_t = 100 % la fracción se mantiene exacta (0 y 1). Para a_t = 50 %, en cambio, se desplaza: si el precio sube 1 %, la fracción pasa a 0,5 × 1,01 / 1,005 ≈ 50,25 %; si baja, queda por debajo del 50 %. Por eso, mantener el 50 % exige un pequeño rebalanceo cada día: al volver a elegir la acción 1, el entorno negocia la diferencia de 0,25 % del capital, que cuesta alrededor de 0,25 USD sobre 100.000 USD. Acumulado en el periodo de entrenamiento, sostener el 50 % todo el tiempo paga 50 USD por la entrada inicial y 579,37 USD en rebalanceos (56,48 USD en validación), lo que coincide con la cifra de la formulación.

Este desplazamiento es la razón para incluir la posición w_t en el estado: el agente sabe cuánto tiene invertido y, por lo tanto, cuánto le cuesta cambiar de fracción.

## Episodios: ventanas de 252 días en train, periodo completo en val/test

| Periodo | Duración del episodio | Inicio |
|---|---|---|
| Entrenamiento (2009–2015, 1.616 días) | 252 decisiones, un año de negociación | Aleatorio, sorteado con el generador de Gymnasium (`np_random`), reproducible con la semilla |
| Validación (2016, 252 días) | El periodo completo: 251 decisiones | Primer día del periodo |
| Prueba (2017–2018, 418 días) | El periodo completo | Primer día del periodo |

En entrenamiento, cada `reset` sortea el día de inicio de una ventana de 252 decisiones. Así el agente recorre tramos alcistas, laterales y de caída en distinto orden, en lugar de memorizar un único recorrido de seis años. En validación y prueba, el episodio recorre el periodo completo desde el primer día, de modo que la evaluación es única y comparable entre estrategias. En todos los casos el episodio empieza con 100.000 USD en efectivo y posición 0. El episodio termina (`terminated = True`) al llegar al último día de la ventana o del periodo; no hay truncamiento por tiempo, porque la duración ya está definida por los datos. El último precio del periodo solo se usa como P_{t+1} de la última decisión.

## Pruebas automáticas y sus resultados

Las pruebas están en `tests/test_investor_env.py`, se ejecutan con `uv run pytest` y corren en el CI de GitHub (job `test` de `.github/workflows/ci.yml`) en cada *push* y en cada Pull Request. Ninguna abre el periodo de prueba: usan entrenamiento, validación o precios sintéticos.

| # | Prueba | Qué verifica | Resultado |
|---|---|---|---|
| 1 | `test_indicadores_sin_lookahead` | Recalcula los indicadores tras borrar todos los datos posteriores a una fecha y comprueba que los valores de esa fecha no cambian. Cinco fechas entre el 3 de agosto de 2009 y el 26 de septiembre de 2016, incluido el último día de entrenamiento | Pasa (5 casos) |
| 2 | `test_costo_entrar_al_100` | Pasar de 0 % a 100 % con 100.000 USD cuesta exactamente 100 USD (0,1 %) | Pasa |
| 3 | `test_efectivo_estable` | Durante 20 días en 0 % el valor se mantiene en 100.000 USD, sin costos y con recompensa 0, aunque el precio se mueva | Pasa |
| 4 | `test_paso_calculado_a_mano` | Con precios sintéticos 100 → 101: 100.000 → 99.900 → × 1,01 = 100.899 USD, recompensa 0,899 y posición 100 % | Pasa |
| 5 | `test_heldout_no_registrado` | Solo hay 6 entornos `Investor` registrados (3 recompensas × train/val) y ninguno usa el periodo de prueba | Pasa |
| 6 | `test_observacion_y_acciones` | La observación tiene 8 valores: los indicadores en el orden de `FEATURES` y la posición; las acciones son {0 %, 50 %, 100 %} | Pasa |
| 7 | `test_desplazamiento_del_50` | Con el precio +1 %, la fracción del 50 % pasa a ≈ 50,25 % y volver a elegir 50 % cobra un rebalanceo pequeño (entre 0 y 1 USD) | Pasa |

Resultado de la corrida local (Python 3.11, Windows 11): **11 pruebas aprobadas en 2,2 s** (`11 passed`). El lint (`ruff check .`) también pasa sin errores.

Las pruebas 1 y 5 sostienen dos de las salvaguardas contra el uso de información futura descritas en la formulación: los indicadores no dependen de precios posteriores a t, y el periodo de prueba no está disponible como entorno de entrenamiento ni de validación.

## Supuestos del simulador

El simulador simplifica la operación real. Estos supuestos se declaran porque afectan la interpretación de los resultados y se retoman en la discusión de limitaciones:

- **Ejecución al cierre de t (*market on close*).** El agente decide con el cierre de t y opera a ese mismo precio. Es optimista frente a ejecutar en la apertura de t+1, que sería lo factible si la decisión se toma después del cierre (registrado en `docs/decisiones.md`).
- **Costo proporcional fijo de 0,1 %** sobre el monto negociado, sin comisión mínima, sin diferencial de compra y venta (*spread*), sin deslizamiento (*slippage*) y sin impacto en el precio, porque se supone liquidez ilimitada.
- **El efectivo no genera intereses.** Estar en 0 % rinde exactamente cero, lo que favorece en algo a comprar y mantener.
- **Fracciones exactas.** Se puede invertir cualquier monto, como si se negociaran fracciones de acción, sin redondear a acciones enteras.
- **Solo posiciones largas y sin apalancamiento.** La exposición está entre 0 % y 100 %, en un único activo.
- **Sin dividendos ni impuestos.** GOOGL no pagó dividendos en el periodo, y la serie ya viene ajustada por el split de 2014.
- **Recompensa multiplicada por 100**, para expresarla en puntos porcentuales. Es un cambio de escala que no altera la política óptima y estabiliza el aprendizaje de la red.
