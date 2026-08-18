import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

# ============================================
# 1. PROJECT SETTINGS
# ============================================

stocks = ["AAPL", "MSFT", "GOOGL", "AMZN"]

start_date = "2025-01-01"
end_date = "2026-01-01"


# ============================================
# 2. DOWNLOAD STOCK DATA
# ============================================

print("Downloading stock market data...")

all_data = {}

for ticker in stocks:
    print(f"Downloading {ticker}...")

    data = yf.download(
        ticker, start=start_date, end=end_date, auto_adjust=True, progress=False
    )

    # Convert MultiIndex columns if returned by yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    all_data[ticker] = data


print("\nData downloaded successfully!")


# ============================================
# 3. ANALYZE EACH STOCK
# ============================================

summary = []
price_data = {}
return_data = {}

for ticker in stocks:
    data = all_data[ticker].copy()

    # Remove missing values
    data = data.dropna()

    # ----------------------------------------
    # Daily Return
    # ----------------------------------------

    data["Daily Return"] = data["Close"].pct_change()

    # ----------------------------------------
    # Moving Averages
    # ----------------------------------------

    data["20-Day MA"] = data["Close"].rolling(window=20).mean()
    data["50-Day MA"] = data["Close"].rolling(window=50).mean()

    # ----------------------------------------
    # Total Return
    # ----------------------------------------

    first_price = data["Close"].iloc[0]
    last_price = data["Close"].iloc[-1]

    total_return = ((last_price - first_price) / first_price) * 100

    # ----------------------------------------
    # Average Daily Return
    # ----------------------------------------

    average_daily_return = data["Daily Return"].mean() * 100

    # ----------------------------------------
    # Annualized Volatility
    # ----------------------------------------

    volatility = data["Daily Return"].std() * np.sqrt(252) * 100

    # ----------------------------------------
    # Highest and Lowest Price
    # ----------------------------------------

    highest_price = data["Close"].max()
    lowest_price = data["Close"].min()

    # ----------------------------------------
    # Best and Worst Day
    # ----------------------------------------

    best_day = data["Daily Return"].max() * 100
    worst_day = data["Daily Return"].min() * 100

    # ----------------------------------------
    # Maximum Drawdown
    # ----------------------------------------

    cumulative_max = data["Close"].cummax()

    drawdown = (data["Close"] - cumulative_max) / cumulative_max

    maximum_drawdown = drawdown.min() * 100

    # ----------------------------------------
    # Store Results
    # ----------------------------------------

    summary.append(
        {
            "Stock": ticker,
            "Starting Price": round(first_price, 2),
            "Ending Price": round(last_price, 2),
            "Total Return (%)": round(total_return, 2),
            "Average Daily Return (%)": round(average_daily_return, 4),
            "Annualized Volatility (%)": round(volatility, 2),
            "Highest Price": round(highest_price, 2),
            "Lowest Price": round(lowest_price, 2),
            "Best Day (%)": round(best_day, 2),
            "Worst Day (%)": round(worst_day, 2),
            "Maximum Drawdown (%)": round(maximum_drawdown, 2),
        }
    )

    price_data[ticker] = data["Close"]
    return_data[ticker] = data["Daily Return"]


# ============================================
# 4. CREATE SUMMARY TABLE
# ============================================

summary_df = pd.DataFrame(summary)

print("\n")
print("=" * 80)
print("STOCK PERFORMANCE SUMMARY")
print("=" * 80)

print(summary_df.to_string(index=False))


# ============================================
# 5. COMPARE RETURNS
# ============================================

returns_df = pd.DataFrame(return_data)

returns_df = returns_df.dropna()

cumulative_returns = ((1 + returns_df).cumprod() - 1) * 100

final_cumulative_returns = cumulative_returns.iloc[-1]

print("\n")
print("=" * 80)
print("CUMULATIVE RETURNS")
print("=" * 80)

for ticker in stocks:
    print(f"{ticker}: {final_cumulative_returns[ticker]:.2f}%")


# ============================================
# 6. FIND BEST PERFORMING STOCK
# ============================================

best_stock = summary_df.loc[summary_df["Total Return (%)"].idxmax()]

most_volatile_stock = summary_df.loc[summary_df["Annualized Volatility (%)"].idxmax()]

least_volatile_stock = summary_df.loc[summary_df["Annualized Volatility (%)"].idxmin()]

print("\n")
print("=" * 80)
print("KEY FINDINGS")
print("=" * 80)

print(
    f"Best performing stock: {best_stock['Stock']} ({best_stock['Total Return (%)']}%)"
)

print(
    f"Most volatile stock: "
    f"{most_volatile_stock['Stock']} "
    f"({most_volatile_stock['Annualized Volatility (%)']}%)"
)

print(
    f"Least volatile stock: "
    f"{least_volatile_stock['Stock']} "
    f"({least_volatile_stock['Annualized Volatility (%)']}%)"
)


# ============================================
# 7. CORRELATION ANALYSIS
# ============================================

correlation_matrix = returns_df.corr()

print("\n")
print("=" * 80)
print("STOCK RETURN CORRELATION")
print("=" * 80)

print(correlation_matrix.round(3))


# ============================================
# 8. SAVE DATA TO CSV
# ============================================

summary_df.to_csv("stock_summary.csv", index=False)

returns_df.to_csv("daily_returns.csv")

pd.DataFrame(price_data).to_csv("stock_prices.csv")

print("\nCSV files created:")
print("- stock_summary.csv")
print("- daily_returns.csv")
print("- stock_prices.csv")


# ============================================
# 9. EXPORT EVERYTHING TO EXCEL
# ============================================

print("\nCreating Excel report...")

with pd.ExcelWriter("stock_analysis.xlsx", engine="openpyxl") as writer:
    # Summary
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

    # Daily returns
    returns_df.to_excel(writer, sheet_name="Daily Returns")

    # Prices
    pd.DataFrame(price_data).to_excel(writer, sheet_name="Stock Prices")

    # Correlation
    correlation_matrix.to_excel(writer, sheet_name="Correlation")

    # Cumulative returns
    cumulative_returns.to_excel(writer, sheet_name="Cumulative Returns")


print("Excel report created: stock_analysis.xlsx")


# ============================================
# 10. FINAL MESSAGE
# ============================================

print("\n")
print("=" * 80)
print("PROJECT COMPLETED SUCCESSFULLY")
print("=" * 80)

print("\nFiles generated:")

print("1. stock_summary.csv")
print("2. daily_returns.csv")
print("3. stock_prices.csv")
print("4. stock_analysis.xlsx")

print("\nYou can now analyze the results using Excel.")


# ============================================
# 11. CREATE VISUALIZATIONS
# ============================================

# Stock price comparison
plt.figure(figsize=(12, 6))

for ticker in stocks:
    plt.plot(price_data[ticker], label=ticker)

plt.title("Stock Price Comparison")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("stock_price_comparison.png", dpi=300)

plt.close()


# Cumulative return comparison
plt.figure(figsize=(12, 6))

for ticker in stocks:
    plt.plot(cumulative_returns[ticker], label=ticker)

plt.title("Cumulative Stock Returns")
plt.xlabel("Date")
plt.ylabel("Return (%)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("cumulative_returns.png", dpi=300)

plt.close()


# Volatility comparison
plt.figure(figsize=(10, 6))

plt.bar(summary_df["Stock"], summary_df["Annualized Volatility (%)"])

plt.title("Annualized Volatility Comparison")
plt.xlabel("Stock")
plt.ylabel("Volatility (%)")
plt.grid(axis="y")

plt.tight_layout()
plt.savefig("volatility_comparison.png", dpi=300)

plt.close()


print("Charts created:")
print("- stock_price_comparison.png")
print("- cumulative_returns.png")
print("- volatility_comparison.png")
