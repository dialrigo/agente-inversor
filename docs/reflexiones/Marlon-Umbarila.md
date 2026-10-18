# Reflexión individual · Marlon Umbarila

## 1. ¿Cuál fue el resultado que más me sorprendió?

Que el "mejor" trial de Optuna fuera el peor candidato. En la búsqueda fue el único con recompensa positiva en validación, pero al reentrenarlo con 150.000 pasos y 4 semillas perdió con todas (−7,5 % en promedio) y operó casi el doble que la configuración original. También me sorprendió que la recompensa que cada trial alcanza en entrenamiento no tuviera ninguna relación con la de validación (Spearman −0,01): los trials que más aprendieron en 2009–2015 estuvieron entre los peores en 2016. Aprender bien el pasado no garantizó decidir bien después.

## 2. ¿Qué decisión metodológica tuvo mayor impacto en el agente?

Evaluar con varias semillas antes de decidir. Con una sola semilla, la v2 parecía ganarle al mercado en validación (+9 % frente a +4,2 %); con cuatro, el retorno medio fue +1,4 % con una desviación de 5,4 puntos, es decir, el resultado dependía más del azar que de la estrategia. Esa misma prueba fue la que evitó adoptar los hiperparámetros de Optuna. Fijar antes la regla de adopción ("mejorar en al menos 3 de 4 semillas") me obligó a decidir con evidencia y no con el número que más me gustaba.

## 3. ¿Qué cambiaría si tuviera que repetir el experimento?

Haría que Optuna calificara cada trial con varias semillas y con los mismos 150.000 pasos del entrenamiento final, y con el criterio retorno / drawdown en lugar de la recompensa. Usaría también validación walk-forward (varios años de validación) en vez de un solo año, porque 2016 es una muestra muy pequeña para elegir entre configuraciones. Y coordinaría mejor los tiempos: la corrida oficial se hizo mientras mi búsqueda seguía en curso; por suerte la decisión fue no cambiar nada, pero el orden correcto era terminar Optuna primero.

## 4. ¿Qué comportamiento del agente no logré explicar completamente?

Por qué, con la misma semilla y el mismo código, la v2 obtiene en validación +9,0 % en una máquina, +8,5 % en otra y +6,1 % en la mía, con casi la misma conducta (31–32 cambios de posición, ~18 % de exposición). Lo atribuyo a diferencias de punto flotante que se acumulan en 150.000 pasos, pero no logré aislar en qué momento del entrenamiento divergen las redes. Tampoco tengo una explicación completa de por qué en el held-out el orden se invirtió: la v1, que perdía en validación, ganó +32 %, mientras la v2 solo +3,5 %.

## 5. ¿Cuál fue la principal diferencia entre lo aprendido en RL y su aplicación a un problema real?

En los entornos del curso (Atari, LunarLander) el entorno es el mismo al entrenar y al evaluar, así que una curva de aprendizaje que sube es buena señal. En finanzas no: el mercado de 2016 o de 2017–2018 no se comporta como el de 2009–2015, y una recompensa de entrenamiento alta puede significar solo que el agente memorizó el pasado. La otra diferencia es el ruido: con un solo episodio de evaluación por año, la varianza entre semillas es tan grande como el efecto que se quiere medir, así que un solo número nunca basta para concluir.
