"""Robustez por semillas: reentrena una configuración con varias semillas y la evalúa en VALIDACIÓN.

    uv run python scripts/semillas.py --config configs/investor_dqn_log_dd.yaml
    uv run python scripts/semillas.py --config configs/investor_dqn_simple.yaml --seeds 42 1 7 123

Equivale al bloque RUN_SEEDS del notebook, pero sin editarlo (solo Diego edita el
notebook). Nunca usa el held-out ("test"). Los modelos no se guardan en saves/,
así que no pisa los de la corrida oficial. Escribe la tabla en
docs/experimentos/semillas_<nombre del config>.csv.
"""
import argparse
import time
from pathlib import Path

import pandas as pd

from rl_games_sb import config, investor_eval, registry

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="configs/investor_dqn_log_dd.yaml")
parser.add_argument("--seeds", type=int, nargs="+", default=[42, 1, 7, 123])
parser.add_argument("--timesteps", type=int, default=None, help="por defecto, los del YAML")
args = parser.parse_args()

cfg = config.load(args.config)
steps = args.timesteps or cfg.timesteps
filas = {}
for s in args.seeds:
    t0 = time.time()
    model = registry.create(cfg.algo, cfg.env, **{**cfg.hyperparams, "seed": s, "verbose": 0})
    model.learn(total_timesteps=steps)
    df = investor_eval.run(investor_eval.agent_policy(model), "val")
    m = investor_eval.metrics(df)
    m["minutos"] = (time.time() - t0) / 60
    filas[f"semilla {s}"] = m
    print(f"semilla {s}:", {k: round(v, 2) for k, v in m.items()}, flush=True)

tabla = pd.DataFrame(filas).T
tabla.loc["media"] = tabla.mean()
tabla.loc["desv. estándar"] = tabla.iloc[:-1].std()
bh = investor_eval.metrics(investor_eval.run(investor_eval.buy_and_hold, "val"))
tabla.loc["Comprar y mantener (ref.)"] = pd.Series(bh)

out = Path("docs/experimentos") / f"semillas_{Path(args.config).stem}.csv"
tabla.round(3).to_csv(out)
print(f"\n{tabla.round(2).to_string()}\n\nGuardado en {out}")
