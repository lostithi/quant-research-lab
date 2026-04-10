import numpy as np
import pandas as pd

def moving_average_crossover(close: pd.Series, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")
    df = pd.DataFrame(index=close.index)
    df["close"] = close
    df["short_ma"] = close.rolling(short_window).mean()
    df["long_ma"] = close.rolling(long_window).mean()
    df["signal"] = np.where(df["short_ma"] > df["long_ma"], 1.0, 0.0)
    df["position_change"] = df["signal"].diff().fillna(0.0)
    return df

def mean_reversion_zscore(close: pd.Series, window: int = 20, entry_z: float = 1.0, exit_z: float = 0.2) -> pd.DataFrame:
    df = pd.DataFrame(index=close.index)
    df["close"] = close
    rolling_mean = close.rolling(window).mean()
    rolling_std = close.rolling(window).std()
    df["zscore"] = (close - rolling_mean) / rolling_std.replace(0, np.nan)

    signal = np.zeros(len(df))
    in_position = 0.0
    for i, z in enumerate(df["zscore"].fillna(0.0)):
        if in_position == 0.0 and z < -entry_z:
            in_position = 1.0
        elif in_position == 1.0 and z > -exit_z:
            in_position = 0.0
        signal[i] = in_position

    df["signal"] = signal
    df["position_change"] = df["signal"].astype(float).diff().fillna(0.0)
    return df