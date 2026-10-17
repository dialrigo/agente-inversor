# Datos y análisis exploratorio

## Conjunto de datos y ajuste por división de acciones

Trabajamos con el conjunto de datos común del curso, esto es, los precios diarios de GOOGL incluidos en la librería `gym_anytrading` (`STOCKS_GOOGL`). Elegimos esta fuente, en lugar de descargar datos propios, para que los resultados sean comparables con los de los demás grupos y para que cualquier persona pueda reproducir el experimento sin depender de un servicio externo. La serie abarca desde el 22 de mayo de 2009 hasta el 29 de agosto de 2018, es decir, 2.335 días de negociación, y contiene seis columnas: precio de apertura (`Open`), máximo (`High`), mínimo (`Low`), cierre (`Close`), cierre ajustado (`Adj Close`) y volumen (`Volume`). De ellas, tomamos el precio de cierre como base de los retornos y de los indicadores del estado, mientras que el volumen lo analizamos únicamente en esta etapa exploratoria.

Antes de calcular cualquier indicador verificamos que el precio de cierre coincide con el cierre ajustado en todo el periodo; por lo tanto, la serie ya incorpora el ajuste por la división de acciones (split) de abril de 2014. Revisamos además los días alrededor del 3 de abril de 2014, sin encontrar la caída abrupta a la mitad que presentaría una serie sin ajustar. Con base en ello, decidimos calcular los retornos y los indicadores directamente sobre el precio de cierre, sin correcciones adicionales.

## División temporal: entrenamiento, validación y prueba

Se optó por una división estrictamente cronológica, puesto que en una serie de precios una partición aleatoria permitiría que el agente aprendiera con información posterior a la que luego se evalúa.

| Periodo | Desde | Hasta | Días | Uso |
|---|---|---|---|---|
| Entrenamiento | 3 ago. 2009 | 31 dic. 2015 | 1.616 | Aprendizaje del agente |
| Validación | 4 ene. 2016 | 30 dic. 2016 | 252 | Comparación de recompensas y ajuste de hiperparámetros |
| Prueba | 3 ene. 2017 | 29 ago. 2018 | 418 | Evaluación final, una única vez |

El entrenamiento inicia el 3 de agosto de 2009, y no el 22 de mayo, porque los primeros días se descartan como periodo de calentamiento: la media móvil de 50 días necesita esa historia para producir su primer valor, y preferimos perder esos días a alimentar al agente con indicadores incompletos.

Del mismo modo, restringimos todo el análisis de esta sección a entrenamiento y validación, es decir, hasta el 31 de diciembre de 2016. Del periodo de prueba solo reportamos sus fechas y su número de días; su comportamiento lo describimos por primera vez en la sección de evaluación, una vez definido el agente. Esta decisión busca que ninguna elección sobre el estado o la recompensa dependa de información del periodo de prueba, con lo cual cerramos una posible vía de fuga de datos.

## Precio y volumen (figura 01)

En la figura 01 se aprecia una tendencia alcista marcada durante el entrenamiento: el precio pasa de 226 a 778 USD, lo que equivale a un incremento del 243,7 % en seis años y medio. En contraste, durante la validación el activo permanece prácticamente estable, con una variación de apenas 4,3 % en 2016. Este contraste tiene dos consecuencias para el planteamiento. Por un lado, comprar y mantener se convierte en una referencia exigente, ya que en un mercado que sube casi de forma continua cualquier salida implica pagar costos y renunciar a parte de la valorización. Por otro lado, el agente aprende en un régimen alcista y se valida en uno lateral, de modo que desde el inicio debemos tener presente que el mercado no se comporta igual en todos los periodos.

El volumen, en cambio, disminuye de manera sostenida: la mediana diaria pasa de 5,3 millones de acciones en 2009 y 2010 a 1,8 millones en 2015 y 2016. Dado que su nivel cambia de forma tan pronunciada, un valor de volumen de 2010 no es comparable con uno de 2016; por esta razón, se decidió no incluirlo en el estado. Adicionalmente, la información de riesgo que aporta, en la medida en que los días de alto volumen coinciden con movimientos amplios del precio, ya queda recogida en la volatilidad reciente.

## Distribución de los retornos y colas pesadas (figura 02)

El análisis utiliza retornos logarítmicos diarios, definidos como el logaritmo del cociente entre el precio de cierre de un día y el del día anterior. Se prefirieron sobre el retorno simple porque se suman a lo largo del tiempo, lo que facilita construir los indicadores de varios días. La siguiente tabla resume su distribución entre 2009 y 2016.

| Estadístico | Valor |
|---|---|
| Media diaria | 0,073 % |
| Desviación estándar diaria | 1,535 % |
| Asimetría | 0,74 |
| Curtosis en exceso | 12,9 |
| Mayor caída diaria | 8,7 % (20 de enero de 2012) |
| Mayor alza diaria | 15,1 % (17 de julio de 2015) |

La curtosis en exceso de 12,9, frente a un valor de cero en una distribución normal, corresponde a una distribución de colas pesadas; en otras palabras, los días extremos son considerablemente más frecuentes de lo que anticiparía una normal. En el panel izquierdo de la figura 02, el histograma es más alto en el centro y más ancho en los extremos que la curva normal con la misma media y desviación. Concretamente, los movimientos superiores a tres desviaciones estándar ocurren en el 1,25 % de los días, cerca de cinco veces lo esperado bajo normalidad (0,27 %).

Para el agente, este hallazgo significa que el riesgo no es uniforme en el tiempo: hay días en los que mantener todo el capital invertido puede representar una pérdida cercana al 9 %. Por consiguiente, decidimos que el estado no podía limitarse a describir la dirección del precio y que debía incluir también una medida del riesgo reciente.

## Regímenes de volatilidad (figura 02) y caídas del activo (figura 03)

El panel derecho de la figura 02 presenta la volatilidad anualizada, calculada en ventanas de 20 días. Esta oscila entre 5,5 % en los periodos más tranquilos y 60 % en agosto de 2011, con una mediana de 21 %. Ahora bien, más que su rango, interesa su comportamiento: las zonas sombreadas, que corresponden al 20 % de días más volátiles, no aparecen dispersas, sino agrupadas en tramos de varias semanas. Así, la volatilidad se organiza en regímenes, de modo que a un periodo agitado tiende a seguirle otro periodo agitado; por el contrario, el retorno de un día aporta muy poca información sobre el del día siguiente.

Sobre este hallazgo fundamentamos la inclusión de `vol_20` en el estado. Si la volatilidad de las últimas semanas anticipa, al menos parcialmente, la de los días próximos, el agente puede emplearla para decidir cuánto capital exponer, aun cuando no logre anticipar la dirección del precio. Escogimos una ventana de 20 días porque equivale aproximadamente a un mes de negociación, lo bastante larga para estimar la volatilidad con estabilidad y lo bastante corta para reaccionar a un cambio de régimen.

Por su parte, la figura 03 muestra la caída del activo desde su máximo previo (drawdown). Las tres caídas más profundas del periodo fueron las siguientes.

| Inicio | Punto mínimo | Caída máxima | Recuperación |
|---|---|---|---|
| 5 ene. 2010 | 6 jul. 2010 | 30,4 % | 8 nov. 2010 |
| 19 ene. 2011 | 24 jun. 2011 | 25,8 % | 27 dic. 2011 |
| 27 feb. 2014 | 12 ene. 2015 | 18,6 % | 17 jul. 2015 |

En consecuencia, aun en un activo que se valorizó 243,7 % durante el entrenamiento hubo caídas de hasta 30 %, cuya recuperación tomó entre 10 y 17 meses. Comprar y mantener absorbe estas caídas en su totalidad; de ahí que consideremos pertinente probar una recompensa que penalice el aumento de la caída desde el máximo, puesto que este riesgo está presente en los datos con los que aprende el agente.

## Indicadores: correlación entre ellos y con el retorno siguiente (figura 04)

A diferencia de las figuras anteriores, la figura 04 la calculamos exclusivamente con datos de entrenamiento, ya que en ella evaluamos los indicadores que el agente utiliza para aprender.

En primer lugar, ningún indicador presenta una correlación lineal relevante con el retorno del día siguiente; todas son inferiores a 0,025 en valor absoluto. No existe, entonces, una señal lineal simple para anticipar el precio. Por lo tanto, si el agente aprende algo útil, será una relación no lineal o, más probablemente, una forma de gestionar el riesgo, esto es, de decidir cuándo reducir la exposición, y no una predicción de la dirección. Este resultado es coherente con lo esperado para un activo de alta liquidez, y lo tenemos en cuenta al interpretar el desempeño del agente.

Del mismo modo, identificamos que varios indicadores están altamente correlacionados entre sí.

| Par de indicadores | Correlación |
|---|---|
| `ret_20` y `dist_sma50` | 0,87 |
| `dist_sma20` y `rsi_14` | 0,87 |
| `ret_20` y `dist_sma20` | 0,85 |
| `dist_sma20` y `dist_sma50` | 0,81 |

Estos indicadores describen la tendencia desde perspectivas similares y, en consecuencia, comparten buena parte de su información. Aun así, decidimos conservarlos, dado que una red neuronal no exige variables independientes y cada indicador aporta un matiz propio, ya sea el horizonte de 20 o de 50 días, o bien la distancia a la media frente a la fuerza relativa del precio. Reconocemos, sin embargo, que el estado contiene menos información nueva de la que sugieren sus siete variables, aspecto que registramos como una limitación del planteamiento.

Finalmente, `vol_20` es el indicador menos correlacionado con los demás, con valores que no superan 0,10. Al medir el riesgo y no la tendencia, aporta información que ningún otro indicador contiene, lo que refuerza su inclusión.

## Decisiones del estado durante el EDA

| Hallazgo | Decisión sobre el estado |
|---|---|
| Retorno sin memoria y volatilidad agrupada en regímenes | Incluir `vol_20` como medida del riesgo reciente |
| Colas pesadas, con movimientos diarios de hasta 15 % | Medir el riesgo además de la tendencia y limitar los indicadores normalizados a un máximo de cinco desviaciones estándar |
| Tendencias prolongadas y caídas de hasta 30 % | Incluir retornos de 1, 5 y 20 días y la distancia a las medias de 20 y 50 días |
| Volumen con un nivel que cambia en el tiempo | Excluir el volumen |
| Precio en niveles no comparable entre 2009 y 2016 | Utilizar solo variables relativas (retornos, distancias y RSI), nunca el precio en niveles |
| Cambio de régimen entre entrenamiento y validación | Normalizar con estadísticas de entrenamiento y discutir la no estacionariedad |
