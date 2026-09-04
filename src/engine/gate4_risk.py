import logging
from src.config import MAX_SHORT_TERM_POSITIONS, MAX_LONG_TERM_POSITIONS
from src.engine.math_models import calculate_kelly_position_sizing

logger = logging.getLogger(__name__)

class Gate4RiskEngine:
    """
    Mathematical Portfolio Sizing via Fractional Kelly Criterion & Volatility Targeting.
    f* = (p * b - q) / b * 0.5 (Half-Kelly)
    """

    def calculate_position_size(self, stock: dict, horizon: str, win_prob: float = 0.60, macro_exposure: float = 1.0) -> dict:
        parkinson_vol = stock.get("parkinson_vol", 0.25)

        if horizon == "SHORT_TERM":
            payoff_ratio = 2.4
            target_annual_vol = 0.10  # 10% target volatility
            max_limit = 6.0
        else:
            payoff_ratio = 3.2
            target_annual_vol = 0.14  # 14% target volatility
            max_limit = 15.0

        kelly = calculate_kelly_position_sizing(
            win_prob=win_prob,
            payoff_ratio=payoff_ratio,
            asset_volatility=parkinson_vol,
            target_vol=target_annual_vol
        )

        safe_alloc = min(kelly["safe_allocation_pct"] * macro_exposure, max_limit)

        return {
            "target_allocation_pct": round(max(safe_alloc, 2.0), 1),
            "half_kelly_score": kelly["half_kelly"],
            "expected_value_pct": kelly["expected_value_pct"],
            "parkinson_vol": round(parkinson_vol * 100.0, 1),
            "win_probability_pct": round(win_prob * 100.0, 1)
        }
