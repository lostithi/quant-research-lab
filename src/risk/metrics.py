import numpy as np
import pandas as pd

def compute_metrics(backtest_df: pd.DataFrame, periods_per_year: int = 252) -> dict:
    returns = backtest_df["strategy_return_net"].dropna()
    equity = backtest_df["strategy_equity"].dropna()
    if returns.empty or equity.empty:
        raise ValueError("Backtest dataframe does not contain valid returns/equity")

    total_return = equity.iloc[-1] / equity.iloc[0] - 1
    annualized_return = (1 + total_return) ** (periods_per_year / max(len(returns), 1)) - 1
    volatility = returns.std(ddof=0) * np.sqrt(periods_per_year)
    sharpe = (returns.mean() * periods_per_year) / volatility if volatility > 0 else 0.0
    max_drawdown = backtest_df["drawdown"].min()
    win_rate = (returns > 0).sum() / max((returns != 0).sum(), 1)

    return {
        "Total Return": float(total_return),
        "Annualized Return": float(annualized_return),
        "Volatility": float(volatility),
        "Sharpe Ratio": float(sharpe),
        "Max Drawdown": float(max_drawdown),
        "Win Rate": float(win_rate),
    }

def rolling_sharpe(returns: pd.Series, window: int = 63, periods_per_year: int = 252) -> pd.Series:
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std(ddof=0)
    return (rolling_mean * periods_per_year) / (rolling_std * (periods_per_year ** 0.5) + 1e-9)

def compute_alpha_beta(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> dict:
    import numpy as np
    aligned = pd.concat([strategy_returns, benchmark_returns], axis=1).dropna()
    aligned.columns = ["strategy", "benchmark"]
    cov = np.cov(aligned["strategy"], aligned["benchmark"])
    beta = cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else 0.0
    alpha = aligned["strategy"].mean() - beta * aligned["benchmark"].mean()
    return {"Alpha (daily)": float(alpha), "Beta": float(beta)}