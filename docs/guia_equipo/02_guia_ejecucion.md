# Guía de ejecución paso a paso

Tiempo total la primera vez: unos 20 minutos, la mayor parte en la descarga de dependencias. La instalación detallada está en `CONFIGURACION_KERNEL.md`, en la raíz del repositorio.

## Paso 1 · Clonar e instalar

```powershell
git clone https://github.com/dialrigo/agente-inversor.git
cd agente-inversor
uv sync
```

## Paso 2 · Prueba de humo (≈1 min)

```powershell
uv run python scripts/prueba_humo.py
```

Entrena dos DQN diminutos (3.000 pasos), los evalúa en validación y corre 2 trials de Optuna, todo en una carpeta temporal. Debe terminar con **`TODO OK`**. Si no, avisa en el grupo con el error completo.

## Paso 3 · Abrir el notebook

1. VS Code → `File → Open Folder` → `agente-inversor`
2. `notebooks/Agente_Inversor.ipynb` → **Select Kernel** → `.venv (Python 3.11)`

## Paso 4 · Elegir el modo de ejecución (celda 1)

| Variable | Valor | Cuándo |
|---|---|---|
| `RETRAIN` | `True` | Corrida oficial o primera vez. Entrena v1 y v2 desde cero (≈5–10 min) |
| `RETRAIN` | `False` | Ya tienes `saves/*.zip` y solo quieres regenerar gráficas |
| `RUN_TUNE` | `True` | Búsqueda Optuna sobre validación (15 trials × 50k pasos, ≈20–30 min) |
| `RUN_SEEDS` | `True` | Robustez: reentrena la versión final con 3 semillas extra (≈10 min) |

## Paso 5 · Run All

Orden del notebook y qué mirar en cada parte:

| Sección | Qué produce | Revisa |
|---|---|---|
| 2 · Datos | Tabla de periodos, precio, retornos, volatilidad, drawdown del activo, indicadores | Rol 1 |
| 4 · Entorno | Pasos de ejemplo y 4 pruebas (deben decir `OK`) | Rol 2 |
| 5 · Recompensa v1 | Curva de aprendizaje, métricas y posiciones en **validación** | Rol 3 |
| 6 · Recompensa v2 | Lo mismo para v2 y la **selección** de la versión final | Rol 3 |
| 7 · Algoritmo | Tabla de hiperparámetros; Optuna opcional | Rol 3 |
| 8 · Held-out | Tabla final, curva de capital, drawdown y posiciones | Rol 4 |
| 9 · Anomalía | Tramo de peor desempeño frente a comprar y mantener | Rol 4 |
| 10–11 · Discusión | Texto y reflexiones individuales | Rol 6 |

Las figuras quedan en `results/*.png` y la tabla final en `results/metricas_heldout.csv`, listas para el informe.

## Paso 6 · MLflow

```powershell
uv run mlflow ui
```

En http://127.0.0.1:5000 → experimento `agente-inversor` están las corridas de entrenamiento (`dqn-Investor-simple-v0`, `dqn-Investor-log_dd-v0`) y, si corriste Optuna, una corrida `tune-...` con un trial anidado por cada combinación.

## Si algo falla

- **Las pruebas de la sección 4 fallan:** no sigas. Avisa a Nicolás (rol 2) y a Diego.
- **El notebook no encuentra `rl_games_sb`:** el kernel no es el `.venv`.
- **Resultados distintos a los oficiales en decimales:** es normal entre máquinas; los oficiales son los de `results/`.
- **Quiero probar otra idea:** hazlo en una rama propia, evalúa solo en validación y anótalo en `docs/pendientes.md`.
