# Reflexión individual · Lorena Valero

## 1. ¿Cuál fue el resultado que más me sorprendió?

Ver la tabla del held-out por primera vez. El agente que elegimos en validación, la v2, ganó apenas +3,46 %, frente a +56,36 % de comprar y mantener, y ni siquiera superó al agente aleatorio promedio (+4,95 %). Pero lo que más me impactó fue la fila de abajo: la v1, que habíamos descartado, ganó +32 %. Tuve la tentación de pensar "elijamos la v1". Justo ahí entendí que, si lo hacía, toda la evaluación perdía valor.

## 2. ¿Qué decisión metodológica tuvo mayor impacto en el agente?

Desde la evaluación, la que más pesó fue haber elegido la versión final con un solo año de validación. En 2016 el activo casi no se movió (+4,3 %) y quedarse fuera del mercado parecía una estrategia brillante. Ese único año decidió todo, y el mercado de 2017–2018 fue completamente distinto. La recompensa definió cómo se comportaba el agente; la validación de un solo año definió que eligiéramos ese comportamiento.

## 3. ¿Qué cambiaría si tuviera que repetir el experimento?

Evaluaría con varias ventanas de tiempo y con varias semillas, no con una sola corrida. Lo aprendí con el agente aleatorio: con la semilla 42 ganó +31,5 % y tuvo el menor drawdown de toda la tabla, pero el promedio de 20 semillas fue +4,95 %. Si un agente al azar puede verse así de bien por suerte, un agente entrenado también. Además, agregaría desde el inicio una comparación contra comprar y mantener dentro de la recompensa.

## 4. ¿Qué comportamiento del agente no logré explicar completamente?

Que su drawdown (13,9 %) fuera casi igual al del mercado (15,4 %) aunque solo estuvo invertido el 18 % del tiempo. Al revisar la curva vi que toda su caída se concentró entre marzo y abril de 2018: justo en la turbulencia el agente se volvió activo, con entradas y salidas rápidas. Tengo una hipótesis, que la penalización lo hacía vender después de cada caída, pero sin inspeccionar los valores Q de la red no puedo confirmarla.

## 5. ¿Cuál fue la principal diferencia entre lo aprendido en RL y su aplicación a un problema real?

En los ejercicios del curso evaluar era sencillo: el agente aterriza o no aterriza, y la recompensa media lo dice todo. Aquí la recompensa del agente no sirve para evaluarlo. Tuve que mirar retorno, drawdown, costos y exposición a la vez, comparar contra baselines y desconfiar de una sola trayectoria. También me di cuenta de que la regla más importante no era técnica sino de disciplina: no tocar el held-out hasta el final y no cambiar nada después de verlo.
