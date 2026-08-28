"""
Implied volatility extraction from European option prices.

Uses Brent's method: guaranteed convergence inside a bracket, no
derivative required. Newton-Raphson converges faster (quadratic vs.
Brent's superlinear) and vega is available in closed form, but Newton
breaks when vega collapses — deep OTM/ITM (phi(d_1) -> 0) and near
expiry (sqrt(T) -> 0) — which happens on every real vol surface. Brent
trades a small speed cost for robustness across the full grid.
"""

import numpy as np
from scipy.optimize import brentq

from src.black_scholes import call_price, put_price


def implied_vol(
    price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "C",
    *,
    sigma_lo: float = 1e-6,
    sigma_hi: float = 5.0,
    tol: float = 1e-8,
) -> float:
    """
    Extract implied volatility from a European option price via Brent's method.

    Parameters
    ----------
    price : float
        Observed market price.
    S, K, T, r : float
        Spot, strike, time to maturity (years), risk-free rate.
    option_type : {"C", "P"}
        Call or put.
    sigma_lo, sigma_hi : float
        Bracket for the root search.
    tol : float
        Absolute tolerance on sigma.

    Returns
    -------
    float
        Implied vol, or NaN if the price violates no-arb bounds
        or Brent fails to bracket a root.
    """

    if option_type not in ("C", "P"):
        raise ValueError(f"option_type must be 'C' or 'P', got {option_type!r}")

    if T <= 0 or S <= 0 or K <= 0 or price <= 0: 
        return np.nan
    
    discounted_K = K * np.exp(-r * T)
    if option_type == "C":
        lower, upper = max(S - discounted_K, 0.0), S
        pricer = call_price
    else:
        lower, upper = max(discounted_K - S, 0.0), discounted_K
        pricer = put_price

    if price < lower or price > upper:
        return np.nan

    f = lambda sigma: pricer(S, K, T, r, sigma) - price

    try:
        return brentq(f, sigma_lo, sigma_hi, xtol=tol)
    except ValueError:
        return np.nan