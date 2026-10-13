# Agente Inversor · Proyecto final de Simulación y Aprendizaje por Refuerzo

Un agente DQN decide cada día qué fracción del capital (0 %, 50 % o 100 %) mantener invertida en **GOOGL**. Aprende con datos de 2009 a 2015, compara dos funciones de recompensa en 2016 y se evalúa **una sola vez** en 2017–2018, un periodo que nunca vio, contra *comprar y mantener* y un *agente aleatorio*.

Construido sobre el repositorio base del curso, [`emiliomunozai/rl_games_sb`](https://github.com/emiliomunozai/rl_games_sb) (Stable-Baselines3 + Gymnasium + MLflow + Optuna). Su README original está en `docs/README_base_profesor.md`.

## Inicio rápido

```powershell
uv sync                                   # entorno .venv con Python 3.11
uv run python scripts/prueba_humo.py      # ≈1 min, debe terminar en "TODO OK"
```

Después abre `notebooks/Agente_Inversor.ipynb` en VS Code con el kernel `.venv` y ejecuta **Run All**. Los detalles de instalación están en **[CONFIGURACION_KERNEL.md](CONFIGURACION_KERNEL.md)**.

Por línea de comandos:

```powershell
uv run rlgames-sb train --config configs/investor_dqn_simple.yaml   # recompensa v1
uv run rlgames-sb train --config configs/investor_dqn_log_dd.yaml   # recompensa v2
uv run rlgames-sb tune  --config configs/investor_dqn_log_dd.yaml   # Optuna (opcional)
uv run mlflow ui                                                    # http://127.0.0.1:5000
```

## Diseño en una tabla

| Elemento | Decisión |
|---|---|
| Datos | GOOGL diario de `gym-anytrading` (dataset común del curso) |
| División | train 2009–2015 · validación 2016 · **held-out 2017–2018** |
| Estado | 7 indicadores del precio (retornos de 1, 5 y 20 días, distancia a SMA20 y SMA50, volatilidad de 20 días, RSI 14) normalizados con estadísticas de train, más la posición actual |
| Acciones | Discretas: 0 %, 50 %, 100 % del capital invertido |
| Ejecución | Decide con el cierre de *t* y ejecuta a ese precio; el precio de *t+1* solo se usa después |
| Costo | 0,1 % del monto negociado |
| Recompensa v1 | Retorno simple diario del portafolio (×100) |
| Recompensa v2 | Retorno log − λ · aumento del drawdown (×100, λ = 1) |
| Algoritmo | DQN (SB3), red MLP 64×64, 150.000 pasos, semilla 42 |
| Métricas | Retorno acumulado, máximo drawdown, costos, cambios de posición, exposición, Sharpe |

## Estructura

```
agente-inversor/
├── configs/
│   ├── investor_dqn_simple.yaml     # v1: hiperparámetros + espacio de búsqueda Optuna
│   └── investor_dqn_log_dd.yaml     # v2
├── notebooks/
│   └── Agente_Inversor.ipynb        # EDA → formulación → recompensas → held-out → discusión
├── scripts/prueba_humo.py           # verificación rápida del flujo completo
├── tests/                           # pruebas del entorno y de las métricas (pytest)
├── src/rl_games_sb/
│   ├── investor_data.py             # NUEVO · datos, indicadores, división temporal
│   ├── investor_env.py              # NUEVO · entorno Gymnasium de inversión
│   ├── investor_eval.py             # NUEVO · baselines y métricas
│   ├── envs.py                      # + registro de Investor-<recompensa>-v0 / -val-v0
│   ├── config.py, experiments.py    # + eval_env (evaluar en validación) y semilla en Optuna
│   └── cli.py, registry.py, tracking.py   # sin cambios (base del profesor)
├── docs/
│   ├── guia_equipo/                 # funciones, checklists, ejecución y flujo GitHub
│   ├── informe/                     # una sección del informe por archivo, cada una con dueño
│   ├── reflexiones/                 # una reflexión individual por integrante
│   ├── experimentos/                # Optuna y robustez por semillas
│   ├── decisiones.md                # bitácora de decisiones
│   └── pendientes.md
├── results/                         # figuras y métricas que genera el notebook
├── saves/                           # modelos entrenados (.zip de SB3, no se versionan)
├── CONFIGURACION_KERNEL.md
├── pyproject.toml, uv.lock, .python-version
└── CLAUDE.md
```

## Equipo

Cada integrante produce una parte de la entrega y verifica la de otro compañero mediante Pull Requests: ver **[docs/guia_equipo/01_funciones_y_checklists.md](docs/guia_equipo/01_funciones_y_checklists.md)**.

## Reglas del experimento

1. El periodo **held-out no se registra** como entorno. Solo `investor_eval.run(..., "test")` lo abre, y solo en la sección 8 del notebook.
2. Optuna y la comparación de recompensas usan **validación (2016)**, nunca el held-out.
3. Una vez visto el held-out, no se cambian recompensa, hiperparámetros ni arquitectura. Si se encuentra un **error** de código, se corrige, se documenta en `docs/decisiones.md` y se vuelve a correr todo.
