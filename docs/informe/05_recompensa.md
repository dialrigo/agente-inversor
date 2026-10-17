# Diseño e iteración de la recompensa

| Dueño | Verifica | Fuente | Rúbrica |
|---|---|---|---|
| janayajoo | Nicolás Gamboa | Secc. 5–6 · `results/05`–`08` | **3** |

## v1: retorno simple, justificación

En cada paso *t* el agente elige una fracción objetivo a ∈ {0; 0,5; 1} del capital invertido en GOOGL. Con V el valor del portafolio, w la fracción invertida actual y c = 0,1 % el costo por monto negociado, el entorno calcula:

- Monto negociado: traded = |a − w|
- Costo: costo = c · traded · V
- Retorno del activo: r = P(t+1) / P(t) − 1
- Nuevo valor: V' = (V − costo) · (1 + a · r)

Los costos se descuentan antes del retorno, por lo que **las tres recompensas ya son netas de costos**. En todas, la recompensa se multiplica por 100 (puntos porcentuales).

| Versión | Recompensa por paso |
|---|---|
| v1 · simple | R = 100 · (V'/V − 1) |
| v2 · log − drawdown | R = 100 · [ ln(V'/V) − λ · max(0, DD_después − DD_antes) ] |
| v3 · log (control) | R = 100 · ln(V'/V) |

donde DD_antes = 1 − V/pico, DD_después = 1 − V'/max(pico, V'), el pico es el máximo valor alcanzado en el episodio y λ = 1 en v2. v3 es exactamente v2 con λ = 0.

v1 premia el retorno porcentual diario del portafolio. Se eligió como punto de partida por ser la formulación más directa: lo que el agente gana en el día es lo que recibe como recompensa, y sirve de línea base para detectar qué falla.

## Entrenamiento v1 y comportamiento observado en validación

Configuración: DQN, red MLP 64×64, 150.000 pasos, semilla 42, entrenado en 2009–2015 con episodios de 252 días de inicio aleatorio y evaluado en 2016 (validación) con un episodio determinista.

En validación (corrida oficial del notebook), v1 obtuvo **−10,33 %** de retorno (comprar y mantener: +4,24 %), con 67 cambios de posición (cerca del 27 % de los días), 5.208 USD en costos, exposición media de 57,2 % y máximo drawdown de 15,9 %. Pasó 54,2 % del tiempo al 100 % invertido, 39,8 % en efectivo y 6,0 % al 50 %.

## Problemas identificados

El agente de v1 **sobreopera**: cambia de posición más de un día de cada cuatro y paga costos que se comen el resultado (más de 5 % del capital inicial). v1 no penaliza el riesgo más allá del costo de operar, y el agente termina persiguiendo movimientos de corto plazo aprendidos en 2009–2015 que no se sostienen en 2016. Su drawdown (15,9 %) es incluso mayor que el del mercado (13,5 %), sin compensación en retorno.

## v2: log con penalización de drawdown, justificación

v2 introduce dos cambios respecto a v1:

1. **Retorno logarítmico.** Los log-retornos se suman en el tiempo: la suma de la recompensa de un episodio es ln(V_final / V_inicial), de modo que maximizar la recompensa acumulada equivale a maximizar la riqueza final. El retorno simple no tiene esa propiedad.
2. **Penalización por aumento del drawdown.** Se resta λ · max(0, DD_después − DD_antes): solo se castigan los días en que el portafolio se hunde más respecto a su máximo, y no los días de recuperación. La intención es desincentivar el riesgo que v1 no castigaba.

## Variante de control: log sin penalización

Con v1 → v2 cambian dos cosas a la vez (log y penalización), así que no se sabe cuál produce el efecto. v3 (`configs/investor_dqn_log.yaml`) usa solo el log, es decir, v2 con λ = 0, con los mismos hiperparámetros y semilla. Así se aísla la contribución de cada cambio.

## Tabla comparativa de las 3 variantes en validación

Corrida exploratoria, previa a la corrida oficial: un episodio determinista en 2016, semilla 42, 150.000 pasos, mismos hiperparámetros en las tres. Es la única corrida que compara las tres variantes entre sí, por eso se usa para aislar el efecto del log; v3 no forma parte del notebook oficial. Las cifras de v1 y v2 que sustentan la selección son las de la corrida oficial (ver "Versión elegida y criterio").

| Estrategia | Retorno | Máx. drawdown | Costos (USD) | Cambios de posición | Exposición media | Sharpe anual | Retorno / drawdown |
|---|---|---|---|---|---|---|---|
| v1 · simple | −7,72 % | 14,50 % | 5.578 | 70 | 58,0 % | −0,46 | −0,53 |
| v2 · log − drawdown | **+8,48 %** | **6,27 %** | 2.915 | 32 | 19,3 % | **0,98** | **1,35** |
| v3 · log | −6,69 % | 16,08 % | 5.926 | 71 | 54,6 % | −0,39 | −0,42 |
| Comprar y mantener | +4,24 % | 13,53 % | 100 | 1 | 100 % | 0,31 | 0,31 |

Tiempo en cada posición (0 % / 50 % / 100 % invertido):

| Estrategia | 0 % | 50 % | 100 % |
|---|---|---|---|
| v1 | 39,3 % | 6,0 % | 54,8 % |
| v2 | 79,4 % | 2,8 % | 17,9 % |
| v3 | 43,3 % | 4,8 % | 52,0 % |
| Comprar y mantener | 0,4 % | 0,0 % | 99,6 % |

**Lectura.**

- **v1 y v3 se comportan casi igual** (retornos de −7,7 % y −6,7 %, unos 70 cambios de posición, exposición de 55 a 58 %). Pasar de retorno simple a log, por sí solo, no cambia la conducta: con retornos diarios pequeños ambos valen casi lo mismo, ya que ln(1 + x) ≈ x. Con una sola semilla, la diferencia de un punto entre ellos queda dentro del ruido y no se interpreta como un efecto del log.
- **Lo que cambia el comportamiento es la penalización por drawdown.** v2 opera menos de la mitad (32 cambios frente a 70), paga la mitad de costos, reduce el drawdown a menos de la mitad y obtiene el mayor retorno y Sharpe.

## Reward hacking de cada versión

Las explicaciones siguientes son hipótesis consistentes con los datos, no pruebas causales.

- **v1 y v3 (sobreoperación).** No se observa un atajo claro, sino ajuste a ruido: el agente cambia de posición con frecuencia persiguiendo señales de corto plazo y los costos de transacción erosionan el resultado.
- **v2 (refugio en efectivo).** Como la penalización se suma en cada aumento del drawdown, aunque el portafolio se recupere después, estar invertido en días volátiles tiene un costo esperado y el efectivo no tiene ninguno. El agente pasa 79 % del tiempo en efectivo. Es un sesgo conservador inducido por la recompensa: λ = 1 puede volverlo demasiado cauto en mercados alcistas. Además, la penalización depende del pico y del valor del portafolio, variables que la observación del agente no incluye (solo ve los 7 indicadores y su posición), así que aprende una regla aproximada y no el control exacto del drawdown.

## Versión elegida y criterio (antes de abrir el held-out)

El criterio de selección se fijó antes de abrir el held-out (ver `docs/decisiones.md`, 2026-10-12): el mayor **ratio retorno / máximo drawdown en validación (2016)**. La selección se hizo en la corrida oficial del notebook (sección 6), con estas cifras en validación:

| Estrategia (corrida oficial, validación 2016) | Retorno | Máx. drawdown | Costos (USD) | Cambios de posición | Exposición media | Sharpe anual | Retorno / drawdown |
|---|---|---|---|---|---|---|---|
| v1 · simple | −10,33 % | 15,88 % | 5.208 | 67 | 57,2 % | −0,64 | −0,65 |
| v2 · log − drawdown | **+8,99 %** | **8,61 %** | 3.097 | 32 | 19,3 % | **1,02** | **1,04** |
| Comprar y mantener | +4,24 % | 13,53 % | 100 | 1 | 100 % | 0,31 | 0,31 |
| Aleatorio (media 20 semillas) | −9,17 % | 13,80 % | 10.753 | 168 | 51,6 % | −0,67 | −0,66 |

Con ese criterio, v2 obtiene 1,04 (8,99 % / 8,61 %), frente a −0,65 de v1 y 0,31 de comprar y mantener, así que se elige **v2**. La corrida exploratoria da el mismo orden (1,35 para v2, −0,53 para v1 y −0,42 para v3). Como apoyo, v2 es además la única variante que supera a comprar y mantener en retorno (+9,0 % frente a +4,2 %), tiene el mejor Sharpe (1,02) y paga cerca del 60 % de los costos de v1 (3.097 frente a 5.208 USD). Con retornos negativos el ratio pierde sentido (en la corrida exploratoria v3 queda por encima de v1 solo porque pierde menos por cada punto de drawdown), pero ninguna de las dos compite con v2.

**Salvedades.**

1. Es un solo año, un solo episodio y una semilla. La robustez entre semillas se reporta en `docs/experimentos/optuna_y_semillas.md`.
2. La elección se hizo mirando 2016, así que el resultado de v2 en validación está algo inflado por selección. El held-out (2017–2018) existe para medir eso.
3. v2 supera al mercado con 19 % de exposición media; puede ser acierto de oportunidad en 2016 y no una ventaja general.
4. Con la misma semilla y los mismos hiperparámetros, la corrida exploratoria y la oficial dan cifras distintas (por ejemplo, v2: +8,48 % frente a +8,99 %), probablemente por diferencias numéricas entre computadores y versiones de librerías. El orden de las variantes se mantiene en ambas, así que la elección de v2 no depende de cuál se use.