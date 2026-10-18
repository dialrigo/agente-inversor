# Reflexión individual · Diego Ríos

## 1. ¿Cuál fue el resultado que más me sorprendió?

Que la versión que descartamos en validación fuera la que mejor le fue en el held-out. La v1 ganó +32 % en 2017–2018 y la v2, la elegida, apenas +3,5 %. En 2016 había pasado exactamente lo contrario. Me costó aceptar que no podíamos "corregir" la elección después de ver ese número. Justo ahí entendí para qué existe el held-out: si lo hubiéramos usado para escoger, el +32 % no habría significado nada.

## 2. ¿Qué decisión metodológica tuvo mayor impacto en el agente?

La penalización por drawdown en la recompensa. Con ella el agente aprendió que la forma más segura de no ser castigado era quedarse en efectivo, y pasó cerca del 80 % de los días fuera del mercado. En 2016, un año casi plano, eso pareció una virtud. En un mercado que subió 56 % fue su mayor costo. Una línea en la función de recompensa cambió por completo la personalidad del agente, más que cualquier hiperparámetro.

## 3. ¿Qué cambiaría si tuviera que repetir el experimento?

Validaría con varios periodos (*walk-forward*) en lugar de un solo año, porque un año no alcanza para distinguir una buena estrategia de un buen momento. Entrenaría con varias semillas y reportaría el promedio: cuando janayajoo y yo corrimos lo mismo con la semilla 42 en máquinas distintas, los números no coincidieron. Y desde el primer día dejaría el entorno de trabajo listo para todo el equipo (uv, kernel, Git), porque perdimos horas en eso al final.

## 4. ¿Qué comportamiento del agente no logré explicar completamente?

Por qué el agente, que se mantuvo tan prudente todo 2017, se volvió tan activo justo en la turbulencia de febrero a mayo de 2018, con 21 idas y vueltas. La hipótesis de que la alta volatilidad le parecía una oportunidad de rebote es coherente con los indicadores, pero sin mirar los valores Q de la red no puedo afirmarlo. Tampoco entiendo del todo por qué la misma semilla da resultados distintos en computadores diferentes.

## 5. ¿Cuál fue la principal diferencia entre lo aprendido en RL y su aplicación a un problema real?

En clase la recompensa venía dada: en LunarLander aterrizar bien es el objetivo y no hay discusión. Aquí diseñar la recompensa *era* el problema, y el mercado cambia de reglas entre un periodo y otro, algo que un entorno de juego nunca hace. También me sorprendió cuánto del trabajo real no es el algoritmo: evitar mirar el futuro, poder reproducir los resultados y coordinar a siete personas en un mismo repositorio. DQN lo importamos en una línea; todo lo demás nos tomó la semana.
