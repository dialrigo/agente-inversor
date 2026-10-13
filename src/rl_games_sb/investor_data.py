"""Datos del Agente Inversor: precios, indicadores y división temporal.

Contents:
  - FEATURES      : nombres de los indicadores que observa el agente
  - TRAIN_END     : último día del periodo de entrenamiento
  - VAL_END       : último día del periodo de validación (el resto es held-out)
  - load_prices() : precios diarios de GOOGL incluidos en gym-anytrading
  - add_features(): indicadores calculados SOLO con información pasada
  - get_split()   : precios, indicadores normalizados y fechas de un periodo

Regla anti-lookahead: el indicador del día t usa precios hasta el cierre de t,
nunca de t+1. La normalización (media y desviación) se calcula solo con el
periodo de entrenamiento y se aplica igual a validación y prueba.
"""
from functools import cache

import numpy as np
import pandas as pd
from gym_anytrading.datasets import STOCKS_GOOGL

FEATURES = ("ret_1", "ret_5", "ret_20", "dist_sma20", "dist_sma50", "vol_20", "rsi_14")

TRAIN_END = "2015-12-31"  # 2009-2015: el agente aprende
VAL_END = "2016-12-31"    # 2016: selección de hiperparámetros (Optuna)
#                           2017-2018: held-out, solo para la evaluación final


def load_prices() -> pd.DataFrame:
    """Precios diarios de GOOGL (2009-05-22 a 2018-08-29), ya ajustados por split."""
    df = STOCKS_GOOGL[["Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega los indicadores. Todos son ventanas que terminan en el día t."""
    close = df["Close"]
    log_ret = np.log(close).diff()
    out = df.copy()
    out["ret_1"] = log_ret
    out["ret_5"] = np.log(close / close.shift(5))
    out["ret_20"] = np.log(close / close.shift(20))
    out["dist_sma20"] = close / close.rolling(20).mean() - 1
    out["dist_sma50"] = close / close.rolling(50).mean() - 1
    out["vol_20"] = log_ret.rolling(20).std()
    gain = log_ret.clip(lower=0).rolling(14).mean()
    loss = (-log_ret.clip(upper=0)).rolling(14).mean()
    out["rsi_14"] = 100 - 100 / (1 + gain / loss)
    return out.dropna()  # quita los ~50 días de calentamiento de las ventanas


@cache
def _table() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    df = add_features(load_prices())
    train = df.loc[:TRAIN_END, list(FEATURES)]
    return df, train.mean(), train.std()


def get_split(name: str) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
    """(precios, indicadores normalizados, fechas) de 'train', 'val' o 'test'."""
    df, mean, std = _table()
    d = df.index
    part = {
        "train": df[d <= TRAIN_END],
        "val": df[(d > TRAIN_END) & (d <= VAL_END)],
        "test": df[d > VAL_END],
    }[name]
    feats = ((part[list(FEATURES)] - mean) / std).clip(-5, 5)
    return part["Close"].to_numpy(), feats.to_numpy(np.float32), part.index
