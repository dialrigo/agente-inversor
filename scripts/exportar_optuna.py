"""Exporta la búsqueda de Optuna registrada en MLflow a una tabla y una figura para el repo.

    uv run python scripts/exportar_optuna.py

Lee mlflow.db (no se versiona) y escribe, para la última corrida `tune-…`:
  - docs/experimentos/optuna_trials.csv : hiperparámetros, recompensa en validación y duración de cada trial
  - docs/experimentos/optuna_curvas.png : curvas de aprendizaje de los trials y recompensa en validación
Así cualquiera ve los trials en GitHub sin abrir `mlflow ui`.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DB = Path("mlflow.db")
OUT = Path("docs/experimentos")
HIGHLIGHT, MUTED, INK, INK2 = "#2a78d6", "#c9c8c3", "#0b0b0b", "#52514e"

con = sqlite3.connect(DB)
parent = con.execute(
    "SELECT run_uuid, name FROM runs WHERE name LIKE 'tune-%' ORDER BY start_time DESC LIMIT 1"
).fetchone()
trials = pd.read_sql(
    "SELECT r.run_uuid, r.name, r.start_time, r.end_time FROM runs r JOIN tags t "
    "ON t.run_uuid = r.run_uuid AND t.key = 'mlflow.parentRunId' WHERE t.value = ?",
    con, params=(parent[0],),
)
params = pd.read_sql("SELECT run_uuid, key, value FROM params", con).pivot(
    index="run_uuid", columns="key", values="value")
metrics = pd.read_sql("SELECT run_uuid, key, value, step FROM metrics", con)

trials["trial"] = trials["name"].str.removeprefix("trial-").astype(int)
trials = trials.sort_values("trial").set_index("run_uuid")
params = params.reindex(trials.index)
tabla = pd.DataFrame({
    "trial": trials["trial"],
    "learning_rate": params["learning_rate"].astype(float),
    "gamma": params["gamma"].astype(float),
    "exploration_fraction": params["exploration_fraction"].astype(float),
    "batch_size": params["batch_size"].astype(int),
    "recompensa_validacion": metrics[metrics.key == "eval/mean_reward"].set_index("run_uuid")["value"],
    "recompensa_entrenamiento_final": metrics[metrics.key == "rollout/ep_rew_mean"]
    .sort_values("step").groupby("run_uuid")["value"].last(),
    "minutos": (trials["end_time"] - trials["start_time"]) / 60_000,
}).sort_values("trial")
mejor = int(tabla.loc[tabla["recompensa_validacion"].idxmax(), "trial"])
tabla.round(6).to_csv(OUT / "optuna_trials.csv", index=False)

curvas = metrics[metrics.key == "rollout/ep_rew_mean"]
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.6, 1]})
for run, t in trials["trial"].items():
    c = curvas[curvas.run_uuid == run].sort_values("step")
    top = t == mejor
    a.plot(c["step"] / 1000, c["value"], color=HIGHLIGHT if top else MUTED,
           lw=2 if top else 1, zorder=3 if top else 2)
    if top:
        a.annotate(f"trial {t} (mejor)", (c["step"].iloc[-1] / 1000, c["value"].iloc[-1]),
                   xytext=(4, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
a.set_title("Curvas de aprendizaje en entrenamiento (2009-2015)", loc="left", fontsize=11, color=INK)
a.set_xlabel("Pasos de entrenamiento (miles)", color=INK2)
a.set_ylabel("Recompensa media por episodio", color=INK2)

orden = tabla.sort_values("recompensa_validacion")
colores = [HIGHLIGHT if t == mejor else MUTED for t in orden["trial"]]
b.barh([f"trial {t}" for t in orden["trial"]], orden["recompensa_validacion"], color=colores, height=0.7)
b.axvline(0, color=INK2, lw=0.8)
b.set_title("Recompensa en validación 2016", loc="left", fontsize=11, color=INK)
b.set_xlabel("Recompensa total del episodio", color=INK2)
b.tick_params(axis="y", labelsize=8)

for ax in (a, b):
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=INK2)
fig.suptitle(f"Optuna · {parent[1]} · {len(tabla)} trials × 50.000 pasos", x=0.01, ha="left",
             fontsize=12, color=INK)
fig.tight_layout()
fig.savefig(OUT / "optuna_curvas.png", dpi=150)
print(tabla.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
corr = tabla["recompensa_entrenamiento_final"].corr(tabla["recompensa_validacion"], method="spearman")
print(f"Correlación de Spearman entrenamiento vs validación: {corr:.2f}")
print(f"\nMejor trial: {mejor}. Guardado en {OUT / 'optuna_trials.csv'} y {OUT / 'optuna_curvas.png'}")
