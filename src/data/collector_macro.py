import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from src.config import MACRO_SYMBOLS

logger = logging.getLogger(__name__)

class MacroDataCollector:
    """Collects macro, geopolitical, and financial market stress indicators automatically."""

    def __init__(self):
        self.symbols = MACRO_SYMBOLS

    def fetch_macro_indicators(self, period="6mo") -> dict:
        """
        Fetches key macro indicators:
        - VIX: Market fear index
        - S&P 500 & KOSPI: Benchmark index prices & moving averages
        - US 10Y Yield: Risk-free rate trend
        - USDKRW: FX shock indicator
        - WTI Oil: Commodity/Inflation shock indicator
        """
        results = {}
        for name, ticker in self.symbols.items():
            try:
                data = yf.Ticker(ticker).history(period=period)
                if not data.empty:
                    current_price = float(data["Close"].iloc[-1])
                    prev_1d = float(data["Close"].iloc[-2]) if len(data) > 1 else current_price
                    prev_5d = float(data["Close"].iloc[-5]) if len(data) >= 5 else current_price
                    prev_20d = float(data["Close"].iloc[-20]) if len(data) >= 20 else current_price

                    chg_1d_pct = ((current_price - prev_1d) / prev_1d) * 100
                    chg_5d_pct = ((current_price - prev_5d) / prev_5d) * 100
                    chg_20d_pct = ((current_price - prev_20d) / prev_20d) * 100

                    # 20-day, 50-day, 200-day moving averages if available
                    sma_20 = float(data["Close"].rolling(20).mean().iloc[-1]) if len(data) >= 20 else current_price
                    sma_50 = float(data["Close"].rolling(50).mean().iloc[-1]) if len(data) >= 50 else current_price
                    sma_200 = float(data["Close"].rolling(200).mean().iloc[-1]) if len(data) >= 200 else current_price

                    results[name] = {
                        "ticker": ticker,
                        "current": round(current_price, 2),
                        "chg_1d_pct": round(chg_1d_pct, 2),
                        "chg_5d_pct": round(chg_5d_pct, 2),
                        "chg_20d_pct": round(chg_20d_pct, 2),
                        "sma_20": round(sma_20, 2),
                        "sma_50": round(sma_50, 2),
                        "sma_200": round(sma_200, 2),
                        "history": data["Close"]
                    }
                else:
                    logger.warning(f"No data returned for macro symbol {ticker}")
            except Exception as e:
                logger.error(f"Error fetching macro ticker {ticker}: {e}")
        
        return results

if __name__ == "__main__":
    collector = MacroDataCollector()
    macro = collector.fetch_macro_indicators(period="3mo")
    for k, v in macro.items():
        print(f"[{k}] Current: {v['current']} | 1D: {v['chg_1d_pct']}% | 5D: {v['chg_5d_pct']}%")
