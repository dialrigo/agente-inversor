"""Evaluación del Agente Inversor y de los baselines bajo las mismas condiciones.

Contents:
  - run()            : recorre un periodo completo con una política y guarda cada paso
  - agent_policy()   : política greedy (sin exploración) de un modelo entrenado
  - buy_and_hold()   : siempre 100 % invertido
  - random_policy()  : acción aleatoria con semilla fija
  - metrics()        : retorno acumulado, máximo drawdown, costos y otras
  - random_summary() : métricas del agente aleatorio promediadas en varias semillas

Todas las estrategias usan el mismo entorno, el mismo costo y el mismo capital
inicial. El periodo 'test' (held-out) solo debe usarse UNA vez, al final.
"""
from collections.abc import Callable

import numpy as np
import pandas as pd

from rl_games_sb.investor_env import InvestorEnv

Policy = Callable[[np.ndarray], int]


def run(policy: Policy, split: str = "test", cost: float = 0.001) -> pd.DataFrame:
    """Una fila por día: fecha, precio, acción, posición, valor, costo y recompensa.

    La primera fila es el día inicial, con el capital antes de operar.
    """
    env = InvestorEnv(split=split, reward="simple", cost=cost)
    obs, info = env.reset(seed=0)
    rows = [{"date": env.dates[0], "price": env.prices[0], "position": 0.0,
             "value": info["value"], "cost": 0.0, "traded": 0.0}]
    done = False
    while not done:
        obs, _, done, _, info = env.step(policy(obs))
        rows.append({"date": env.dates[env.t], "price": env.prices[env.t],
                     "position": info["position"], "value": info["value"],
                     "cost": info["cost"], "traded": info["traded"]})
    return pd.DataFrame(rows).set_index("date")


def agent_policy(model) -> Policy:
    return lambda obs: int(model.predict(obs, deterministic=True)[0])


def buy_and_hold(obs: np.ndarray) -> int:
    return 2  # 100 % invertido desde el primer día


def random_policy(seed: int) -> Policy:
    rng = np.random.default_rng(seed)
    return lambda obs: int(rng.integers(3))


def metrics(df: pd.DataFrame) -> dict[str, float]:
    value = df["value"]
    daily = value.pct_change().dropna()
    drawdown = 1 - value / value.cummax()
    return {
        "retorno_acumulado_%": 100 * (value.iloc[-1] / value.iloc[0] - 1),
        "max_drawdown_%": 100 * drawdown.max(),
        "costos_$": df["cost"].sum(),
        # cambios de la posición objetivo (0/50/100 %); no cuenta los pequeños
        # rebalanceos diarios que exige mantener el 50 %, aunque sí se cobran
        "cambios_de_posicion": int((df["position"].diff().iloc[1:] != 0).sum()),
        "exposicion_media_%": 100 * df["position"].iloc[1:].mean(),
        "sharpe_anual": float(np.sqrt(252) * daily.mean() / daily.std()) if daily.std() > 0 else 0.0,
        "valor_final_$": value.iloc[-1],
    }


def random_summary(split: str = "test", seeds: range = range(20)) -> pd.Series:
    """Promedio de las métricas del agente aleatorio en varias semillas."""
    return pd.DataFrame([metrics(run(random_policy(s), split)) for s in seeds]).mean()
