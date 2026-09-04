import logging

logger = logging.getLogger(__name__)

class Gate2ScreeningEngine:
    """
    Institutional Mathematical Quant Factor Engine:
    - Regime classification via Hurst Exponent (H)
    - Statistical Arbitrage / Mean Reversion via Ornstein-Uhlenbeck (O-U)
    - Fama-French Quality & Value Composite Factors
    - Carhart 12M-1M Cross-Sectional Momentum
    """

    def score_short_term(self, stock: dict) -> dict:
        """
        Calculates Tactical Short-Term Statistical Alpha Score (0 ~ 100).
        Evaluates whether price dynamics exhibit mathematically proven statistical edges.
        """
        score = 0
        factors = []

        h = stock.get("hurst_exponent", 0.50)
        z_ou = stock.get("ou_z_score", 0.0)
        tau = stock.get("ou_half_life", 20.0)
        vol_ratio = stock.get("vol_ratio", 1.0)
        dual_buying = stock.get("dual_buying", False)
        bandwidth = stock.get("bb_bandwidth", 0.1)
        amihud = stock.get("amihud_illiq", 0.1)
        rsi = stock.get("rsi_14", 50.0)

        # 1. Regime Identification & Statistical Edge (Max 35)
        if h > 0.58:
            # Persistent Trend Regime
            score += 25
            factors.append(f"허스트 지수 H={h} (강한 추세 지속성 국면 - 모멘텀 알파 유효)")
            if vol_ratio >= 2.0:
                score += 10
                factors.append(f"거래량 폭증({vol_ratio}배) 동반 추세 돌파 가속")
        elif h < 0.42 and z_ou <= -1.5:
            # Anti-persistent Mean Reversion Regime
            score += 30
            factors.append(f"허스트 H={h} & O-U 통계적 저평가 (Z={z_ou}σ, 반감기 {tau}일)")
            if tau <= 12.0:
                score += 5
                factors.append("빠른 평균회귀 속도(Half-life ≤ 12D)")
        elif 0.46 <= h <= 0.54:
            # Random Walk / Zero Edge
            score -= 10
            factors.append(f"허스트 H={h} (랜덤워크 국면 - 통계적 우위 부재)")

        # 2. Institutional Flow & Microstructure (Max 35)
        if dual_buying:
            score += 30
            factors.append("기관·외인 동시 순유입 (스마트 머니 쌍끌이 누적)")
        elif stock.get("market") == "US_SP500" and vol_ratio >= 1.8:
            score += 25
            factors.append(f"미국 기관급 거래대금 집중 (평균 대비 {vol_ratio}배)")
        elif stock.get("foreign_net_5d", 0) > 0:
            score += 15
            factors.append("외국인 5일 누적 순매수 우위")

        # 3. Volatility Compression & Energy Buildup (Max 20)
        if bandwidth < 0.08:
            score += 20
            factors.append(f"볼린저 대역폭 초강력 수축({round(bandwidth*100, 1)}%) - 변동성 폭발 임계점")
        elif bandwidth < 0.14:
            score += 10

        # 4. Momentum Filter (Max 10)
        if 48.0 <= rsi <= 65.0:
            score += 10
            factors.append(f"RSI 최적 가속 구간 (RSI {rsi})")

        # Win probability estimation based on factor confluence
        empirical_win_prob = 0.50 + (score / 300.0)  # 50% ~ 78% range
        empirical_win_prob = min(max(empirical_win_prob, 0.45), 0.78)

        return {
            "short_term_score": max(score, 0),
            "qualified": score >= 50,
            "win_prob": round(empirical_win_prob, 3),
            "key_factors": factors,
            "quant_regime": "TRENDING" if h > 0.55 else ("MEAN_REVERTING" if h < 0.45 else "RANDOM_WALK")
        }

    def score_long_term(self, stock: dict) -> dict:
        """
        Calculates Strategic Long-Term Fama-French & Quality Composite Alpha Score (0 ~ 100).
        """
        score = 0
        factors = []

        roe = stock.get("roe")
        forward_pe = stock.get("forward_pe")
        pbr = stock.get("price_to_book")
        parkinson_vol = stock.get("parkinson_vol", 0.30)
        carhart_mom = stock.get("carhart_mom", 0.0)
        sma_200 = stock.get("sma_200", 0)
        price = stock.get("current_price", 0)

        # 1. Fama-French Quality Factor (ROE, Operating Margin) (Max 30)
        if roe is not None:
            if roe >= 0.20:
                score += 30
                factors.append(f"최상위 수익성 팩터 (ROE {round(roe*100, 1)}%)")
            elif roe >= 0.12:
                score += 20
                factors.append(f"안정적 수익성 팩터 (ROE {round(roe*100, 1)}%)")
            elif roe < 0:
                score -= 15
                factors.append("음(-)의 ROE 페널티")

        # 2. Value Factor (Earnings Yield E/P) (Max 25)
        if forward_pe is not None and forward_pe > 0:
            ey = (1.0 / forward_pe) * 100.0
            if ey >= 8.0:  # PER <= 12.5
                score += 25
                factors.append(f"깊은 저평가 밸류 (이익수익률 {round(ey, 1)}%, PER {round(forward_pe, 1)}배)")
            elif ey >= 4.5:  # PER <= 22
                score += 18
                factors.append(f"적정 밸류에이션 (이익수익률 {round(ey, 1)}%)")
            elif ey < 2.0:
                score += 5
                factors.append(f"고성장 프리미엄 반영 (PER {round(forward_pe, 1)}배)")

        # 3. Carhart 12M - 1M Cross-Sectional Momentum (Max 25)
        if carhart_mom >= 25.0:
            score += 25
            factors.append(f"강력한 카하트 중기 모멘텀 (+{carhart_mom}%)")
        elif carhart_mom >= 10.0:
            score += 15
            factors.append(f"양호한 카하트 모멘텀 (+{carhart_mom}%)")
        elif carhart_mom < -15.0:
            score -= 10
            factors.append(f"하락 역추세 모멘텀 ({carhart_mom}%)")

        # 4. Parkinson Low-Volatility Factor (Max 20)
        if parkinson_vol <= 0.22:
            score += 20
            factors.append(f"파킨슨 저변동성 우량주 (연환산 변동성 {round(parkinson_vol*100, 1)}%)")
        elif parkinson_vol <= 0.35:
            score += 12
        else:
            factors.append(f"고변동성 자산 (연환산 {round(parkinson_vol*100, 1)}%)")

        empirical_win_prob = 0.52 + (score / 350.0)
        empirical_win_prob = min(max(empirical_win_prob, 0.48), 0.80)

        return {
            "long_term_score": max(score, 0),
            "qualified": score >= 55,
            "win_prob": round(empirical_win_prob, 3),
            "key_factors": factors
        }
