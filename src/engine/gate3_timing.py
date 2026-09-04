import logging

logger = logging.getLogger(__name__)

class Gate3TimingEngine:
    """
    Gate 3: Precision Timing Trigger Engine.
    Calculates specific entry prices, stop-loss levels, and take-profit targets.
    """

    def calculate_short_term_timing(self, stock: dict) -> dict:
        price = stock.get("current_price", 0)
        vwap = stock.get("vwap", price)
        atr = stock.get("atr_14", price * 0.02)
        rsi = stock.get("rsi_14", 50)

        # Trigger logic
        above_vwap = price >= vwap
        momentum_good = (45 <= rsi <= 70)

        # Tight Stop Loss: 1.5 * ATR or hard stop 2.5%
        stop_loss_dist = max(atr * 1.5, price * 0.025)
        stop_loss_price = round(price - stop_loss_dist, 2 if stock.get("market") == "US_SP500" else 0)

        # Target: Risk-Reward 1:2.5
        target_dist = stop_loss_dist * 2.5
        target_price = round(price + target_dist, 2 if stock.get("market") == "US_SP500" else 0)

        timing_action = "BUY_TRIGGERED" if (above_vwap and momentum_good) else "WATCHLIST_WAIT"

        return {
            "timing_action": timing_action,
            "entry_price": price,
            "stop_loss": stop_loss_price,
            "target_price": target_price,
            "risk_reward_ratio": "1 : 2.5",
            "trigger_notes": f"VWAP({vwap}) 상단 지지 확인, 단기 손절선: {stop_loss_price}"
        }

    def calculate_long_term_timing(self, stock: dict) -> dict:
        price = stock.get("current_price", 0)
        sma_20 = stock.get("sma_20", price)
        sma_50 = stock.get("sma_50", price)
        sma_200 = stock.get("sma_200", price)

        # Strategic Stop Loss: 7% or break of 200 SMA
        stop_loss_price = round(min(price * 0.93, sma_200 * 0.97), 2 if stock.get("market") == "US_SP500" else 0)

        # Target: 20% ~ 35% fundamental expansion
        target_price = round(price * 1.25, 2 if stock.get("market") == "US_SP500" else 0)

        # Timing: Buy on pullbacks near SMA 20 or SMA 50
        dist_to_sma20 = abs(price - sma_20) / sma_20
        is_pullback = dist_to_sma20 <= 0.04

        timing_action = "STRATEGIC_ACCUMULATE" if is_pullback else "WAIT_FOR_PULLBACK"

        return {
            "timing_action": timing_action,
            "entry_price": price,
            "stop_loss": stop_loss_price,
            "target_price": target_price,
            "risk_reward_ratio": "1 : 3.5",
            "trigger_notes": f"20일선({sma_20}) 부근 눌림목 분할 매수 적합, 손절선: {stop_loss_price}"
        }
