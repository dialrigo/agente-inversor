# Configuración del kernel · Agente Inversor

El proyecto usa **uv** (como recomendó el profesor) y **Python 3.11**, que es la versión que exige `pyproject.toml` (`>=3.11, <3.12`). No usamos conda ni `pip install` para este proyecto.

> Si trabajas desde *Anaconda PowerShell*, primero ejecuta `conda deactivate` (hasta que no aparezca `(base)` en el prompt). Así evitas que VS Code o uv tomen el Python de conda.

---

## 1. Instalar uv (una sola vez por computador)

En **PowerShell** (normal, no hace falta administrador):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y vuelve a abrir la terminal y verifica:

```powershell
uv --version
```

uv descarga Python 3.11 por su cuenta (lo lee del archivo `.python-version`). No necesitas instalar Python aparte.

## 2. Crear el entorno del proyecto

```powershell
cd "$HOME\Documents\003 EFMIA\agente-inversor"
uv sync
```

Esto crea la carpeta `.venv\` con todas las dependencias exactas de `uv.lock` (Stable-Baselines3, Gymnasium, gym-anytrading, MLflow, Optuna, PyTorch, ipykernel…).

- **Primera vez:** puede tardar 5 a 10 minutos. PyTorch con CUDA pesa cerca de 2,5 GB.
- **GPU:** en Windows, uv instala PyTorch con CUDA 13.0 y, si no hay GPU NVIDIA compatible, usa la CPU. Para este proyecto **la CPU es suficiente**: los configs usan `device: cpu` porque una red MLP pequeña entrena más rápido en CPU.

Verifica la instalación:

```powershell
uv run python -c "import torch, stable_baselines3, gymnasium; print(torch.__version__, stable_baselines3.__version__, gymnasium.__version__, torch.cuda.is_available())"
```

## 3. Prueba de humo (≈1 minuto)

Antes de abrir el notebook, confirma que todo el flujo corre:

```powershell
uv run python scripts/prueba_humo.py
```

Debe terminar con `TODO OK`. Si falla, revisa la sección 6.

## 4. Kernel en VS Code

1. Instala las extensiones **Python** y **Jupyter** (Microsoft).
2. `File → Open Folder…` y abre la carpeta `agente-inversor` (la raíz, **no** la carpeta `notebooks`).
3. Abre `notebooks/Agente_Inversor.ipynb`.
4. Arriba a la derecha: **Select Kernel → Python Environments → `.venv (Python 3.11.x)`**. Su ruta termina en `agente-inversor\.venv\Scripts\python.exe`.
5. La primera celda imprime `Raíz del proyecto: ...\agente-inversor`. Si muestra otra ruta, el kernel no es el correcto.
6. **Run All**. Con `RETRAIN = True`, el entrenamiento de las dos versiones tarda unos 5 a 10 minutos en CPU.

Si `.venv` no aparece en la lista, usa *Select Another Kernel → Python Environments → Enter interpreter path* y selecciona `.venv\Scripts\python.exe`. Otra opción es reiniciar VS Code después de `uv sync`.

## 5. Ver los experimentos en MLflow

```powershell
uv run mlflow ui
```

Abre http://127.0.0.1:5000 → experimento **agente-inversor**. Ahí están los parámetros, la curva `rollout/ep_rew_mean` y el modelo de cada corrida.

## 6. Problemas comunes

| Síntoma | Solución |
|---|---|
| `uv` no se reconoce | Cerrar y abrir la terminal; si sigue igual, reiniciar sesión de Windows |
| `ModuleNotFoundError: rl_games_sb` en el notebook | El kernel no es el `.venv` del proyecto (paso 4) |
| El kernel usa Python de conda | `conda deactivate`, reiniciar VS Code y volver a elegir `.venv` |
| Error al compilar `box2d` | Ejecutar `uv sync` de nuevo; si persiste, instalar *Microsoft C++ Build Tools*. No afecta a este proyecto, que no usa Box2D, pero sí bloquea la instalación |
| Descarga de PyTorch muy lenta o cortada | Volver a ejecutar `uv sync`, que retoma desde la caché |
| `database is locked` (MLflow) | Cerrar la ventana de `mlflow ui` mientras entrenas |
| Resultados distintos entre integrantes | Normal en decimales entre máquinas. Para el informe vale **una** corrida oficial (la de Diego), guardada en `results/` |

## 7. Comandos útiles

```powershell
uv run rlgames-sb inspect --env Investor-simple-v0 --steps 5
uv run rlgames-sb train --config configs/investor_dqn_simple.yaml
uv run rlgames-sb train --config configs/investor_dqn_log_dd.yaml
uv run rlgames-sb tune  --config configs/investor_dqn_log_dd.yaml   # opcional, ~15 trials
uv run rlgames-sb delete dqn --env Investor-simple-v0               # borra el modelo guardado
```
