import yfinance as yf
import pandas as pd
import numpy as np
import logging
from src.config import SP500_UNIVERSE
from src.engine.math_models import (
    calculate_hurst_exponent,
    calculate_ou_mean_reversion,
    calculate_parkinson_volatility,
    calculate_amihud_liquidity,
    calculate_parametric_var
)

logger = logging.getLogger(__name__)

def calculate_advanced_quant_metrics(df: pd.DataFrame) -> dict:
    """Calculates advanced institutional quantitative finance metrics."""
    if len(df) < 30:
        return {}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # 1. Classical Moving Averages
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1] if len(df) >= 50 else sma_20
    sma_200 = close.rolling(200).mean().iloc[-1] if len(df) >= 200 else sma_50

    # 2. Volume Spike & Amihud Illiquidity
    avg_vol_20 = volume.rolling(20).mean().iloc[-1]
    last_vol = volume.iloc[-1]
    vol_ratio = (last_vol / avg_vol_20) if avg_vol_20 > 0 else 1.0
    amihud = calculate_amihud_liquidity(close, volume)

    # 3. Bollinger Bandwidth
    std_20 = close.rolling(20).std().iloc[-1]
    bb_bandwidth = (4 * std_20) / sma_20 if sma_20 > 0 else 0

    # 4. RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_14 = 100 - (100 / (1 + rs))
    last_rsi = float(rsi_14.iloc[-1]) if not np.isnan(rsi_14.iloc[-1]) else 50.0

    # 5. ATR (14)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_14 = tr.rolling(14).mean().iloc[-1]

    # 6. VWAP Approximation
    vwap = (close * volume).sum() / volume.sum() if volume.sum() > 0 else close.iloc[-1]

    # 7. Mathematical Quant Models
    hurst = calculate_hurst_exponent(close)
    ou = calculate_ou_mean_reversion(close)
    parkinson_vol = calculate_parkinson_volatility(high, low)
    var_metrics = calculate_parametric_var(close)

    # 8. Carhart 12M - 1M Momentum (Skip last month to avoid short-term reversal noise)
    if len(close) >= 252:
        carhart_mom = (close.iloc[-21] - close.iloc[-252]) / close.iloc[-252]
    elif len(close) >= 60:
        carhart_mom = (close.iloc[-10] - close.iloc[-60]) / close.iloc[-60]
    else:
        carhart_mom = 0.0

    current_price = float(close.iloc[-1])

    return {
        "current_price": round(current_price, 2),
        "sma_20": round(float(sma_20), 2),
        "sma_50": round(float(sma_50), 2),
        "sma_200": round(float(sma_200), 2),
        "vol_ratio": round(float(vol_ratio), 2),
        "amihud_illiq": amihud,
        "bb_bandwidth": round(float(bb_bandwidth), 4),
        "rsi_14": round(last_rsi, 2),
        "atr_14": round(float(atr_14), 2),
        "vwap": round(float(vwap), 2),
        # Advanced Quant Parameters
        "hurst_exponent": hurst,
        "ou_half_life": ou["half_life"],
        "ou_z_score": ou["z_score"],
        "ou_stationary": ou["stationary"],
        "parkinson_vol": parkinson_vol,
        "var_99_pct": var_metrics["var_99_pct"],
        "cvar_99_pct": var_metrics["cvar_99_pct"],
        "carhart_mom": round(float(carhart_mom * 100.0), 2)
    }

class USStockCollector:
    """Collects US S&P 500 stocks with rigorous mathematical and fundamental metrics."""

    def __init__(self, tickers=None):
        self.tickers = tickers or SP500_UNIVERSE

    def fetch_stock_data(self, ticker: str, period="2y") -> dict:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty or len(hist) < 30:
                return {}

            tech = calculate_advanced_quant_metrics(hist)
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
                "operating_margins": info.get("operatingMargins", None),
                "revenue_growth": info.get("revenueGrowth", None),
                "earnings_growth": info.get("earningsGrowth", None)
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
