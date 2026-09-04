import logging

logger = logging.getLogger(__name__)

class Gate2ScreeningEngine:
    """
    Gate 2: Dual-Horizon Screening & Factor Scoring Engine.
    Calculates Short-Term Tactical Score and Long-Term Strategic Score for candidate stocks.
    """

    def score_short_term(self, stock: dict) -> dict:
        """
        Evaluates 1-day to 2-week momentum & flow potential.
        Score range: 0 ~ 100
        """
        score = 0
        factors = []

        vol_ratio = stock.get("vol_ratio", 1.0)
        rsi = stock.get("rsi_14", 50.0)
        bandwidth = stock.get("bb_bandwidth", 0.1)
        dual_buying = stock.get("dual_buying", False)
        foreign_flow = stock.get("foreign_net_5d", 0)
        inst_flow = stock.get("inst_net_5d", 0)

        # 1. Volume Spike (Max 30)
        if vol_ratio >= 2.5:
            score += 30
            factors.append(f"거래대금 폭증 (20일 평균 대비 {vol_ratio}배)")
        elif vol_ratio >= 1.8:
            score += 20
            factors.append(f"거래량 유입 활발 ({vol_ratio}배)")
        elif vol_ratio >= 1.2:
            score += 10

        # 2. Institutional / Foreigner Flow (Max 30)
        if dual_buying:
            score += 30
            factors.append("외국인+기관 5일 연속 쌍끌이 순매수 유입")
        elif foreign_flow > 0 or inst_flow > 0:
            score += 15
            factors.append("스마트 머니(외인 또는 기관) 순매수 유입")
        elif stock.get("market") == "US_SP500":
            # For US stocks without dual flow data, reward relative volume strength
            if vol_ratio >= 1.5:
                score += 20
                factors.append("미국 대형주 기관급 유동성 유입 포착")

        # 3. Volatility Compression / Squeeze (Max 20)
        if bandwidth < 0.08:
            score += 20
            factors.append("볼린저 밴드 초강력 수축(Squeeze) 후 변동성 분출 직전")
        elif bandwidth < 0.15:
            score += 10

        # 4. RSI Momentum Zone (Max 20)
        if 50.0 <= rsi <= 68.0:
            score += 20
            factors.append(f"RSI 최적 모멘텀 상승 구간 (RSI: {rsi})")
        elif 40.0 <= rsi < 50.0:
            score += 10
        elif rsi > 75.0:
            score -= 10
            factors.append(f"단기 과매수 과열 경계 (RSI: {rsi})")

        qualified = (score >= 60)

        return {
            "short_term_score": score,
            "qualified": qualified,
            "key_factors": factors
        }

    def score_long_term(self, stock: dict) -> dict:
        """
        Evaluates 3-month to 1-year fundamental quality, valuation, and growth.
        Score range: 0 ~ 100
        """
        score = 0
        factors = []

        roe = stock.get("roe")
        forward_pe = stock.get("forward_pe")
        pbr = stock.get("price_to_book")
        current_price = stock.get("current_price", 0)
        sma_200 = stock.get("sma_200", 0)
        sma_50 = stock.get("sma_50", 0)

        # 1. Quality Factor (ROE, Margins) (Max 30)
        if roe is not None:
            if roe >= 0.18:
                score += 30
                factors.append(f"초우량 수익성 (ROE {round(roe*100, 1)}%)")
            elif roe >= 0.10:
                score += 20
                factors.append(f"양호한 수익성 (ROE {round(roe*100, 1)}%)")
            elif roe < 0:
                score -= 15
                factors.append("적자 기업 페널티")
        else:
            score += 15  # Neutral if not reported

        # 2. Valuation Factor (PE / PB) (Max 25)
        if forward_pe is not None and forward_pe > 0:
            if forward_pe <= 15.0:
                score += 25
                factors.append(f"매력적 저평가 (Forward PER {round(forward_pe, 1)}배)")
            elif forward_pe <= 28.0:
                score += 15
                factors.append(f"적정 밸류에이션 (Forward PER {round(forward_pe, 1)}배)")
            elif forward_pe > 50.0:
                score += 5
                factors.append(f"고성장 프리미엄 반영 (PER {round(forward_pe, 1)}배)")
        else:
            score += 10

        # 3. Long-term Trend Support (Max 25)
        if current_price > sma_200 and sma_50 >= sma_200:
            score += 25
            factors.append("200일 장기 이평선 상회 및 50일선 정배열 우상향")
        elif current_price > sma_200:
            score += 15
            factors.append("200일 장기 추세선 위 지지 확인")
        else:
            score -= 10
            factors.append("200일선 하회 - 역추세 조정 구간")

        # 4. Market Cap Stability (Max 20)
        market_cap = stock.get("market_cap", 0)
        if market_cap > 50_000_000_000_000 or market_cap > 50_000_000_000:  # Large Cap
            score += 20
            factors.append("시장 지배적 대형 우량주 안정성")
        else:
            score += 10

        qualified = (score >= 65)

        return {
            "long_term_score": score,
            "qualified": qualified,
            "key_factors": factors
        }
