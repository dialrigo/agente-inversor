"""Pruebas de las métricas y de los baselines (investor_eval).

Se usan series pequeñas calculadas a mano y el periodo de validación (2016).
El held-out no se toca aquí: solo se abre en la corrida oficial del notebook.
"""
import math
import statistics
from itertools import pairwise

import pandas as pd
import pytest

from rl_games_sb import investor_data, investor_eval


def _serie(values, positions, costs):
    n = len(values)
    traded = [0.0] + [abs(b - a) for a, b in pairwise(positions)]
    return pd.DataFrame(
        {"value": values, "position": positions, "cost": costs, "traded": traded},
        index=pd.date_range("2020-01-01", periods=n),
    )


def test_metricas_serie_hecha_a_mano():
    # 100 → 120 → 90 → 110: gana 10 % en total; peor caída 120 → 90 = 25 %
    df = _serie([100, 120, 90, 110], [0.0, 1.0, 1.0, 1.0], [0.0, 0.1, 0.0, 0.0])
    m = investor_eval.metrics(df)
    assert m["retorno_acumulado_%"] == pytest.approx(10.0)
    assert m["max_drawdown_%"] == pytest.approx(25.0)
    assert m["costos_$"] == pytest.approx(0.1)
    assert m["cambios_de_posicion"] == 1        # solo la entrada inicial
    assert m["exposicion_media_%"] == pytest.approx(100.0)
    assert m["valor_final_$"] == pytest.approx(110.0)

    diarios = [120 / 100 - 1, 90 / 120 - 1, 110 / 90 - 1]
    sharpe = math.sqrt(252) * statistics.mean(diarios) / statistics.stdev(diarios)
    assert m["sharpe_anual"] == pytest.approx(sharpe)


def test_sin_caidas_drawdown_cero():
    df = _serie([100, 101, 102, 103], [0.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0])
    assert investor_eval.metrics(df)["max_drawdown_%"] == pytest.approx(0.0)


def test_efectivo_sin_volatilidad():
    df = _serie([100, 100, 100], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    m = investor_eval.metrics(df)
    assert m["retorno_acumulado_%"] == 0.0
    assert m["sharpe_anual"] == 0.0              # sin división por cero
    assert m["cambios_de_posicion"] == 0


def test_comprar_y_mantener_es_activo_menos_costo_de_entrada():
    # Verificación manual de la rúbrica: B&H ≈ retorno del activo − 0,1 % de entrada
    precios, _, _ = investor_data.get_split("val")
    df = investor_eval.run(investor_eval.buy_and_hold, "val")
    esperado = 100_000 * (1 - 0.001) * precios[-1] / precios[0]
    assert df["value"].iloc[-1] == pytest.approx(esperado)
    assert df["cost"].sum() == pytest.approx(100.0)
    assert investor_eval.metrics(df)["cambios_de_posicion"] == 1


def test_run_recorre_el_periodo_completo():
    precios, _, fechas = investor_data.get_split("val")
    df = investor_eval.run(investor_eval.buy_and_hold, "val")
    assert len(df) == len(precios)               # día inicial + un paso por día
    assert df.index[0] == fechas[0] and df.index[-1] == fechas[-1]
    assert df["value"].iloc[0] == 100_000


def test_agente_aleatorio_reproducible_con_semilla():
    a = investor_eval.run(investor_eval.random_policy(7), "val")
    b = investor_eval.run(investor_eval.random_policy(7), "val")
    c = investor_eval.run(investor_eval.random_policy(8), "val")
    pd.testing.assert_frame_equal(a, b)
    assert not a["position"].equals(c["position"])
