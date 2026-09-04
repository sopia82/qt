import logging

logger = logging.getLogger(__name__)

class Gate0MacroEventEngine:
    """
    Gate 0: Evaluates Political, Geopolitical, and Macroeconomic Stress.
    Criteria:
    - VIX Spike (> 28 -> Panic, > 22 -> Caution)
    - US 10Y Yield Weekly Spike (+15bps -> Tech pressure)
    - USD/KRW Weekly Shock (+2% -> Foreign capital flight)
    - News Sentiment Collapse (< -0.40) or Event Blackout (FOMC / CPI)
    """

    def evaluate(self, macro_data: dict, news_data: dict) -> dict:
        vix_info = macro_data.get("VIX", {})
        us10y_info = macro_data.get("US_10Y", {})
        usdkrw_info = macro_data.get("USDKRW", {})

        vix_val = vix_info.get("current", 18.0)
        us10y_5d = us10y_info.get("chg_5d_pct", 0.0)
        usdkrw_5d = usdkrw_info.get("chg_5d_pct", 0.0)
        sentiment = news_data.get("sentiment_score", 0.0)
        blackout = news_data.get("blackout_alert", False)

        status = "NORMAL"
        reasons = []

        # 1. Panic / Blackout Condition
        if blackout:
            status = "BLACKOUT"
            reasons.append("주요 경제지표(FOMC/CPI) 발표 일정 감지 - 단기 신규 진입 일시 동결")

        if vix_val >= 28.0:
            status = "CRITICAL_RISK_OFF"
            reasons.append(f"VIX 공포지수 급등({vix_val} >= 28) - 현금 비중 80% 이상 확보 권장")
        elif vix_val >= 22.0:
            if status == "NORMAL":
                status = "CAUTION"
            reasons.append(f"VIX 변동성 경계 구간({vix_val} >= 22) - 보수적 포지션 운영")

        # 2. Yield shock
        if us10y_5d >= 4.0:
            reasons.append(f"미국 10년물 국채금리 단기 급등(5D +{us10y_5d}%) - 고PER 기술주 밸류에이션 부담")

        # 3. Currency shock
        if usdkrw_5d >= 2.0:
            reasons.append(f"원/달러 환율 단기 급등(5D +{usdkrw_5d}%) - 한국 KOSPI 외국인 매도세 유의")

        # 4. News sentiment
        if sentiment <= -0.4:
            if status == "NORMAL":
                status = "CAUTION"
            reasons.append(f"정치/경제 뉴스 감성 악화(Score: {sentiment}) - 무역/전쟁/규제 이슈 주의")

        allow_trading = (status in ["NORMAL", "CAUTION"])
        max_exposure = 1.0
        if status == "CAUTION":
            max_exposure = 0.6  # Reduce exposure to 60%
        elif status in ["BLACKOUT", "CRITICAL_RISK_OFF"]:
            max_exposure = 0.2  # Max 20% or 0%

        return {
            "status": status,
            "allow_new_entries": allow_trading,
            "max_portfolio_exposure": max_exposure,
            "reasons": reasons if reasons else ["거시경제 및 정치 리스크 안정 국면"],
            "vix": vix_val,
            "sentiment_score": sentiment
        }
