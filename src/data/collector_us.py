import yfinance as yf
import pandas as pd
import numpy as np
import logging
from src.config import SP500_UNIVERSE

logger = logging.getLogger(__name__)

def calculate_technical_indicators(df: pd.DataFrame) -> dict:
    """Calculates technical indicators from OHLCV dataframe."""
    if len(df) < 20:
        return {}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Moving Averages
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1] if len(df) >= 50 else sma_20
    sma_200 = close.rolling(200).mean().iloc[-1] if len(df) >= 200 else sma_50

    # Volume spike ratio
    avg_vol_20 = volume.rolling(20).mean().iloc[-1]
    last_vol = volume.iloc[-1]
    vol_ratio = (last_vol / avg_vol_20) if avg_vol_20 > 0 else 1.0

    # Bollinger Bands (20, 2)
    std_20 = close.rolling(20).std().iloc[-1]
    bb_upper = sma_20 + (2 * std_20)
    bb_lower = sma_20 - (2 * std_20)
    bb_bandwidth = (bb_upper - bb_lower) / sma_20 if sma_20 > 0 else 0

    # RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_14 = 100 - (100 / (1 + rs))
    last_rsi = float(rsi_14.iloc[-1]) if not np.isnan(rsi_14.iloc[-1]) else 50.0

    # ATR (14) for volatility & stop loss
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_14 = tr.rolling(14).mean().iloc[-1]

    # VWAP approximation on recent daily bars
    vwap = (close * volume).sum() / volume.sum() if volume.sum() > 0 else close.iloc[-1]

    current_price = float(close.iloc[-1])

    return {
        "current_price": round(current_price, 2),
        "sma_20": round(float(sma_20), 2),
        "sma_50": round(float(sma_50), 2),
        "sma_200": round(float(sma_200), 2),
        "vol_ratio": round(float(vol_ratio), 2),
        "bb_upper": round(float(bb_upper), 2),
        "bb_lower": round(float(bb_lower), 2),
        "bb_bandwidth": round(float(bb_bandwidth), 4),
        "rsi_14": round(last_rsi, 2),
        "atr_14": round(float(atr_14), 2),
        "vwap": round(float(vwap), 2)
    }

class USStockCollector:
    """Collects US S&P 500 stocks price, volume, technical and fundamental metrics."""

    def __init__(self, tickers=None):
        self.tickers = tickers or SP500_UNIVERSE

    def fetch_stock_data(self, ticker: str, period="1y") -> dict:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty or len(hist) < 20:
                return {}

            tech = calculate_technical_indicators(hist)
            if not tech:
                return {}

            info = stock.info or {}
            fundamentals = {
                "forward_pe": info.get("forwardPE", None),
                "trailing_pe": info.get("trailingPE", None),
                "price_to_book": info.get("priceToBook", None),
                "roe": info.get("returnOnEquity", None),
                "market_cap": info.get("marketCap", 0),
                "profit_margins": info.get("profitMargins", None),
                "revenue_growth": info.get("revenueGrowth", None)
            }

            return {
                "ticker": ticker,
                "market": "US_SP500",
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "Unknown"),
                **tech,
                **fundamentals
            }
        except Exception as e:
            logger.error(f"Error fetching US stock {ticker}: {e}")
            return {}

    def fetch_all(self, max_count=None) -> list:
        results = []
        target_tickers = self.tickers[:max_count] if max_count else self.tickers
        for ticker in target_tickers:
            data = self.fetch_stock_data(ticker)
            if data:
                results.append(data)
        return results

if __name__ == "__main__":
    collector = USStockCollector()
    sample = collector.fetch_stock_data("AAPL")
    print("AAPL Sample Data:", sample)
