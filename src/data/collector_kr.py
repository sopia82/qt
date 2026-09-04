import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import logging
from src.config import KOSPI_UNIVERSE
from src.data.collector_us import calculate_technical_indicators

logger = logging.getLogger(__name__)

class KRStockCollector:
    """Collects KOSPI 100 stocks OHLCV, technicals, and Foreigner/Institutional investor flows."""

    def __init__(self, tickers=None):
        self.tickers = tickers or KOSPI_UNIVERSE

    def fetch_investor_flow(self, code: str) -> dict:
        """
        Fetches recent Foreigner & Institutional net buying from Naver Finance.
        Returns 5-day net buy sums (Foreigner, Institutional) in shares / approximate amounts.
        """
        url = f"https://finance.naver.com/item/frgn.naver?code={code}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code != 200:
                return {"foreign_net_5d": 0, "inst_net_5d": 0, "dual_buying": False}

            soup = BeautifulSoup(resp.text, "html.parser")
            tables = soup.find_all("table", {"class": "type2"})
            if len(tables) < 2:
                return {"foreign_net_5d": 0, "inst_net_5d": 0, "dual_buying": False}

            rows = tables[1].find_all("tr")
            foreign_sum = 0
            inst_sum = 0
            count = 0

            for r in rows:
                cols = r.find_all("td")
                if len(cols) >= 7:
                    inst_str = cols[5].text.strip().replace(",", "").replace("+", "")
                    frgn_str = cols[6].text.strip().replace(",", "").replace("+", "")
                    try:
                        inst_val = int(inst_str)
                        frgn_val = int(frgn_str)
                        inst_sum += inst_val
                        foreign_sum += frgn_val
                        count += 1
                        if count >= 5:  # Last 5 trading days
                            break
                    except ValueError:
                        continue

            dual_buying = (foreign_sum > 0 and inst_sum > 0)
            return {
                "foreign_net_5d": foreign_sum,
                "inst_net_5d": inst_sum,
                "dual_buying": dual_buying
            }
        except Exception as e:
            logger.debug(f"Investor flow fetch fallback for {code}: {e}")
            return {"foreign_net_5d": 0, "inst_net_5d": 0, "dual_buying": False}

    def fetch_stock_data(self, code: str, name: str, period="1y") -> dict:
        yf_ticker = f"{code}.KS"
        try:
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period=period)
            if hist.empty or len(hist) < 20:
                return {}

            tech = calculate_technical_indicators(hist)
            if not tech:
                return {}

            flow = self.fetch_investor_flow(code)

            info = stock.info or {}
            fundamentals = {
                "forward_pe": info.get("forwardPE", None),
                "trailing_pe": info.get("trailingPE", None),
                "price_to_book": info.get("priceToBook", None),
                "roe": info.get("returnOnEquity", None),
                "market_cap": info.get("marketCap", 0)
            }

            return {
                "ticker": code,
                "yf_ticker": yf_ticker,
                "market": "KR_KOSPI",
                "name": name,
                "sector": info.get("sector", "KOSPI"),
                **tech,
                **flow,
                **fundamentals
            }
        except Exception as e:
            logger.error(f"Error fetching KOSPI stock {code}: {e}")
            return {}

    def fetch_all(self, max_count=None) -> list:
        results = []
        target_list = self.tickers[:max_count] if max_count else self.tickers
        for code, name in target_list:
            data = self.fetch_stock_data(code, name)
            if data:
                results.append(data)
        return results

if __name__ == "__main__":
    collector = KRStockCollector()
    sample = collector.fetch_stock_data("005930", "삼성전자")
    print("Samsung Electronics Sample:", sample)
