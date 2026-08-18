# Financial Market Data Analysis

A Python-based financial data analysis project that uses real historical stock market data to compare the performance and risk of major technology companies.

## Objective

The goal of this project is to analyze historical stock data and compare:

- Stock returns
- Daily returns
- Annualized volatility
- Maximum drawdown
- Moving averages
- Cumulative performance
- Correlation between stocks

## Stocks Analyzed

- Apple (AAPL)
- Microsoft (MSFT)
- Alphabet (GOOGL)
- Amazon (AMZN)

## Technologies Used

- Python
- Pandas
- NumPy
- yfinance
- Matplotlib
- OpenPyXL
- Excel

## Data Source

Historical stock market data was obtained using the Yahoo Finance API through the `yfinance` Python library.

## Analysis

The project calculates:

### Total Return

Measures the percentage change between the starting and ending stock prices.

### Daily Return

Measures the percentage change in price from one trading day to the next.

### Annualized Volatility

Measures the historical variability of daily stock returns.

### Maximum Drawdown

Measures the largest decline from a previous peak.

### Correlation

Measures how closely the daily returns of different stocks move together.

## Output

The project generates:

- `stock_summary.csv`
- `daily_returns.csv`
- `stock_prices.csv`
- `stock_analysis.xlsx`
- `stock_price_comparison.png`
- `cumulative_returns.png`
- `volatility_comparison.png`

## How to Run

Clone the repository and enter the project directory:

```bash
cd financial-data-project
```

