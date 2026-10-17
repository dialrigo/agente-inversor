# Reflexión individual · janayajoo

## 1. ¿Cuál fue el resultado que más me sorprendió?
Que la versión que elegí con cuidado en validación, v2, quedó muy por debajo de comprar y mantener en el held-out (+3,5 % frente a +56,4 %) y no se distinguió del azar en Sharpe (0,26 frente a 0,27). Más sorprendente aún fue que v1, la que descarté porque perdía en 2016, terminó con +32 % en 2017–2018. Entendí que un año de validación puede premiar la estrategia equivocada: en 2016 quedarse fuera del mercado fue rentable, y en 2017–2018 salió carísimo.

## 2. ¿Qué decisión metodológica tuvo mayor impacto en el agente?
La penalización por aumento del drawdown. Pasar de retorno simple a logarítmico casi no cambió la conducta (v1 y v3 operaron unas 70 veces y perdieron por costos), pero agregar la penalización llevó al agente a pasar cerca de 79 % del tiempo en efectivo. Lo supe gracias a la variante de control v3, que agregué para separar los dos efectos. Otra decisión de peso fue fijar el criterio de selección antes de abrir el held-out, que es lo que me permite reportar el resultado malo sin retocarlo.

## 3. ¿Qué cambiaría si tuviera que repetir el experimento?
No elegiría la versión mirando un solo año ni una sola semilla. Validaría en varios años (por ejemplo, ventanas móviles) y compararía las versiones con varias semillas, porque con la semilla 42 la v2 dio +6 % u +9 % según la máquina, y con otras dos semillas perdió. También probaría un λ menor a 1 y añadiría el drawdown actual a la observación del agente, que hoy no lo ve y aun así es lo que se le penaliza.

## 4. ¿Qué comportamiento del agente no logré explicar completamente?
No sé explicar por qué v2 estuvo en el mercado solo el 18 % del tiempo y aun así tuvo casi el mismo drawdown que comprar y mantener (13,9 % frente a 15,4 %). Mi hipótesis es que sus pocas entradas cayeron justo en la turbulencia de 2018, cuando rotó decenas de veces, pero no la comprobé. Tampoco sé por qué dos semillas ganan y dos pierden con exactamente la misma configuración.

## 5. ¿Cuál fue la principal diferencia entre lo aprendido en RL y su aplicación a un problema real?
En RL de clase el entorno es estacionario: lo aprendido en entrenamiento sirve en prueba. Aquí no. Entre 2009–2015, 2016 y 2017–2018 el mercado cambió de régimen, y la correlación entre el rendimiento en entrenamiento y en validación fue −0,01 en las búsquedas de Optuna: aprender mejor el pasado no mejoró las decisiones. Además, los costos de operar (5,4 % del capital en el held-out) pesaron más que muchas decisiones de diseño, y un buen resultado en validación no garantizó nada hacia adelante.