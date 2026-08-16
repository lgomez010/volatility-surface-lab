"""
Implied volatility extraction from European option prices.

Uses Brent's method for guaranteed convergence inside a bracket.
Newton-Raphson is faster per iteration but blows up when vega -> 0
(deep OTM, near-expiry) -- exactly the wings where reliable IV
extraction matters most for surface construction.
"""

import numpy as np
from scipy.optimize import brentq

from src.black_scholes import call_price, put_price


def implied_vol_call(
    price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    sigma_lo: float = 1e-6,
    sigma_hi: float = 5.0,
    tol: float = 1e-8,
) -> float:
    """
    Extract implied volatility from a European call price via Brent's method.

    Parameters
    ----------
    price : float
        Observed market price of the call.
    S : float
        Current spot price of the underlying.
    K : float
        Strike price.
    T : float
        Time to maturity in years.
    r : float
        Risk-free interest rate (continuously compounded).
    sigma_lo, sigma_hi : float
        Bracket for the root search. Defaults [1e-6, 5.0] cover any
        realistic equity vol regime.
    tol : float
        Absolute tolerance on sigma passed to brentq.

    Returns
    -------
    float
        Implied volatility, or NaN if the price violates no-arbitrage
        bounds or Brent fails to bracket a root.
    """
    # No-arbitrage bounds for a European call:
    #   max(S - K*exp(-rT), 0) <= C <= S
    intrinsic = max(S - K * np.exp(-r * T), 0.0)
    if price < intrinsic or price > S:
        return np.nan

    f = lambda sigma: call_price(S, K, T, r, sigma) - price

    try:
        return brentq(f, sigma_lo, sigma_hi, xtol=tol)
    except ValueError:
        # No sign change in the bracket -> no root exists in [sigma_lo, sigma_hi].
        return np.nan


def implied_vol_put(
    price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    sigma_lo: float = 1e-6,
    sigma_hi: float = 5.0,
    tol: float = 1e-8,
) -> float:
    """
    Extract implied volatility from a European put price via Brent's method.

    Parameters
    ----------
    price : float
        Observed market price of the put.
    S, K, T, r : float
        Spot, strike, time to maturity, risk-free rate.
    sigma_lo, sigma_hi, tol : float
        Bracket and tolerance for the root search.

    Returns
    -------
    float
        Implied volatility, or NaN if the price violates no-arbitrage
        bounds or Brent fails to bracket a root.
    """
    # No-arbitrage bounds for a European put:
    #   max(K*exp(-rT) - S, 0) <= P <= K*exp(-rT)
    discounted_K = K * np.exp(-r * T)
    intrinsic = max(discounted_K - S, 0.0)
    if price < intrinsic or price > discounted_K:
        return np.nan

    f = lambda sigma: put_price(S, K, T, r, sigma) - price

    try:
        return brentq(f, sigma_lo, sigma_hi, xtol=tol)
    except ValueError:
        return np.nan