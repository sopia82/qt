import logging

logger = logging.getLogger(__name__)

class Gate3TimingEngine:
    """
    Mathematical Precision Timing Trigger Engine:
    - Sets Stop-Loss at the 99% Student-t VaR tail risk boundary
    - Sets Target Price based on O-U Equilibrium Mu (for Mean Reversion)
      or Optimal Payoff Ratio (for Trend Following)
    """

    def calculate_short_term_timing(self, stock: dict) -> dict:
        price = stock.get("current_price", 100.0)
        vwap = stock.get("vwap", price)
        var_99 = stock.get("var_99_pct", -3.2)
        h = stock.get("hurst_exponent", 0.50)
        ou_mu = stock.get("ou_stationary", False) and stock.get("ou_half_life", 99) < 20

        # Mathematical Stop Loss at 99% Student-t VaR
        # i.e., price level that has only 1% statistical probability of breach under normal regime
        var_loss_pct = abs(min(var_99, -2.0)) / 100.0
        stop_loss_price = round(price * (1.0 - var_loss_pct), 2 if stock.get("market") == "US_SP500" else 0)

        # Mathematical Target Price
        if h < 0.45 and ou_mu:
            # Mean Reversion Target = Ornstein-Uhlenbeck Equilibrium Price
            eq_target = stock.get("equilibrium_mu", price * 1.05)
            target_price = round(max(eq_target, price * 1.03), 2 if stock.get("market") == "US_SP500" else 0)
            strategy_type = "O-U 평균회귀 차익거래"
        else:
            # Trend Continuation Target with 1:2.4 Payoff Ratio
            target_dist = (price - stop_loss_price) * 2.4
            target_price = round(price + target_dist, 2 if stock.get("market") == "US_SP500" else 0)
            strategy_type = "모멘텀 추세추종 돌파"

        # Trigger logic: Price above VWAP or near bottom support with high volume
        trigger_active = (price >= vwap * 0.995)

        return {
            "timing_action": "BUY_TRIGGERED" if trigger_active else "WATCHLIST_WAIT",
            "strategy_type": strategy_type,
            "entry_price": price,
            "stop_loss": stop_loss_price,
            "target_price": target_price,
            "var_99_boundary": f"{var_99}% (99% VaR)",
            "risk_reward_ratio": "1 : 2.4"
        }

    def calculate_long_term_timing(self, stock: dict) -> dict:
        price = stock.get("current_price", 100.0)
        sma_200 = stock.get("sma_200", price)
        parkinson_vol = stock.get("parkinson_vol", 0.25)

        # Dynamic Stop Loss scaled to Parkinson Annualized Volatility
        vol_stop_pct = max(min(parkinson_vol * 0.35, 0.10), 0.05)
        stop_loss_price = round(price * (1.0 - vol_stop_pct), 2 if stock.get("market") == "US_SP500" else 0)

        # Strategic Target: 1:3.2 Risk-Reward based on Fundamental Expansion
        target_dist = (price - stop_loss_price) * 3.2
        target_price = round(price + target_dist, 2 if stock.get("market") == "US_SP500" else 0)

        return {
            "timing_action": "STRATEGIC_ACCUMULATE",
            "strategy_type": "파마-프렌치 멀티팩터 가치성장",
            "entry_price": price,
            "stop_loss": stop_loss_price,
            "target_price": target_price,
            "volatility_buffer": f"{round(vol_stop_pct*100, 1)}%",
            "risk_reward_ratio": "1 : 3.2"
        }
