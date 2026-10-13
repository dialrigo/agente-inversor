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
