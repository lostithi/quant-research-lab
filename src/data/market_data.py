from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parents[2] / "data_cache"
CACHE_DIR.mkdir(exist_ok=True)

@dataclass
class MarketDataRequest:
    ticker: str
    start: str = "2020-01-01"
    end: str | None = None
    interval: str = "1d"

def _cache_path(request: MarketDataRequest) -> Path:
    safe = f"{request.ticker}_{request.start}_{request.end or 'latest'}_{request.interval}.csv".replace(":", "-")
    return CACHE_DIR / safe

def load_market_data(request: MarketDataRequest, refresh: bool = False) -> pd.DataFrame:
    cache_file = _cache_path(request)
    if cache_file.exists() and not refresh:
        return pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")

    df = yf.download(
        request.ticker,
        start=request.start,
        end=request.end,
        interval=request.interval,
        auto_adjust=True,
        progress=False,
    )
    if df.empty:
        raise ValueError(f"No data returned for {request.ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    df = df[[c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]].dropna()
    df.index.name = "Date"
    df.to_csv(cache_file)
    return df

def load_multiple(tickers: list[str], start: str, end: str | None = None) -> dict[str, pd.DataFrame]:
    return {t: load_market_data(MarketDataRequest(ticker=t, start=start, end=end)) for t in tickers}