import pandas as pd

def run_backtest(
    price_df: pd.DataFrame,
    signal_df: pd.DataFrame,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    initial_capital: float = 10000.0
) -> pd.DataFrame:
    df = price_df.copy()
    df = df.join(signal_df[["signal", "position_change"]], how="left")
    df[["signal", "position_change"]] = df[["signal", "position_change"]].fillna(0.0)

    df["asset_return"] = df["Close"].pct_change().fillna(0.0)
    df["strategy_return_gross"] = df["signal"].shift(1).fillna(0.0) * df["asset_return"]

    trade_cost = (abs(df["position_change"]) * (fee_bps + slippage_bps)) / 10000.0
    df["trade_cost"] = trade_cost
    df["strategy_return_net"] = df["strategy_return_gross"] - df["trade_cost"]

    df["asset_equity"] = initial_capital * (1 + df["asset_return"]).cumprod()
    df["strategy_equity"] = initial_capital * (1 + df["strategy_return_net"]).cumprod()
    df["drawdown"] = df["strategy_equity"] / df["strategy_equity"].cummax() - 1.0
    return df