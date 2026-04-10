# 📈 Quant Research Lab

A modular quantitative research and backtesting platform built in Python.
Designed to simulate, evaluate, and compare trading strategies across multiple assets
with interactive risk analytics and strategy optimisation tools.

🔗 **[Live Demo →](https://quant-research-lab.streamlit.app/)**

---

## Screenshot

> *()*

---

## Overview

This project was built to demonstrate core quantitative developer skills:
modular Python engineering, financial data pipelines, strategy backtesting,
risk analytics, and interactive data visualisation.

It supports multiple assets, two configurable trading strategies, parameter
optimisation via heatmap, and a full trade log — all through an interactive
Streamlit dashboard.

---

## Features

- **Multi-asset support** — backtest across SPY, QQQ, AAPL, MSFT, TSLA, BTC-USD, GLD simultaneously
- **Two trading strategies** — Moving Average Crossover and Mean Reversion (z-score)
- **Realistic execution model** — configurable fees and slippage in basis points
- **Risk analytics** — Sharpe ratio, annualised return, volatility, max drawdown, win rate, alpha, beta
- **Rolling Sharpe chart** — see how risk-adjusted performance changes over time
- **Parameter optimisation** — sweep MA window combinations and visualise results as a Sharpe heatmap
- **Return distribution** — histogram of daily strategy returns
- **Drawdown chart** — visualise the worst peak-to-trough periods
- **Trade log** — every entry and exit with price, return, and equity
- **Ticker comparison tab** — compare all selected assets on one chart with a metrics table

---

## Project Structure

quant-research-lab/  
├── app/  
│ └── quant_dashboard.py # Streamlit dashboard (entry point)  
├── src/  
│ ├── data/  
│ │ └── market_data.py # Market data loading and caching  
│ ├── strategies/  
│ │ └── signals.py # Strategy signal generation  
│ ├── backtest/  
│ │ ├── engine.py # Backtest execution engine  
│ │ └── optimiser.py # Parameter sweep and optimisation  
│ └── risk/  
│ └── metrics.py # Risk and performance metrics  
├── tests/  
│ └── test_backtest.py # Unit tests  
├── requirements.txt  
└── README.md  

  
---

## Strategies

### Moving Average Crossover
Generates a long signal when a short-period moving average crosses above
a long-period moving average. Parameters (short window, long window) are
fully configurable via the sidebar.

### Mean Reversion (Z-score)
Enters a long position when the asset's z-score falls below a negative
entry threshold, indicating it is statistically cheap relative to its
recent history. Exits when the z-score reverts toward zero.

---

## Risk Metrics

| Metric | Description |
|---|---|
| Total Return | Overall return over the full backtest period |
| Annualised Return | Geometric average return per year |
| Volatility | Annualised standard deviation of daily returns |
| Sharpe Ratio | Return per unit of risk (annualised) |
| Max Drawdown | Worst peak-to-trough decline |
| Win Rate | Proportion of trading days with positive return |
| Alpha | Daily excess return vs SPY benchmark |
| Beta | Sensitivity of strategy returns to SPY |

---

## Backtesting Assumptions

- Positions are entered on the day **after** a signal is generated (no look-ahead bias)
- Transaction costs modelled as fees + slippage in basis points, applied on every position change
- All strategies are long-only (no short selling)
- Initial capital is configurable (default £10,000)
- Data sourced from Yahoo Finance via `yfinance`

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| pandas / numpy | Data processing and numerical computation |
| yfinance | Historical market data |
| Streamlit | Interactive dashboard |
| Plotly | Charts and visualisations |
| pytest | Unit testing |

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/quant-research-lab.git
cd quant-research-lab

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\Activate.ps1       # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app/quant_dashboard.py
```

---

## Run Tests

```bash
PYTHONPATH=. pytest
```

---

## Potential Extensions

- [ ] Event-driven backtesting engine for more realistic execution modelling
- [ ] Short-selling and market-neutral strategies
- [ ] Monte Carlo simulation for return distribution forecasting
- [ ] Portfolio-level position sizing and rebalancing
- [ ] Live data feed integration
- [ ] Multi-factor signal combination
- [ ] Walk-forward optimisation to reduce overfitting

---

## Author

**Mohammed Ihthisham Neelam Kadavil** (lostithi)  
MSc Data Science— Heriot-Watt University  
[LinkedIn](www.linkedin.com/in/mohammed-ihthisham-neelam-kadavil) · [GitHub](https://github.com/lostithi)

---

## Disclaimer

This project is for educational and portfolio purposes only.
Nothing in this repository constitutes financial advice.
Past strategy performance does not guarantee future results.
