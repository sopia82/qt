import logging
from src.config import MAX_SHORT_TERM_POSITIONS, MAX_LONG_TERM_POSITIONS

logger = logging.getLogger(__name__)

class Gate4RiskEngine:
    """
    Gate 4: Dynamic Risk Management & Position Sizing Engine.
    Adjusts individual allocation based on ATR volatility and Macro Exposure multiplier.
    """

    def calculate_position_size(self, stock: dict, horizon: str, macro_exposure: float = 1.0) -> dict:
        price = stock.get("current_price", 100)
        atr = stock.get("atr_14", price * 0.02)
        volatility_pct = (atr / price) if price > 0 else 0.02

        if horizon == "SHORT_TERM":
            base_allocation_pct = 5.0  # Default 5% per short-term idea
            # Inverse volatility weighting: more volatile = smaller size
            adjusted_pct = base_allocation_pct * (0.025 / max(volatility_pct, 0.01))
            final_pct = min(adjusted_pct * macro_exposure, 5.0)
            max_positions = MAX_SHORT_TERM_POSITIONS
        else:
            base_allocation_pct = 12.0  # Default 12% per long-term idea
            adjusted_pct = base_allocation_pct * (0.02 / max(volatility_pct, 0.01))
            final_pct = min(adjusted_pct * macro_exposure, 15.0)
            max_positions = MAX_LONG_TERM_POSITIONS

        return {
            "target_allocation_pct": round(max(final_pct, 2.0), 1),
            "max_positions_limit": max_positions,
            "volatility_risk": "HIGH" if volatility_pct > 0.035 else "NORMAL"
        }
