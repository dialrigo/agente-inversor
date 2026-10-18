# Discusión y limitaciones



El resultado principal es negativo: el agente elegido no superó a comprar y mantener ni al aleatorio promedio en el held-out. En esta sección explicamos por qué.

## Reward hacking observado

Un agente de RL optimiza la recompensa que le damos, no la intención que tuvimos al diseñarla. Cuando las dos se separan, el agente encuentra atajos que cumplen la recompensa pero no su propósito. En el proyecto observamos un atajo distinto en cada versión.

- **v1 (retorno simple): sobreoperación.** Esperábamos que, en un activo alcista, v1 aprendiera a quedarse invertido. No fue así: cambió de posición 67 veces en validación y 94 en el held-out, y pagó 5.208 y 10.540 USD en costos, respectivamente. La recompensa simple solo cobra el costo de operar en el paso en que ocurre, de modo que perseguir movimientos de pocos días parece rentable durante el entrenamiento aunque no lo sea fuera de él. 

- **v2 (log − drawdown): refugio en efectivo.** La penalización castiga cada aumento del drawdown, y en efectivo el drawdown no puede crecer. El agente aprendió una política de "fuera por defecto": 79,7 % de los días en efectivo en validación y una exposición media del 18 % en el held-out (figura 10). Es el caso más claro de reward hacking del proyecto. Le pedimos controlar el riesgo y aprendió a evitarlo no participando, aunque eso signifique perder las subidas. El tramo del 13 de abril al 26 de mayo de 2017 lo muestra: el precio subió 18,2 % y el agente estuvo invertido, en promedio, solo el 5 % del capital (figura 11, sección 08).

El atajo de v2 tuvo además un efecto que no buscábamos. Con solo 18 % de exposición, su drawdown en el held-out (13,87 %) quedó casi igual al de comprar y mantener (15,36 %). El drawdown que sufrió no vino de estar invertido mucho tiempo, sino de 21 idas y vueltas concentradas en la turbulencia de febrero a mayo de 2018, cuando entraba tras una caída y la penalización lo empujaba a salir antes del rebote. Por eso reportamos siempre retorno, drawdown y costos juntos: mirando solo la recompensa, v2 parecería un agente prudente; con las tres métricas se ve que no logró el objetivo que justificó la penalización.

## No-estacionariedad 

El supuesto que el RL estándar no puede garantizar en finanzas es que el entorno de mañana se comporta como el de ayer. En nuestros datos, los tres periodos son tres regímenes distintos (figura 01):

| Periodo | Movimiento de GOOGL | Régimen |
|---|---|---|
| Entrenamiento 2009–2015 | +243,7 %, con caídas de hasta 30,4 % (figura 03) | Alcista con correcciones fuertes |
| Validación 2016 | +4,3 % | Lateral, con caída al inicio del año |
| Held-out 2017–2018 | +56,5 % | Alcista de baja volatilidad en 2017 y turbulento en febrero–mayo de 2018 |

La consecuencia más visible es que **el orden de las versiones se invirtió**. En validación, v2 ganó +8,99 % y v1 perdió −10,33 %; en el held-out, v2 ganó +3,46 % y v1 +31,99 %. Quedarse fuera del mercado fue una buena regla en un año lateral y una mala regla en un año alcista. No reajustamos nada al ver el held-out, porque elegir con el periodo de prueba invalidaría la evaluación (`docs/decisiones.md`, 2026-10-17), pero el resultado muestra que un solo año de validación no basta para elegir entre estrategias que dependen tanto del régimen.

La sección 08 encontró el mismo problema a nivel de los indicadores. En el entrenamiento, después de días con RSI superior a 78 el retorno de los 20 días siguientes fue en promedio +0,27 %, frente a +1,45 % en un día cualquiera; quedarse fuera tras una sobrecompra era razonable. En abril y mayo de 2017 el RSI llegó a 92–94 y el precio siguió subiendo durante semanas. La volatilidad también cambió de escala: promedió 15 % anual en 2017, por debajo de la mediana de entrenamiento (20,9 %), y 30,8 % en febrero–mayo de 2018. La relación entre lo que el agente observa y lo que pasa después no fue la misma que aprendió. Esto coincide con: colas pesadas, volatilidad agrupada en regímenes y poca dependencia lineal entre un día y el siguiente, todos visibles en nuestro análisis exploratorio (figuras 02 y 04).

## Datos escasos y riesgo de memorizar

El entrenamiento tiene 1.616 días. Con 150.000 pasos de DQN, el agente recorre ese periodo el equivalente a unas 93 veces, en ventanas de 252 días con inicio aleatorio. Las ventanas aleatorias cambian el orden en que ve los días, pero no aumentan la cantidad de situaciones distintas: hay solo una crisis de 2011, un solo split de 2014 y una sola secuencia de precios. Una red con dos capas de 64 neuronas puede aprender reglas que funcionan en esos días específicos sin que valgan en otros.

Los experimentos de validación muestran el efecto de tener tan pocos datos:

- **El resultado depende mucho de la semilla.** Con los mismos hiperparámetros, cuatro semillas de v2 dieron en validación entre −3,95 % y +6,12 %, con una media de +1,43 % ± 5,42 puntos. La dispersión entre semillas es mayor que la diferencia media frente a comprar y mantener (+4,24 %). El +8,99 % de la corrida oficial (semilla 42) es el extremo favorable de esa distribución, no un valor típico. 

- **Optuna se ajustó a la validación.** De 15 trials, solo uno terminó con recompensa positiva en 2016, sin un patrón claro por hiperparámetro. Reentrenado con 150.000 pasos y cuatro semillas, ese "mejor" candidato perdió en todas (−7,46 % en promedio). Elegir el máximo de muchas corridas ruidosas sobre un solo año selecciona suerte, no calidad.

Lo que sí fue estable entre semillas es la conducta: las cuatro semillas de v2 tuvieron menos drawdown que el mercado en validación y una exposición media de 16 % a 27 %. El agente aprende de forma consistente *cómo* comportarse (conservador), pero no *cuándo* ese comportamiento paga.

## Supuestos del simulador

El simulador simplifica la operación real (sección 04). Revisamos cada supuesto según hacia dónde mueve nuestros resultados:

| Supuesto | Efecto en los resultados |
|---|---|
| Ejecución al cierre del mismo día en que se observa (*market on close*) | **Optimista para el agente.** En la práctica, una decisión tomada con el cierre se ejecutaría en la apertura siguiente. Con 68 cambios de posición, v2 sería la estrategia más afectada; comprar y mantener casi no lo sería |
| Costo fijo de 0,1 %, sin *spread*, deslizamiento ni impacto en el precio | Optimista para las estrategias que operan mucho. Aun así, los costos ya fueron decisivos: v2 pagó 5.449 USD, más que su retorno, y el aleatorio pagó 19.102 USD en promedio. Con costos más realistas el agente quedaría todavía más lejos del baseline |
| El efectivo no genera intereses | **Pesimista para el agente.** v2 estuvo en efectivo la mayor parte del tiempo; con las tasas de corto plazo de 2017–2018, del orden de 1 % a 2 % anual en EE. UU., habría ganado algo por ese efectivo. No alcanza para cerrar una diferencia de 52,9 puntos, pero sí matiza la comparación con el aleatorio |
| Fracciones exactas, solo posiciones largas, sin apalancamiento | Neutral para la comparación, porque aplica igual a todas las estrategias; limita lo que el agente podría aprender (no puede ganar con las caídas) |
| Sin dividendos ni impuestos | GOOGL no pagó dividendos en el periodo; los impuestos sobre ganancias castigarían más a quien opera con frecuencia |

En conjunto, los supuestos favorecen al agente en ejecución y costos, y lo perjudican solo en los intereses del efectivo. Por eso el resultado negativo es robusto: un simulador más realista lo empeoraría, no lo revertiría.

## Sesgo de supervivencia (GOOGL)

Elegimos GOOGL, una empresa que hoy sabemos que fue de las más exitosas de su década. Estudiar solo activos que sobrevivieron y crecieron infla los resultados de las estrategias evaluadas sobre ellos. En nuestro caso, el sesgo opera en dos direcciones:

- **Favorece a comprar y mantener.** El activo subió 243,7 % en entrenamiento y 56,5 % en el held-out. En un activo así, cualquier estrategia que salga del mercado parte en desventaja, y el baseline pasivo se vuelve excepcionalmente difícil de superar. Con una acción elegida al azar, que pudo estancarse o quebrar, la comparación podría ser muy distinta.
- **Moldea lo que aprende el agente.** El agente nunca vio una caída prolongada sin recuperación, porque en GOOGL todas las caídas del periodo se recuperaron en 10 a 17 meses (sección 02). Lo que aprendió sobre riesgo está condicionado por un activo que siempre volvió a subir.

Por eso nuestras conclusiones valen para GOOGL en 2009–2018 y no se deben generalizar a "invertir en acciones".

## Qué cambiaríamos

Ordenamos las propuestas según el problema que resuelven:

1. **Recompensa diferencial frente a comprar y mantener.** Premiar al agente por el retorno *adicional* al del activo, como en el aprendizaje directo de estrategias de inversión, castigaría quedarse fuera cuando el mercado sube y no solo las caídas propias. Ataca directamente el refugio en efectivo de v2.

2. **Penalizar la rotación de forma explícita.** Un costo adicional por cambiar de posición en la recompensa, no solo el costo de transacción, reduciría las 21 idas y vueltas del held-out.

3. **Validación *walk-forward*.** Elegir la recompensa e hiperparámetros con varios años de validación sucesivos, y no con 2016 solo, para que la selección no dependa del régimen de un año particular.

4. **Más semillas en la selección.** Comparar versiones por la media de varias semillas, como hicimos en los experimentos de robustez, y no por una sola corrida.

5. **Más activos.** Entrenar y evaluar con varias acciones, incluidas algunas que no crecieron, para reducir el sesgo de supervivencia y darle al agente más situaciones distintas, de modo que memorizar un único recorrido deje de ser suficiente.

6. **Simulador más realista.** Ejecutar en la apertura siguiente, agregar intereses al efectivo y un *spread* variable, para que el resultado se acerque a lo que obtendría un inversionista real.