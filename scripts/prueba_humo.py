"""Prueba de humo (~1 minuto): verifica que todo el flujo corre antes del Run All.

    uv run python scripts/prueba_humo.py

Entrena un DQN diminuto (3.000 pasos) en un directorio temporal, sin tocar
saves/ ni mlflow.db del proyecto. Si termina con "TODO OK", el notebook corre.
"""
import os
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="agente_inversor_"))
os.environ["MLFLOW_TRACKING_URI"] = f"sqlite:///{(tmp / 'mlflow.db').as_posix()}"

from rl_games_sb import config, envs, experiments, investor_eval, registry

registry.SAVE_DIR = tmp / "saves"
registry.SAVE_DIR.mkdir()

for name in ("simple", "log_dd"):
    cfg = config.load(f"configs/investor_dqn_{name}.yaml")
    cfg.timesteps = 3_000
    cfg.hyperparams["learning_starts"] = 500
    experiments.train(cfg)
    model = registry.load(cfg.algo, cfg.env, device="cpu")
    m = investor_eval.metrics(investor_eval.run(investor_eval.agent_policy(model), "val"))
    print(f"[{name}] validación:", {k: round(v, 2) for k, v in m.items()})

cfg.tune["trials"], cfg.tune["timesteps"] = 2, 1_000
experiments.tune(cfg)
print("Entorno registrado:", "Investor-simple-v0" in envs.gym.registry)
print(f"\nTODO OK (archivos temporales en {tmp})")
