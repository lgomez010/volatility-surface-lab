"""Tests for implied volatility extraction."""

import numpy as np
import pytest

from src.black_scholes import call_price, put_price
from src.utils.implied_vol import implied_vol_call, implied_vol_put


@pytest.mark.parametrize("sigma_true", [0.10, 0.20, 0.35, 0.60])
def test_round_trip_call(sigma_true):
    """price -> IV -> price should recover the original sigma."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    price = call_price(S, K, T, r, sigma_true)
    sigma_recovered = implied_vol_call(price, S, K, T, r)
    assert np.isclose(sigma_recovered, sigma_true, atol=1e-6)


@pytest.mark.parametrize("sigma_true", [0.10, 0.20, 0.35, 0.60])
def test_round_trip_put(sigma_true):
    """Same round-trip check for puts."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    price = put_price(S, K, T, r, sigma_true)
    sigma_recovered = implied_vol_put(price, S, K, T, r)
    assert np.isclose(sigma_recovered, sigma_true, atol=1e-6)


@pytest.mark.parametrize("K", [80, 90, 100, 110, 120])
def test_round_trip_across_strikes(K):
    """Round-trip should work across the strike range (ITM, ATM, OTM)."""
    S, T, r, sigma_true = 100.0, 0.5, 0.05, 0.25
    price = call_price(S, K, T, r, sigma_true)
    sigma_recovered = implied_vol_call(price, S, K, T, r)
    assert np.isclose(sigma_recovered, sigma_true, atol=1e-6)


def test_call_below_intrinsic_returns_nan():
    """Price below intrinsic value violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 80.0, 1.0, 0.05
    intrinsic = S - K * np.exp(-r * T)
    result = implied_vol_call(intrinsic - 1.0, S, K, T, r)
    assert np.isnan(result)


def test_call_above_spot_returns_nan():
    """Price above spot violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    result = implied_vol_call(S + 1.0, S, K, T, r)
    assert np.isnan(result)


def test_put_above_discounted_strike_returns_nan():
    """Put price above K*exp(-rT) violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    result = implied_vol_put(K * np.exp(-r * T) + 1.0, S, K, T, r)
    assert np.isnan(result)