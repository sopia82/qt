import logging

logger = logging.getLogger(__name__)

class Gate1MarketRegimeEngine:
    """
    Gate 1: Market Trend & Regime Filter.
    Determines whether S&P 500 and KOSPI are in Bull, Bear, or Sideways regimes.
    """

    def evaluate(self, macro_data: dict) -> dict:
        results = {}

        # 1. US Market Regime (S&P 500)
        sp500 = macro_data.get("SP500", {})
        if sp500:
            price = sp500.get("current", 0)
            sma_50 = sp500.get("sma_50", 0)
            sma_200 = sp500.get("sma_200", 0)

            if price > sma_200 and sma_50 >= sma_200:
                us_regime = "BULL_UPTREND"
                us_desc = "S&P 500 200일선 상회 및 50일선 정배열 (강세장 유지)"
            elif price > sma_200 and sma_50 < sma_200:
                us_regime = "NEUTRAL_CONSOLIDATION"
                us_desc = "S&P 500 200일선 지지 중이나 50일선 혼조 (횡보/조정)"
            else:
                us_regime = "BEAR_DOWNTREND"
                us_desc = "S&P 500 200일선 하회 (약세장 경계 - 롱 진입 축소)"

            results["US_SP500"] = {
                "regime": us_regime,
                "price": price,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "desc": us_desc
            }

        # 2. KR Market Regime (KOSPI)
        kospi = macro_data.get("KOSPI", {})
        if kospi:
            price = kospi.get("current", 0)
            sma_50 = kospi.get("sma_50", 0)
            sma_200 = kospi.get("sma_200", 0)

            if price > sma_200:
                kr_regime = "BULL_UPTREND"
                kr_desc = "KOSPI 200일선 상회 (중장기 상승 추세)"
            elif price > sma_50:
                kr_regime = "NEUTRAL_CONSOLIDATION"
                kr_desc = "KOSPI 50일선 지지 횡보 국면"
            else:
                kr_regime = "BEAR_DOWNTREND"
                kr_desc = "KOSPI 주요 이평선 하회 (단기 수급 집중주만 선별 대응)"

            results["KR_KOSPI"] = {
                "regime": kr_regime,
                "price": price,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "desc": kr_desc
            }

        return results
