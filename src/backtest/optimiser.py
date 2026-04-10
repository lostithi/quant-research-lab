import itertools
import pandas as pd
from src.strategies.signals import moving_average_crossover
from src.backtest.engine import run_backtest
from src.risk.metrics import compute_metrics

def sweep_ma_parameters(
    price_df: pd.DataFrame,
    short_range: range = range(5, 50, 5),
    long_range: range = range(20, 200, 10),
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> pd.DataFrame:
    results = []
    for short, long in itertools.product(short_range, long_range):
        if short >= long:
            continue
        try:
            signals = moving_average_crossover(price_df["Close"], short, long)
            bt = run_backtest(price_df, signals, fee_bps=fee_bps, slippage_bps=slippage_bps)
            metrics = compute_metrics(bt)
            results.append({"short": short, "long": long, **metrics})
        except Exception:
            continue
    return pd.DataFrame(results)