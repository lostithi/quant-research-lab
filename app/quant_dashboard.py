import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.backtest.engine import run_backtest
from src.data.market_data import MarketDataRequest, load_market_data, load_multiple
from src.risk.metrics import compute_metrics, rolling_sharpe, compute_alpha_beta
from src.strategies.signals import moving_average_crossover, mean_reversion_zscore
from src.backtest.optimiser import sweep_ma_parameters

st.set_page_config(page_title="Quant Research Lab", layout="wide", page_icon="📈")

st.markdown("## Quant Research Lab")
st.caption("Backtesting · Risk Analytics · Strategy Optimisation")
st.divider()


with st.sidebar:
    st.header("Configuration")
    tickers = st.multiselect(
        "Tickers",
        options=["SPY", "QQQ", "AAPL", "MSFT", "TSLA", "BTC-USD", "GLD"],
        default=["SPY"]
    )
    if not tickers:
        st.warning("Please select at least one ticker.")
        st.stop()

    start    = st.date_input("Start date", value=pd.to_datetime("2020-01-01"))
    strategy = st.selectbox("Strategy", ["Moving Average Crossover", "Mean Reversion"])
    st.divider()
    st.subheader("Execution costs")
    fee_bps         = st.slider("Fees (bps)",     0, 50,  5)
    slippage_bps    = st.slider("Slippage (bps)", 0, 50,  2)
    initial_capital = st.number_input("Initial capital (£)", min_value=1000.0,
                                      value=10000.0, step=1000.0)
    st.divider()
    st.subheader("Strategy parameters")
    if strategy == "Moving Average Crossover":
        short_window = st.slider("Short MA", 5,  50,  20)
        long_window  = st.slider("Long MA",  20, 200, 50)
    else:
        window  = st.slider("Z-score window", 5,   60,  20)
        entry_z = st.slider("Entry z-score",  0.5, 3.0, 1.0, 0.1)
        exit_z  = st.slider("Exit z-score",   0.0, 1.5, 0.2, 0.1)


with st.spinner("Loading market data..."):
    all_data = load_multiple(tickers, start=str(start))


all_backtests: dict[str, pd.DataFrame] = {}
all_metrics:   dict[str, dict]         = {}

for ticker, price_df in all_data.items():
    if strategy == "Moving Average Crossover":
        signal_df = moving_average_crossover(price_df["Close"], short_window, long_window)
    else:
        signal_df = mean_reversion_zscore(price_df["Close"], window, entry_z, exit_z)

    bt = run_backtest(price_df, signal_df,
                      fee_bps=fee_bps,
                      slippage_bps=slippage_bps,
                      initial_capital=initial_capital)
    m = compute_metrics(bt)


    try:
        if ticker != "SPY":
            spy_df  = load_market_data(MarketDataRequest(ticker="SPY", start=str(start)))
            spy_ret = spy_df["Close"].pct_change().dropna()
        else:
            spy_ret = price_df["Close"].pct_change().dropna()
        ab = compute_alpha_beta(bt["strategy_return_net"].dropna(), spy_ret)
        m.update(ab)
    except Exception:
        pass

    all_backtests[ticker] = bt
    all_metrics[ticker]   = m

st.subheader("Per-ticker detail")
selected = st.selectbox("Inspect ticker", tickers)
backtest_df = all_backtests[selected]
metrics     = all_metrics[selected]
price_df    = all_data[selected]

fmt = {
    "Sharpe Ratio":  lambda v: f"{v:.2f}",
    "Beta":          lambda v: f"{v:.2f}",
    "Alpha (daily)": lambda v: f"{v:.4f}",
}
kpi_cols = st.columns(len(metrics))
for col, (key, value) in zip(kpi_cols, metrics.items()):
    col.metric(key, fmt.get(key, lambda v: f"{v:.2%}")(value))

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Equity Curve", "Drawdown & Risk",
    "Optimisation Heatmap", "Trade Log", "Compare Tickers"
])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=backtest_df.index, y=backtest_df["asset_equity"],
                             name="Buy & Hold", line=dict(color="#636EFA")))
    fig.add_trace(go.Scatter(x=backtest_df.index, y=backtest_df["strategy_equity"],
                             name="Strategy",   line=dict(color="#EF553B")))
    fig.update_layout(title=f"Equity Curve — {selected}", template="plotly_dark",
                      xaxis_title="Date", yaxis_title="Portfolio Value (£)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    roll = rolling_sharpe(backtest_df["strategy_return_net"].dropna())
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=roll.index, y=roll,
                              name="Rolling Sharpe (63d)", line=dict(color="#00CC96")))
    fig2.add_hline(y=1.0, line_dash="dash", line_color="white", annotation_text="Sharpe = 1")
    fig2.update_layout(title="Rolling Sharpe Ratio", template="plotly_dark",
                       xaxis_title="Date", yaxis_title="Sharpe")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=backtest_df.index, y=backtest_df["drawdown"],
                              fill="tozeroy", name="Drawdown",
                              line=dict(color="#EF553B")))
    fig3.update_layout(title="Strategy Drawdown", template="plotly_dark",
                       xaxis_title="Date", yaxis_title="Drawdown %",
                       yaxis_tickformat=".1%")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Return Distribution")
    ret  = backtest_df["strategy_return_net"].dropna() * 100
    fig4 = px.histogram(ret, nbins=80, template="plotly_dark",
                        labels={"value": "Daily Return (%)", "count": "Frequency"},
                        title="Daily Return Distribution")
    fig4.add_vline(x=0, line_dash="dash", line_color="white")
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    if strategy == "Moving Average Crossover":
        if st.button("Run parameter sweep"):
            with st.spinner("Sweeping MA parameters..."):
                sweep_df = sweep_ma_parameters(price_df, fee_bps=fee_bps,
                                               slippage_bps=slippage_bps)
            pivot = sweep_df.pivot(index="short", columns="long", values="Sharpe Ratio")
            fig5  = px.imshow(pivot, color_continuous_scale="RdYlGn",
                              labels=dict(x="Long MA", y="Short MA", color="Sharpe Ratio"),
                              title=f"Sharpe Ratio Heatmap — {selected}",
                              template="plotly_dark")
            st.plotly_chart(fig5, use_container_width=True)
            st.dataframe(sweep_df.sort_values("Sharpe Ratio", ascending=False).head(10),
                         use_container_width=True)
    else:
        st.info("Parameter sweep is currently available for Moving Average Crossover only.")

with tab4:
    trades = backtest_df[backtest_df["position_change"] != 0][
        ["Close", "signal", "position_change", "strategy_return_net", "strategy_equity"]
    ].copy()
    trades.columns = ["Price", "Signal", "Change", "Return", "Equity"]
    trades["Action"] = trades["Change"].apply(lambda x: "BUY" if x > 0 else "SELL")
    st.dataframe(trades.style.map(
        lambda v: "color: #00CC96" if v == "BUY" else "color: #EF553B",
        subset=["Action"]
    ), use_container_width=True)
    st.caption(f"Total trades: {len(trades)}")

with tab5:
    st.subheader("Strategy equity curve — all tickers")
    fig6 = go.Figure()
    for t, bt in all_backtests.items():
        fig6.add_trace(go.Scatter(x=bt.index, y=bt["strategy_equity"],
                                  name=f"{t} Strategy"))
        fig6.add_trace(go.Scatter(x=bt.index, y=bt["asset_equity"],
                                  name=f"{t} Buy & Hold",
                                  line=dict(dash="dot")))
    fig6.update_layout(title="All Tickers — Strategy vs Buy & Hold",
                       template="plotly_dark",
                       xaxis_title="Date", yaxis_title="Portfolio Value (£)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Metrics comparison table")
    comparison = pd.DataFrame(all_metrics).T
    comparison.index.name = "Ticker"
    fmt_map = {"Sharpe Ratio": "{:.2f}", "Beta": "{:.2f}", "Alpha (daily)": "{:.4f}"}
    st.dataframe(
        comparison.style.format({
            col: fmt_map.get(col, "{:.2%}") for col in comparison.columns
        }).background_gradient(subset=["Sharpe Ratio"], cmap="RdYlGn"),
        use_container_width=True
    )