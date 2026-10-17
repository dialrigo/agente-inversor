# Reflexión individual · Marlon Umbarila

Rama `reflexion/Marlon-Umbarila` · verifica Nataly · 3 a 6 líneas por pregunta, en primera persona.

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

---

## Qué hice en el proyecto y dónde verlo

Mi función fue **algoritmo, Optuna, semillas y reproducibilidad** (rúbrica 2, 4 y 5). Todo se calificó en **validación (2016)**; nunca usé el held-out para decidir.

| Qué hice | Qué se comparó o se obtuvo | Dónde se ve |
|---|---|---|
| Cloné el repo desde cero en Windows siguiendo solo el README y `CONFIGURACION_KERNEL.md` | `uv sync` y prueba de humo a la primera (`TODO OK` en ~16 s); dos corridas idénticas → determinista en una misma máquina | `docs/informe/10_reproducibilidad.md` |
| Búsqueda de hiperparámetros con Optuna (15 trials × 50.000 pasos, 8 min) | learning rate, γ, exploración y batch; solo el trial 3 (γ = 0,9) fue positivo | `docs/experimentos/optuna_log.txt`, tabla en `optuna_y_semillas.md` |
| Exportación de MLflow a tabla y figura (`scripts/exportar_optuna.py`) | Curvas de aprendizaje de los 15 trials frente a su recompensa en validación; Spearman −0,01 | `docs/experimentos/optuna_curvas.png`, `optuna_trials.csv` |
| Robustez por semillas (`scripts/semillas.py`, 4 semillas × 150.000 pasos) | YAML (+1,4 % ± 5,4; 2 de 4 ganan) frente a Optuna (−7,5 % ± 3,8; 0 de 4) y comprar y mantener (+4,2 %) | `docs/experimentos/semillas_*.csv` y sus logs, `optuna_y_semillas.md` |
| Decisión sobre los hiperparámetros | Se mantiene el YAML: el candidato de Optuna es peor en 4 de 4 semillas | `docs/decisiones.md`, `docs/informe/06_algoritmo.md` |
| Documentación del algoritmo | DQN, arquitectura 8 → 64 → 64 → 3, tabla de hiperparámetros, protocolo train / val / held-out | `docs/informe/06_algoritmo.md` |
| Comparación entre máquinas | Misma semilla en 3 equipos: misma conducta, retorno ±3 puntos | `docs/informe/10_reproducibilidad.md` |

**Para verlo de forma interactiva:** `uv run mlflow ui` → http://127.0.0.1:5000 → modo **Model training** → experimento `agente-inversor` → corrida `tune-dqn-Investor-log_dd-v0`.

**Lo que me llevo:** en RL aplicado a datos reales la parte difícil no es entrenar el agente, sino no engañarse con los resultados. Separar train, validación y held-out, fijar las reglas antes de mirar los números y repetir con varias semillas fue lo que convirtió un "+9 %" llamativo en una conclusión honesta: el agente no le gana al mercado de forma confiable, pero sí aprende de manera consistente a asumir menos riesgo.
