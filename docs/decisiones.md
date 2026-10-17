# Bitácora de decisiones

Formato: fecha · autor · decisión · motivo. Lo más reciente va al final.

- 2026-10-12 · Diego · Base de código: repositorio del profesor `rl_games_sb` (SB3 + MLflow + Optuna + uv) · Recomendación de la sesión 6: enfocarse en el problema, no en reprogramar algoritmos.
- 2026-10-12 · Diego · Datos: GOOGL diario de `gym-anytrading` · Es el dataset común del curso (sesión 6). Ya viene ajustado por el split de 2014 (`Close == Adj Close`).
- 2026-10-12 · Diego · Entorno propio (`InvestorEnv`) en lugar de `stocks-v0` · `stocks-v0` solo tiene acciones largo/corto y una recompensa sin costos ni capital; el enunciado pide fracciones {0, 50, 100 %}, costos, capital de \$100.000 y drawdown.
- 2026-10-12 · Diego · División train 2009–2015 / val 2016 / test 2017–2018 · Separación temporal estricta; validación para comparar recompensas y para Optuna sin tocar el held-out.
- 2026-10-12 · Diego · Ejecución al cierre de t (market on close) · Simplicidad y consistencia con los datos diarios. Es optimista frente a ejecutar en la apertura de t+1; queda como limitación.
- 2026-10-12 · Diego · Recompensa ×100 · Escala en puntos porcentuales para estabilizar la red; no cambia la política óptima.
- 2026-10-12 · Diego · Episodios de entrenamiento de 252 días con inicio aleatorio · Más diversidad de situaciones que un único episodio de 6 años.
- 2026-10-12 · Diego · Criterio de selección de la versión final: ratio retorno / máximo drawdown en validación · Equilibra retorno y riesgo; se fija antes de abrir el held-out.
- 2026-10-12 · Diego · Cambios al código del profesor: (1) `envs.py` registra los entornos Investor; (2) `config.py` y `experiments.py` aceptan `eval_env`; (3) el sampler de Optuna usa la semilla del config · Cambios mínimos para evaluar en validación y ser reproducibles.
- 2026-10-12 · Diego · Organización del equipo: cada integrante tiene una función de producción con commits propios y verifica a otro compañero (anillo Andrés → Nicolás → janayajoo → Lorena → Marlon → Nataly → Andrés) · Distribuir la participación real en la entrega y evitar conflictos: solo Diego edita el notebook; los demás escriben en `docs/informe/` y `docs/reflexiones/`.
- 2026-10-17 · Andrés · EDA (sección 2 del notebook) restringido a train y validación (≤ 2016-12-31); del held-out solo se muestran fechas y número de días hasta la sección 8 · Evitar que las decisiones del estado y la recompensa se apoyen en estadísticas del periodo de prueba.
- 2026-10-17 · Nicolás · Metricas Análisis de métricas y tests
- 2026-10-17 · janayajoo · Variante de control v3 (`configs/investor_dqn_log.yaml`): retorno log sin penalización (v2 con λ = 0), mismos hiperparámetros y semilla · Aislar el efecto del log del de la penalización por drawdown. No cambia el protocolo ni abre el held-out.
- 2026-10-17 · janayajoo · Recompensa elegida: v2 (log − drawdown), con ratio retorno / drawdown de 1,35 en validación 2016 frente a −0,53 (v1) y −0,42 (v3) · Aplica el criterio fijado el 2026-10-12; v1 y v3 operan ~70 veces y pierden por costos, v2 reduce el drawdown a 6,3 %.
- 2026-10-17 · Diego · Corrida oficial: versión elegida en validación = v2 (log − drawdown). En el held-out v1 rindió más (+32 % frente a +3,5 %), pero se mantiene v2 como versión evaluada y no se reajusta nada · Elegir con el held-out invalidaría la evaluación; el cambio de orden entre 2016 y 2017–2018 se reporta como evidencia de no-estacionariedad.
- 2026-10-17 · Andrés · Cifras de validación de la sección 05 alineadas con la corrida oficial del notebook (v2: ratio 1,04; v1: −0,65), en reemplazo del 1,35 citado en la entrada de la recompensa elegida; la tabla de las tres variantes se conserva como corrida exploratoria · Regla del informe: cifras solo de la corrida oficial. La elección de v2 no cambia, porque ambas corridas dan el mismo orden.
