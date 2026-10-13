"""Entorno de simulación de inversión en un activo (interfaz Gymnasium).

Contents:
  - ACTIONS      : fracción del capital invertida por cada acción discreta
  - REWARDS      : variantes de recompensa disponibles
  - InvestorEnv  : el entorno

Cronología de un paso (lookahead-safe):
  1. Al cierre del día t el agente observa los indicadores de t (calculados con
     precios hasta t) y su posición actual.
  2. Elige la fracción objetivo a_t ∈ {0 %, 50 %, 100 %}. La orden se ejecuta al
     precio de cierre de t (supuesto "market on close") y paga
     costo = COST × |a_t − posición actual| × valor del portafolio.
  3. El precio pasa de P_t a P_{t+1}; el portafolio gana a_t × (P_{t+1}/P_t − 1).
  4. Se calcula la recompensa con V_{t+1} y se entrega la observación de t+1.
El precio de t+1 solo se usa DESPUÉS de que la acción quedó fija.
"""
import gymnasium as gym
import numpy as np

from rl_games_sb import investor_data

ACTIONS = (0.0, 0.5, 1.0)
REWARDS = ("simple", "log", "log_dd")


class InvestorEnv(gym.Env):
    """Decide qué fracción del capital mantener invertida en GOOGL.

    reward:
      - "simple": retorno simple del portafolio, (V_{t+1} − V_t) / V_t
      - "log":    retorno logarítmico, log(V_{t+1} / V_t)
      - "log_dd": retorno log − dd_penalty × aumento del drawdown en el paso
    Los costos ya están descontados de V_{t+1}, así que toda recompensa los incluye.
    La recompensa se multiplica por `reward_scale` (×100 = puntos porcentuales)
    para que la red no aprenda con números del orden de 0,001; no cambia la
    política óptima.
    """

    def __init__(
        self,
        split: str = "train",
        reward: str = "simple",
        cost: float = 0.001,
        episode_len: int | None = 252,
        initial_cash: float = 100_000.0,
        dd_penalty: float = 1.0,
        reward_scale: float = 100.0,
        render_mode: str | None = None,  # sin render; gym.make siempre lo pasa
    ):
        assert reward in REWARDS, reward
        self.render_mode = render_mode
        self.prices, self.feats, self.dates = investor_data.get_split(split)
        self.reward_kind = reward
        self.cost = cost
        # En validación y prueba un episodio recorre el periodo completo.
        self.episode_len = episode_len if split == "train" else None
        self.initial_cash = initial_cash
        self.dd_penalty = dd_penalty
        self.reward_scale = reward_scale

        # indicadores normalizados (recortados a ±5) + posición actual (0 a 1)
        n_feats = self.feats.shape[1] + 1
        self.observation_space = gym.spaces.Box(-5.0, 5.0, (n_feats,), np.float32)
        self.action_space = gym.spaces.Discrete(len(ACTIONS))

    def _obs(self) -> np.ndarray:
        return np.append(self.feats[self.t], np.float32(self.weight)).astype(np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        last = len(self.prices) - 1
        if self.episode_len:  # entrenamiento: una ventana aleatoria de ~1 año
            self.t = int(self.np_random.integers(0, last - self.episode_len))
            self.end = self.t + self.episode_len
        else:
            self.t, self.end = 0, last
        self.value = self.peak = self.initial_cash
        self.weight = 0.0
        return self._obs(), {"value": self.value}

    def step(self, action):
        target = ACTIONS[int(action)]
        traded = abs(target - self.weight)
        cost = self.cost * traded * self.value

        asset_ret = self.prices[self.t + 1] / self.prices[self.t] - 1
        new_value = (self.value - cost) * (1 + target * asset_ret)

        if self.reward_kind == "simple":
            reward = new_value / self.value - 1
        else:
            reward = np.log(new_value / self.value)
            if self.reward_kind == "log_dd":
                dd_before = 1 - self.value / self.peak
                dd_after = 1 - new_value / max(self.peak, new_value)
                reward -= self.dd_penalty * max(0.0, dd_after - dd_before)

        # Tras el movimiento del precio la fracción invertida se desplaza.
        self.weight = target * (1 + asset_ret) / (1 + target * asset_ret)
        self.value = new_value
        self.peak = max(self.peak, new_value)
        self.t += 1

        info = {"value": self.value, "position": target, "cost": cost, "traded": traded}
        terminated = self.t >= self.end
        return self._obs(), float(reward * self.reward_scale), terminated, False, info
