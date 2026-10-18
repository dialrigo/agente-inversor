# Introducción y pregunta central

## Contexto: Invertir es un problema natural de RL

Invertir corresponde a una serie de decisiones que se dan bajo incertidumbre. Cada día decidimos que capital mantener en un activo sin conocer el futuro comportamiento del precio, y una vez decidido quedamos condicionados a lo que podemos hacer después: hay costos asociados a cambiar de posición y si hay una caída se requiere pensar en estrategias de recuperación desde un valor menor. 

Este es el mismo principio del aprendizaje por refuerzo: el agente observa un estado, elige una acción y recibe una recompensa, esta recompensa depende de la acción y la evolución del entorno. Al final, su objetivo es maximizar la recompensa acumulada.

En este proyecto el agente administra USD100.000 y al cierre de cada día, elige qué porcentaje mantener invertido en acciones de GOOGLE: 0%, 50%, 100%. El estado combina siete indicadores calculados solo con precios pasados (retornos de 1, 5 y 20 días, distancia a las medias de 20 y 50 días, volatilidad de 20 días y RSI de 14 días) con la posición actual. 

Seleccionamos las ventanas temporales a partir de criterios financieros y de representación del estado en aprendizaje por refuerzo.
Primero, utilizamos retornos de 1, 5 y 20 días porque representan horizontes diarios, semanales y mensuales, permitiendo capturar distintas escalas del momentum del precio.
Segundo, incorporamos medias móviles de 20 y 50 días para representar tendencias de corto y mediano plazo, mientras que la volatilidad de 20 días permite caracterizar el riesgo histórico reciente.

Finalmente, utilizamos el RSI de 14 días porque corresponde a una parametrización tradicional de este indicador técnico.


Cada cambio de posición paga un costo de 0,1% sobre el monto negociado. Usamos los precios diarios de GOOGL del conjunto `gym-anytrading` (2009–2018) y los separamos en el tiempo: entrenamiento de 2009 a 2015, validación en 2016 y un periodo de prueba, de enero de 2017 a agosto de 2018, que se abrió una sola vez. 

El agente se entrenó con DQN, en la implementación de Stable-Baselines3, y probamos dos versiones de la recompensa: el retorno simple del portafolio (v1) y el retorno logarítmico con una penalización por aumento del drawdown (v2).

Elegimos comparar contra dos referencias:

1. Comprar y mantener representa lo que haría un inversionista pasivo y, en un activo que subió 243,7 % durante el entrenamiento (figura 01), es difícil de superar. 
2. El agente aleatorio, evaluado con 20 semillas, indica si el agente aprendió algo mejor que decidir al azar con las mismas reglas de costo.

## Pregunta central del proyecto

**¿Puede un agente de RL aprender una estrategia de inversión que se comporte mejor que comprar y mantener o que un agente aleatorio, en un periodo que nunca vio?**

Medimos el retorno, el máximo drawdown, los costos pagados, la exposición media y el índice de Sharpe, porque una estrategia que gana menos pero con mucho menos riesgo puede ser preferible para un inversionista.

## Resumen del resultado

Para este ejercicio la respuesta es **no**. La versión elegida en validación (v2, por su mejor relación retorno / drawdown en 2016) ganó **+3,46 %** en el held-out, frente a **+56,36 %** de comprar y mantener y **+4,95 %** del aleatorio promedio. Además redujo el máximo drawdown en solo 1,5 puntos (13,87 % frente a 15,36 %) y pagó 5.449 USD en costos, más que todo su retorno (`results/metricas_heldout.csv`, figura 09). El agente aprendió a refugiarse en efectivo, con una exposición media del 18 %. Esa conducta fue rentable en el año lateral de validación y muy costosa en el mercado alcista de 2017–2018. La versión descartada (v1) habría rendido +32 % en el held-out; ese cambio de orden entre periodos es la principal evidencia de no-estacionariedad del proyecto y se analiza en la discusión.
