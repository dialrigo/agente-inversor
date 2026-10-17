# Comportamiento inesperado del agente

| Dueño | Verifica | Fuente | Rúbrica |
|---|---|---|---|
| Lorena Valero (`LorenaValero20`) | janayajoo | Secc. 9 · `results/11` | 4 |

## 01. Cómo se identificó el comportamiento inesperado

En lugar de elegir a mano un episodio "interesante", lo que podría sesgar el análisis, el tramo se buscó de forma sistemática. Para cada día del held-out se calculó la diferencia entre el retorno logarítmico de 30 días hábiles del agente elegido (v2) y el de comprar y mantener. El tramo analizado es el de **mayor desventaja** del agente. Como diagnóstico adicional se contaron las **idas y vueltas** en todo el held-out: secuencias A → B → A en tres días consecutivos, en las que el agente cambia de decisión y vuelve atrás pagando dos veces el costo de operar.

## 02. Tramo de peor desempeño frente a comprar y mantener

*Figura 11 · `results/11_anomalia.png`.*

| Dato | Valor |
|---|---|
| Fechas del tramo | 13 de abril → 26 de mayo de 2017 (30 días hábiles) |
| Desventaja frente a comprar y mantener | −16,3 puntos log |
| Movimiento del precio en el tramo | **+18,2 %** (de ~840 a ~993 USD) |
| Exposición media del agente | **5 %** |
| Cambios de posición en el tramo | 4 |
| Idas y vueltas en todo el held-out | 21 |

## 03. Qué hizo el agente y qué vio en el estado

En el tramo de mayor subida de 2017 el agente estuvo **prácticamente todo el tiempo en efectivo**. Solo entró al 50 % dos veces y por dos días cada vez: el 18–19 de abril, justo antes de que comenzara el rally, y del 22 al 24 de mayo, cuando el precio ya estaba cerca del máximo del tramo. Las dos veces salió enseguida. A finales de marzo había hecho lo mismo: entró al 50 % durante una caída del precio (de ~870 a ~840 USD) y salió antes del rebote.

Con los indicadores que observa el agente, calculados a partir del precio, el tramo se ve así:

| Fecha | Cierre | ret_20 | dist_sma20 | dist_sma50 | vol_20 (anual) | RSI 14 |
|---|---|---|---|---|---|---|
| 12-abr-2017 (antes del tramo) | 841,5 | −3,2 % | −0,9 % | −0,5 % | 11,1 % | 52 |
| 28-abr-2017 | 924,5 | +8,5 % | +7,4 % | +8,0 % | 17,0 % | **94** |
| 10-may-2017 | 954,8 | +12,8 % | +5,9 % | +9,5 % | 15,9 % | **92** |
| 26-may-2017 | 993,3 | +7,2 % | +3,6 % | +10,7 % | 12,9 % | 69 |

Desde finales de abril, el RSI llegó a 92–94, muy por encima del percentil 90 del entrenamiento (78). La distancia a la media de 20 días (7,4 %) también superó su percentil 90 de entrenamiento (5,0 %). Son señales típicas de **sobrecompra**. En el entrenamiento (2009–2015), después de días con RSI > 78 el retorno de los 20 días siguientes fue en promedio +0,27 %, frente a +1,45 % en un día cualquiera. Para un agente entrenado con esos datos, quedarse fuera tras una sobrecompra era una regla razonable. En promedio, durante el tramo los indicadores normalizados estuvieron por encima de su media de entrenamiento: RSI +1,4 desviaciones, `ret_20` +0,9 y `dist_sma20` +0,9. La volatilidad estuvo por debajo (−0,9). El precio, sin embargo, siguió subiendo.

El patrón se repite en el resto del held-out. El agente casi no participa en las subidas tranquilas de 2017, cuando la volatilidad anualizada promedió **15 %** frente a una mediana de 20,9 % en entrenamiento. En cambio, se vuelve activo en la turbulencia de febrero a mayo de 2018, con una volatilidad promedio de **30,8 %**, cerca del percentil 90 del entrenamiento (35,9 %). Ahí concentra sus entradas, sus idas y vueltas y todo su drawdown.

*Nota:* los indicadores se calcularon con el código del proyecto a partir de los precios. No se inspeccionaron los valores Q de la red, así que la relación entre indicador y decisión es una interpretación consistente con lo observado, no una prueba causal.

## 04. Hipótesis

La explicación más consistente combina dos de las tres hipótesis planteadas:

1. **Efecto de la recompensa (reward hacking): la causa principal.** La penalización por aumento del drawdown hace que estar en efectivo sea la forma más segura de no recibir castigos: en efectivo el drawdown nunca crece. El agente aprendió una política de "fuera por defecto" (79,7 % de los días en efectivo en validación; exposición media del 18 % en el held-out) y solo entra brevemente cuando el precio ya cayó y los indicadores sugieren un rebote. Cuando una entrada empieza a perder, la penalización lo empuja a salir, así que vende después de la caída y no está cuando llega la recuperación. Eso explica a la vez el bajo retorno, las 21 idas y vueltas y un drawdown casi igual al del mercado aunque solo invirtió el 18 % del tiempo: el drawdown que sí sufrió lo generó la rotación en el peor periodo, no la exposición sostenida.
2. **No-estacionariedad: el factor que lo hizo costoso.** En 2009–2015 la sobrecompra solía ir seguida de retornos más débiles, y en 2016 quedarse fuera fue rentable. En 2017 el activo tuvo una subida de baja volatilidad, poco frecuente en el entrenamiento, en la que la sobrecompra se mantuvo durante semanas. La misma política que ganó +9 % en validación quedó 53 puntos por debajo de comprar y mantener en el held-out.
3. **Ruido o sobreajuste: posible, pero secundario.** Las idas y vueltas sugieren cierta inestabilidad de la política cerca de los límites de decisión. No hay evidencia de que sea la causa principal, porque el patrón de efectivo por defecto es consistente entre validación y held-out.

**Qué cambiaríamos para corregirlo:**
- Penalizar la rotación de forma explícita en la recompensa, para reducir las idas y vueltas.
- Usar una recompensa **diferencial frente a comprar y mantener**, que castigue quedarse fuera cuando el activo sube y no solo las caídas propias.
- Validar con varios periodos (*walk-forward*) en lugar de un solo año, para que la elección de la recompensa no dependa del régimen de un año particular.
