"""Reusable stock-market analysis pipeline.

Prices are adjusted by yfinance (auto_adjust=True). Returns are historical
descriptive statistics, not forecasts or investment advice.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

TRADING_DAYS_PER_YEAR = 252


def download_prices(
    tickers: Iterable[str], start: str, end: str
) -> pd.DataFrame:
    """Download adjusted closing prices; fail clearly if any ticker has no data."""
    ticker_list = list(dict.fromkeys(t.strip().upper() for t in tickers if t.strip()))
    if not ticker_list:
        raise ValueError("Provide at least one ticker symbol.")
    if pd.Timestamp(start) >= pd.Timestamp(end):
        raise ValueError("Start date must be earlier than end date.")

    series: dict[str, pd.Series] = {}
    failures: list[str] = []
    for ticker in ticker_list:
        try:
            frame = yf.download(
                ticker, start=start, end=end, auto_adjust=True,
                progress=False, threads=False
            )
            if frame.empty:
                failures.append(ticker)
                continue
            close = frame["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            close = pd.to_numeric(close, errors="coerce").dropna()
            if close.empty:
                failures.append(ticker)
                continue
            series[ticker] = close.rename(ticker)
        except Exception as exc:
            failures.append(f"{ticker} ({type(exc).__name__})")

    if failures:
        raise RuntimeError(
            "No usable price data was returned for: " + ", ".join(failures)
            + ". Check ticker symbols, dates, and network access."
        )
    prices = pd.concat(series.values(), axis=1).sort_index()
    prices.index = pd.to_datetime(prices.index)
    return prices


def analyze_prices(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Calculate per-asset metrics and aligned return/correlation tables."""
    if prices.empty or prices.dropna(how="all").empty:
        raise ValueError("Price data is empty.")
    clean = prices.copy()
    clean = clean.apply(pd.to_numeric, errors="coerce").dropna(how="all")
    clean = clean.loc[:, clean.notna().any()]
    if (clean.dropna(how="all") <= 0).any().any():
        raise ValueError("Prices must be positive.")

    daily_returns = clean.pct_change(fill_method=None)
    rows = []
    for ticker in clean.columns:
        series = clean[ticker].dropna()
        returns = daily_returns[ticker].dropna()
        if len(series) < 2 or returns.empty:
            raise ValueError(f"Not enough observations to analyze {ticker}.")
        running_peak = series.cummax()
        drawdown = series / running_peak - 1
        rows.append({
            "Ticker": ticker,
            "Observations": int(len(series)),
            "Start Date": series.index[0].date().isoformat(),
            "End Date": series.index[-1].date().isoformat(),
            "Starting Price": float(series.iloc[0]),
            "Ending Price": float(series.iloc[-1]),
            "Total Return (%)": float((series.iloc[-1] / series.iloc[0] - 1) * 100),
            "Annualized Volatility (%)": float(returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100),
            "Maximum Drawdown (%)": float(drawdown.min() * 100),
            "Best Day (%)": float(returns.max() * 100),
            "Worst Day (%)": float(returns.min() * 100),
            "20-Day Moving Average": float(series.rolling(20).mean().iloc[-1]) if len(series) >= 20 else np.nan,
            "50-Day Moving Average": float(series.rolling(50).mean().iloc[-1]) if len(series) >= 50 else np.nan,
        })

    aligned_returns = daily_returns.dropna(how="all")
    cumulative_returns = ((1 + daily_returns.fillna(0)).cumprod() - 1) * 100
    correlation = aligned_returns.corr()
    return {
        "summary": pd.DataFrame(rows),
        "prices": clean,
        "daily_returns": daily_returns,
        "cumulative_returns": cumulative_returns,
        "correlation": correlation,
    }


def export_results(results: dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    """Write CSV, Excel and chart outputs to the selected directory."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results["summary"].to_csv(output / "stock_summary.csv", index=False)
    results["prices"].to_csv(output / "stock_prices.csv", index_label="Date")
    results["daily_returns"].to_csv(output / "daily_returns.csv", index_label="Date")

    with pd.ExcelWriter(output / "stock_analysis.xlsx", engine="openpyxl") as writer:
        for key, sheet in [
            ("summary", "Summary"), ("prices", "Stock Prices"),
            ("daily_returns", "Daily Returns"),
            ("cumulative_returns", "Cumulative Returns"),
            ("correlation", "Correlation"),
        ]:
            results[key].to_excel(writer, sheet_name=sheet, index=(key != "summary"))

    _save_line_chart(results["prices"], "Adjusted closing prices",
                     "Price", output / "stock_price_comparison.png")
    _save_line_chart(results["cumulative_returns"], "Cumulative returns",
                     "Return (%)", output / "cumulative_returns.png")
    summary = results["summary"].set_index("Ticker")
    ax = summary["Annualized Volatility (%)"].plot(kind="bar", figsize=(10, 6))
    ax.set(title="Annualized volatility", xlabel="Ticker", ylabel="Volatility (%)")
    ax.grid(axis="y", alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(output / "volatility_comparison.png", dpi=200)
    plt.close(ax.figure)


def _save_line_chart(
    frame: pd.DataFrame, title: str, ylabel: str, destination: Path
) -> None:
    ax = frame.plot(figsize=(12, 6))
    ax.set(title=title, xlabel="Date", ylabel=ylabel)
    ax.grid(alpha=0.3)
    ax.legend(title="Ticker")
    ax.figure.tight_layout()
    ax.figure.savefig(destination, dpi=200)
    plt.close(ax.figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare historical stock performance and risk.")
    parser.add_argument("--tickers", default="AAPL,MSFT,GOOGL,AMZN",
                        help="Comma-separated ticker symbols.")
    parser.add_argument("--start", default="2025-01-01", help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end", default="2026-01-01", help="End date (exclusive, YYYY-MM-DD).")
    parser.add_argument("--output-dir", default="outputs", help="Directory for generated reports.")
    args = parser.parse_args()

    tickers = [ticker.strip() for ticker in args.tickers.split(",") if ticker.strip()]
    prices = download_prices(tickers, args.start, args.end)
    results = analyze_prices(prices)
    export_results(results, args.output_dir)
    print(results["summary"].round(3).to_string(index=False))
    print(f"\nReports and charts saved to: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
