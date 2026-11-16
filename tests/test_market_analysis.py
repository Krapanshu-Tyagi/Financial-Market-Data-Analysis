import numpy as np
import pandas as pd
import pytest

from market_analysis import analyze_prices, download_prices


@pytest.fixture
def sample_prices():
    dates = pd.date_range("2025-01-01", periods=4, freq="B")
    return pd.DataFrame(
        {"AAA": [100.0, 110.0, 105.0, 120.0],
         "BBB": [50.0, 52.0, 51.0, 53.0]},
        index=dates,
    )


def test_analyze_prices_calculates_returns_and_risk(sample_prices):
    result = analyze_prices(sample_prices)
    summary = result["summary"].set_index("Ticker")
    assert summary.loc["AAA", "Total Return (%)"] == pytest.approx(20.0)
    assert summary.loc["AAA", "Maximum Drawdown (%)"] == pytest.approx(-100 * 5 / 110)
    assert result["daily_returns"].loc[:, "AAA"].iloc[1] == pytest.approx(0.10)
    assert result["correlation"].shape == (2, 2)


def test_analyze_prices_rejects_empty_input():
    with pytest.raises(ValueError, match="empty"):
        analyze_prices(pd.DataFrame())


def test_analyze_prices_rejects_non_positive_prices():
    prices = pd.DataFrame({"AAA": [10.0, 0.0, 12.0]})
    with pytest.raises(ValueError, match="positive"):
        analyze_prices(prices)


def test_download_prices_rejects_invalid_date_range():
    with pytest.raises(ValueError, match="earlier"):
        download_prices(["AAPL"], "2025-02-01", "2025-01-01")
