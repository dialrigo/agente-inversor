# Reflexión individual · Andrés Díaz

## 1. ¿Cuál fue el resultado que más me sorprendió?

Lo que más me sorprendió fue descubrir, desde el análisis exploratorio, que ninguno de los indicadores del estado tenía una correlación relevante con el retorno del día siguiente, pues todas fueron inferiores a 0,025; aun así, el agente tomaba decisiones con ellos, lo que me llevó a entender que no aprendía a predecir el precio, sino a gestionar su exposición al riesgo. Esa intuición cobró sentido en el periodo de prueba, donde la versión descartada en validación rindió 32 % y la elegida apenas 3,5 %: una política que solo administra el riesgo depende por completo del régimen de mercado en el que se evalúa.

## 2. ¿Qué decisión metodológica tuvo mayor impacto en el agente?

Considero que la decisión de mayor impacto fue la separación temporal estricta entre entrenamiento, validación y prueba. Al revisar el análisis exploratorio identifiqué que varias figuras se calculaban con la serie completa, incluido el periodo de prueba; aunque las conclusiones se sostenían solo con entrenamiento y validación, corregirlo antes de la corrida oficial evitó que el estado se justificara con información futura. Esta decisión no modificó el retorno del agente; sin embargo, determinó algo más importante, la validez de las conclusiones, porque un resultado obtenido con fuga de datos habría carecido de sentido, fuera positivo o negativo.

## 3. ¿Qué cambiaría si tuviera que repetir el experimento?

Si repitiera el experimento, incluiría en el estado la caída del portafolio desde su máximo. La recompensa elegida penaliza precisamente el aumento de esa caída, pero el agente solo observaba los indicadores del precio y su posición; por lo tanto, se le pidió controlar una variable que no podía ver, y terminó aprendiendo una regla aproximada que lo llevó a refugiarse en efectivo. Como responsable de la formulación, considero que este es el ajuste más directo para alinear lo que el agente observa con lo que se le pide optimizar.

## 4. ¿Qué comportamiento del agente no logré explicar completamente?

No logré explicar completamente por qué el agente realizó 21 idas y vueltas, concentradas en la turbulencia de 2018. Esperaba que una recompensa diseñada para evitar caídas lo mantuviera fuera del mercado en los periodos más volátiles; no obstante, fue justamente allí donde se volvió más activo, entrando y saliendo en pocos días y pagando costos repetidos. Mi hipótesis es que los indicadores alcanzaron valores poco frecuentes en el entrenamiento, cerca de los límites de decisión de la red; sin inspeccionar sus valores Q, sin embargo, no puedo afirmarlo con certeza.

## 5. ¿Cuál fue la principal diferencia entre lo aprendido en RL y su aplicación a un problema real?

La principal diferencia fue darme cuenta de que la mayor parte del trabajo estuvo fuera del algoritmo. En el curso, implementar DQN o PPO parecía el centro del problema; en este proyecto, en cambio, el algoritmo vino resuelto por Stable Baselines3, y el esfuerzo real se concentró en definir el estado, auditar la fuga de información, modelar los costos, diseñar la recompensa, proteger el periodo de prueba y asegurar que el experimento fuera reproducible. En consecuencia, entendí que la calidad de un agente depende menos del algoritmo que de la formulación del problema que se le plantea.
