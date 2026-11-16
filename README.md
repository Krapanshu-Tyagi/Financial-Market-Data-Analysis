# Financial Market Data Analysis

A reproducible Python pipeline for comparing historical stock performance and risk using adjusted market prices from Yahoo Finance via `yfinance`.

## What it measures

- **Total return:** change from the first to last adjusted close in the selected period.
- **Daily returns:** percentage change between consecutive adjusted closes.
- **Annualized volatility:** sample standard deviation of daily returns multiplied by `sqrt(252)`.
- **Maximum drawdown:** largest peak-to-trough decline in the adjusted closing-price series.
- **Moving averages:** 20- and 50-observation simple moving averages.
- **Correlation:** Pearson correlation between aligned daily returns.

These are historical descriptive statistics, not predictions or investment recommendations. The annualization assumes 252 trading sessions per year. Yahoo Finance data availability and adjustments may change over time.

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Default analysis (AAPL, MSFT, GOOGL, AMZN):

```bash
python stock_analysis.py
```

Choose your own tickers, dates, and output directory:

```bash
python stock_analysis.py --tickers AAPL,MSFT,NVDA --start 2024-01-01 --end 2025-01-01 --output-dir outputs
```

The end date is exclusive, following the `yfinance` convention. Generated files are saved to the output directory:

- `stock_summary.csv`
- `stock_prices.csv`
- `daily_returns.csv`
- `stock_analysis.xlsx` (summary, prices, returns, cumulative returns, and correlation sheets)
- `stock_price_comparison.png`
- `cumulative_returns.png`
- `volatility_comparison.png`

## Tests

The metric calculations are tested with deterministic local data; tests do not call Yahoo Finance.

```bash
python -m pytest -q
```

## Project structure

```
.
├── market_analysis.py
├── stock_analysis.py
├── tests/
│   └── test_market_analysis.py
├── requirements.txt
└── README.md
```
