# Reproducibilidad

## Requisitos y comandos (uv sync, prueba de humo, Run All)

Requisitos: Git, [uv](https://docs.astral.sh/uv/) y Python 3.11 (uv lo instala si falta; ver `.python-version`). No hace falta GPU. El dataset es GOOGL diario (2009-05-22 a 2018-08-29) incluido en el paquete `gym-anytrading` (`STOCKS_GOOGL`), así que no hay que descargar nada aparte.

```powershell
git clone https://github.com/dialrigo/agente-inversor.git
cd agente-inversor
uv sync                                   # instala las versiones exactas de uv.lock
uv run python scripts/prueba_humo.py      # ≈ 20 s, debe terminar en "TODO OK"
```

| Paso | Comando | Resultado |
|---|---|---|
| Entrenar v1 (retorno simple) | `uv run rlgames-sb train --config configs/investor_dqn_simple.yaml` | modelo en `saves/` + corrida en MLflow |
| Entrenar v2 (log − drawdown, versión final) | `uv run rlgames-sb train --config configs/investor_dqn_log_dd.yaml` | ídem |
| Entrenar v3 (log, control) | `uv run rlgames-sb train --config configs/investor_dqn_log.yaml` | ídem |
| Búsqueda Optuna (validación) | `uv run rlgames-sb tune --config configs/investor_dqn_log_dd.yaml` | corrida `tune-…` en MLflow |
| Robustez por semillas (validación) | `uv run python scripts/semillas.py --config configs/investor_dqn_log_dd.yaml` | `docs/experimentos/semillas_investor_dqn_log_dd.csv` |
| Tabla y figura de los trials de Optuna | `uv run python scripts/exportar_optuna.py` (después de la búsqueda; lee `mlflow.db`) | `docs/experimentos/optuna_trials.csv`, `docs/experimentos/optuna_curvas.png` |
| Evaluación held-out, baselines y figuras | Abrir `notebooks/Agente_Inversor.ipynb` con el kernel `.venv` → **Run All** (`RETRAIN = True`) | `results/*.png`, `results/metricas_heldout.csv` |
| Pruebas automáticas | `uv run pytest` | entorno y métricas |
| Ver experimentos | `uv run mlflow ui` → http://127.0.0.1:5000 | |

`mlflow.db` y `mlruns/` (registro local de MLflow) y `saves/` (modelos entrenados) no se versionan; cada quien los genera al correr los comandos. El detalle de qué comando produce cada archivo de `docs/experimentos/` está en `docs/experimentos/optuna_y_semillas.md`.

Los baselines (comprar y mantener, aleatorio) se ejecutan dentro del notebook con `investor_eval.buy_and_hold` y `investor_eval.random_policy`, en el mismo entorno, periodo y costo que el agente.

## Semillas fijas y dónde se fijan

| Qué | Dónde | Valor |
|---|---|---|
| Python `random`, NumPy, PyTorch (notebook) | Celda 1 del notebook (`SEED`) | 42 |
| Red, *replay buffer*, ε-greedy e inicio de episodios de entrenamiento (SB3) | `hyperparams.seed` en `configs/*.yaml` | 42 |
| Sampler TPE de Optuna | `experiments.tune` usa `hyperparams.seed` | 42 |
| Episodios de evaluación | `investor_eval.run` → `env.reset(seed=0)`; en validación y held-out el episodio es el periodo completo, sin azar | 0 |
| Agente aleatorio | `random_policy(SEED)` en la curva; media de 20 semillas (0–19) en la tabla | 42; 0–19 |
| Robustez | `scripts/semillas.py` | 42, 1, 7, 123 |

**Verificación en la misma máquina.** La prueba de humo se corrió dos veces seguidas y dio resultados **idénticos** (mismas recompensas de entrenamiento, mismas métricas en validación y mismos valores de los 2 trials de Optuna). Con las semillas fijas, el experimento es determinista dentro de una misma máquina.

**Entre máquinas no es idéntico.** PyTorch no garantiza resultados bit a bit iguales entre sistemas operativos o CPU; en un entrenamiento de 150.000 pasos las diferencias mínimas de punto flotante se acumulan. Por eso los resultados oficiales son los de `results/` (corrida de Diego) y aquí se cuantifica cuánto cambian en otra máquina.

## Versiones usadas (Python, torch, SB3, gymnasium)

Instaladas por `uv sync` desde `uv.lock` (máquina de Marlon, 2026-10-17):

| Paquete | Versión |
|---|---|
| uv | 0.12.17 |
| Python | 3.11.9 |
| torch | 2.14.1+cu130 (se ejecuta en CPU: `device: cpu`) |
| stable-baselines3 | 2.9.0 |
| gymnasium | 1.4.0 |
| optuna | 5.0.0 |
| mlflow | 3.16.1 |

## Prueba en una segunda máquina: tiempo y diferencias con la corrida oficial

Máquina: PC de Marlon, Windows (x64), CPU. Clonado desde cero el 2026-10-17 siguiendo solo `README.md` y `CONFIGURACION_KERNEL.md`.

| Paso | Tiempo |
|---|---|
| Prueba de humo | 0,27 min (≈ 16 s) |
| Optuna (15 trials × 50.000 pasos) | 8 min |
| Un entrenamiento completo (150.000 pasos) | ≈ 2 min |
| Semillas (4 × 150.000 pasos, dos configuraciones en paralelo) | ≈ 10 min |

**Pasos que fallaron o confundieron.**

- La guía funcionó sin cambios: `uv sync`, la prueba de humo y la búsqueda de Optuna corrieron a la primera.
- En PowerShell, al redirigir la salida a un archivo (`|`, `Tee-Object`), los acentos salen mal (`validaci¾n`) y los logs quedan en UTF-16. Se evita con `$env:PYTHONIOENCODING="utf-8"` antes de correr. Además, PowerShell envuelve los mensajes de MLflow (que van a stderr) como `NativeCommandError`; no es un error real.
- Con la salida redirigida a un archivo, Python no escribe nada hasta terminar; si se cierra la ventana antes, se pierde todo. `scripts/semillas.py` ahora escribe cada semilla al terminarla (`flush=True`).

**Diferencias con la corrida oficial.** La versión final (v2, semilla 42, hiperparámetros del YAML) evaluada en validación 2016 en tres máquinas:

| Métrica | Corrida oficial (`results/`, notebook) | Máquina de Marlon (`scripts/semillas.py`) | Corrida exploratoria de janayajoo |
|---|---|---|---|
| Retorno acumulado % | 8,99 | 6,12 | 8,48 |
| Máximo drawdown % | 8,61 | 6,27 | 6,27 |
| Costos USD | 3.097 | 2.982 | 2.915 |
| Cambios de posición | 32 | 31 | 32 |
| Exposición media % | 19,3 | 17,7 | 19,3 |
| Sharpe anual | 1,02 | 0,76 | 0,98 |

La **conducta** del agente se reproduce (31–32 cambios de posición, ~18–19 % del tiempo invertido, mismo patrón de refugio en efectivo), pero las cifras exactas no: el retorno varía hasta ~3 puntos y el drawdown ~2,3 puntos entre máquinas. Con la misma semilla, las diferencias mínimas de punto flotante entre equipos se acumulan a lo largo de 150.000 pasos de entrenamiento y terminan en redes algo distintas. Esa variación es menor que la que hay entre semillas en una misma máquina (desviación de 5,4 puntos de retorno, ver `docs/experimentos/optuna_y_semillas.md`), pero implica que las cifras de un solo entrenamiento deben leerse con un margen de algunos puntos. Las que valen para el informe son las de la corrida oficial.
