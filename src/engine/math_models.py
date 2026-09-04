import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

def calculate_hurst_exponent(price_series: pd.Series, max_lags=30) -> float:
    """
    Calculates the Hurst Exponent (H) via Rescaled Range (R/S) analysis.
    H < 0.45: Mean-Reverting (Anti-persistent - Ornstein-Uhlenbeck regime)
    0.45 <= H <= 0.55: Geometric Brownian Motion (Random Walk - Zero statistical edge)
    H > 0.55: Trending (Persistent - Momentum / Trend following regime)
    """
    ts = price_series.dropna().values
    n = len(ts)
    if n < 40:
        return 0.50

    lags = range(2, min(max_lags, n // 3))
    tau = []
    lagvec = []

    for lag in lags:
        diffs = ts[lag:] - ts[:-lag]
        if len(diffs) > 0:
            std = np.std(diffs)
            if std > 1e-8:
                tau.append(std)
                lagvec.append(lag)

    if len(tau) < 3:
        return 0.50

    poly = np.polyfit(np.log(lagvec), np.log(tau), 1)
    hurst = float(poly[0])
    return round(float(np.clip(hurst, 0.05, 0.95)), 3)

def calculate_ou_mean_reversion(price_series: pd.Series) -> dict:
    """
    Fits an Ornstein-Uhlenbeck (O-U) stochastic process using pure linear algebra:
    dX_t = theta * (mu - X_t) dt + sigma * dW_t
    Returns:
    - half_life (tau): Expected days for mean reversion = ln(2) / theta
    - z_score: Standardized deviation of current price from moving equilibrium
    - stationary: Whether ADF-type t-statistic indicates mean reversion (t < -2.86)
    """
    ts = price_series.dropna().values
    n = len(ts)
    if n < 30:
        return {"half_life": 10.0, "z_score": 0.0, "stationary": False, "equilibrium_mu": float(ts[-1]) if n > 0 else 100.0}

    x_prev = ts[:-1]
    dx = ts[1:] - x_prev

    try:
        # Linear regression dx = a + b * x_prev
        b, a = np.polyfit(x_prev, dx, 1)
        theta = -b

        # Compute t-statistic for stationarity (Dickey-Fuller t-test with constant)
        res = dx - (a + b * x_prev)
        s2 = np.sum(res ** 2) / max(n - 3, 1)
        denom = np.sum((x_prev - np.mean(x_prev)) ** 2)
        se_b = np.sqrt(s2 / max(denom, 1e-8))
        t_stat = b / max(se_b, 1e-8)
        stationary = (t_stat < -2.86)

        if theta > 1e-4:
            half_life = np.log(2.0) / theta
            half_life = min(max(half_life, 1.0), 60.0)
            equilibrium_mu = a / theta
        else:
            half_life = 99.0
            equilibrium_mu = np.mean(ts)
    except Exception:
        half_life = 20.0
        equilibrium_mu = np.mean(ts)
        stationary = False

    rolling_std = np.std(ts[-30:]) if n >= 30 else (np.std(ts) + 1e-6)
    current_price = ts[-1]
    z_score = (current_price - equilibrium_mu) / (rolling_std + 1e-8)

    return {
        "half_life": round(float(half_life), 1),
        "z_score": round(float(z_score), 2),
        "stationary": stationary,
        "equilibrium_mu": round(float(equilibrium_mu), 2)
    }

def calculate_parkinson_volatility(high_series: pd.Series, low_series: pd.Series, window=20) -> float:
    """
    Calculates Parkinson Extreme-Value Volatility:
    sigma_P = sqrt( 1 / (4 * ln(2) * N) * sum( ln(H_t / L_t)^2 ) ) * sqrt(252)
    5x more statistically efficient than standard close-to-close sample volatility.
    """
    if len(high_series) < window:
        return 0.25

    h = high_series.tail(window).values
    l = low_series.tail(window).values
    ratio = h / np.where(l > 0, l, 1.0)
    log_hl = np.log(np.maximum(ratio, 1.0))
    parkinson_var = (1.0 / (4.0 * np.log(2.0) * window)) * np.sum(log_hl ** 2)
    annualized_vol = np.sqrt(parkinson_var) * np.sqrt(252.0)
    return round(float(np.clip(annualized_vol, 0.05, 1.50)), 4)

def calculate_amihud_liquidity(close_series: pd.Series, volume_series: pd.Series, window=20) -> float:
    """
    Calculates Amihud (2002) Illiquidity Measure:
    ILLIQ = mean( |Return_t| / (Price_t * Volume_t) ) * 1e9
    Measures price impact per dollar traded. Lower = High liquidity / Institutional presence.
    """
    if len(close_series) < window:
        return 0.1

    ret = close_series.pct_change().abs().tail(window)
    dollar_vol = (close_series * volume_series).tail(window)
    illiq = (ret / np.where(dollar_vol > 0, dollar_vol, 1.0)).mean() * 1e9
    return round(float(np.nan_to_num(illiq, nan=0.1)), 4)

def calculate_kelly_position_sizing(win_prob: float, payoff_ratio: float, asset_volatility: float, target_vol=0.12) -> dict:
    """
    Fractional Kelly Criterion combined with Volatility Parity:
    f* = (p * b - q) / b
    where p = win probability, b = payoff ratio, q = 1 - p.
    Half-Kelly is applied for conservative capital preservation (Thorp & MacLean).
    """
    p = np.clip(win_prob, 0.35, 0.85)
    b = max(payoff_ratio, 1.1)
    q = 1.0 - p

    raw_kelly = (p * b - q) / b
    if raw_kelly <= 0:
        return {"kelly_weight": 0.0, "safe_allocation_pct": 2.0, "expected_value": 0.0}

    # Half-Kelly for mathematical safety margin
    half_kelly = raw_kelly * 0.5

    # Volatility targeting scalar
    vol_scale = target_vol / max(asset_volatility, 0.08)
    final_weight = half_kelly * vol_scale

    # Expected value per trade: E[R] = p * win_size - q * loss_size
    expected_value = (p * b - q) * 100.0

    alloc_pct = round(float(np.clip(final_weight * 100.0, 2.0, 15.0)), 1)

    return {
        "kelly_raw": round(float(raw_kelly), 3),
        "half_kelly": round(float(half_kelly), 3),
        "safe_allocation_pct": alloc_pct,
        "expected_value_pct": round(float(expected_value), 2)
    }

def calculate_parametric_var(price_series: pd.Series, confidence=0.99, horizon_days=1) -> dict:
    """
    Calculates Value at Risk (VaR 99%) and Expected Shortfall (CVaR)
    based on student-t distribution to account for financial fat tails.
    """
    returns = price_series.pct_change().dropna()
    if len(returns) < 30:
        return {"var_99_pct": -3.5, "cvar_99_pct": -4.8}

    mu = float(returns.mean())
    sigma = float(returns.std())

    # Fit Student-t distribution for fat tails
    try:
        df, loc, scale = stats.t.fit(returns)
        var_t = float(stats.t.ppf(1 - confidence, df, loc, scale))
    except Exception:
        var_t = mu - 2.326 * sigma  # Gaussian fallback

    # Expected Shortfall (CVaR): Average loss beyond VaR
    tail_losses = returns[returns <= var_t]
    cvar_t = float(tail_losses.mean()) if len(tail_losses) > 0 else var_t * 1.3

    return {
        "var_99_pct": round(var_t * 100.0, 2),
        "cvar_99_pct": round(cvar_t * 100.0, 2)
    }
