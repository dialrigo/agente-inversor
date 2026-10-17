"""Pruebas del entorno del Agente Inversor (InvestorEnv) y de sus datos.

    uv run pytest

Ninguna prueba abre el periodo held-out ("test"): se usan entrenamiento,
validación o precios sintéticos.
"""
import numpy as np
import pandas as pd
import pytest

from rl_games_sb import envs, investor_data
from rl_games_sb.investor_env import ACTIONS, InvestorEnv

CASH = 100_000.0


def make_env(prices: list[float]) -> InvestorEnv:
    """Entorno de validación con precios sintéticos, para calcular a mano."""
    env = InvestorEnv(split="val")
    env.prices = np.array(prices)
    env.reset(seed=0)
    return env


# Prueba 1 · lookahead: el indicador del día t no cambia si borramos todo lo
# posterior a t. Posiciones dentro de train y validación (≤ 2016).
@pytest.mark.parametrize("pos", [0, 100, 1000, 1615, 1800])
def test_indicadores_sin_lookahead(pos):
    prices = investor_data.load_prices()
    feats = list(investor_data.FEATURES)
    full = investor_data.add_features(prices)
    t = full.index[pos]
    assert t <= pd.Timestamp(investor_data.VAL_END)
    cortado = investor_data.add_features(prices.loc[:t])
    assert np.allclose(full.loc[t, feats], cortado.loc[t, feats])


# Prueba 2 · costo: pasar de 0 % a 100 % con $100.000 cuesta 0,1 % = $100.
def test_costo_entrar_al_100():
    env = InvestorEnv(split="val")
    env.reset(seed=0)
    _, _, _, _, info = env.step(2)
    assert info["cost"] == pytest.approx(100.0)
    assert info["traded"] == 1.0


# Prueba 3 · en efectivo (0 %) el valor no cambia, no se cobran costos y la
# recompensa es cero, aunque el precio se mueva.
def test_efectivo_estable():
    env = InvestorEnv(split="val")
    env.reset(seed=0)
    for _ in range(20):
        _, reward, _, _, info = env.step(0)
        assert info["value"] == CASH
        assert info["cost"] == 0.0
        assert reward == 0.0


# Prueba 4 · un paso calculado a mano: entrar al 100 % cuesta $100
# (100.000 → 99.900) y el precio sube 1 % (99.900 × 1,01 = 100.899).
def test_paso_calculado_a_mano():
    env = make_env([100.0, 101.0, 101.0])
    obs, reward, terminated, _, info = env.step(2)
    assert info["value"] == pytest.approx(100_899.0)
    assert reward == pytest.approx((100_899 / 100_000 - 1) * 100)  # 0,899 p. p.
    assert obs[-1] == pytest.approx(1.0)
    assert not terminated


# Prueba 5 · el held-out no está registrado en Gymnasium: solo se abre desde
# investor_eval para la evaluación final.
def test_heldout_no_registrado():
    investor = {k: s for k, s in envs.gym.registry.items() if k.startswith("Investor")}
    assert len(investor) == 6  # 3 recompensas × (train, val)
    for env_id, spec in investor.items():
        assert "test" not in env_id
        assert spec.kwargs["split"] in ("train", "val")


# Prueba 6 · la observación es los 7 indicadores (en el orden de FEATURES) más
# la posición actual, y las acciones son {0 %, 50 %, 100 %}.
def test_observacion_y_acciones():
    env = InvestorEnv(split="val")
    obs, _ = env.reset(seed=0)
    assert obs.shape == (len(investor_data.FEATURES) + 1,)
    assert np.array_equal(obs[:-1], env.feats[0])
    assert obs[-1] == 0.0
    assert ACTIONS == (0.0, 0.5, 1.0)
    assert env.action_space.n == 3


# Prueba 7 · desplazamiento del 50 %: si el precio sube 1 %, la parte invertida
# pasa a 0,5 × 1,01 / 1,005 ≈ 50,25 %, y volver a pedir 50 % cobra un
# rebalanceo pequeño.
def test_desplazamiento_del_50():
    env = make_env([100.0, 101.0, 101.0, 101.0])
    obs, _, _, _, info = env.step(1)
    assert info["cost"] == pytest.approx(50.0)
    assert info["value"] == pytest.approx(99_950 * 1.005)
    assert obs[-1] == pytest.approx(0.5 * 1.01 / 1.005)

    _, _, _, _, info = env.step(1)
    assert info["traded"] == pytest.approx(0.5 * 1.01 / 1.005 - 0.5)
    assert 0 < info["cost"] < 1
