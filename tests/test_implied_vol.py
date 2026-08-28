"""Tests for implied volatility extraction."""

import numpy as np
import pytest

from vollab.black_scholes import call_price, put_price
from vollab.utils.implied_vol import implied_vol


@pytest.mark.parametrize("sigma_true", [0.10, 0.20, 0.35, 0.60])
def test_round_trip_call(sigma_true):
    """price -> IV -> price should recover the original sigma."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    price = call_price(S, K, T, r, sigma_true)
    sigma_recovered = implied_vol(price, S, K, T, r, "C")
    assert np.isclose(sigma_recovered, sigma_true, atol=1e-6)


@pytest.mark.parametrize("sigma_true", [0.10, 0.20, 0.35, 0.60])
def test_round_trip_put(sigma_true):
    """Same round-trip check for puts."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    price = put_price(S, K, T, r, sigma_true)
    sigma_recovered = implied_vol(price, S, K, T, r, "P")
    assert np.isclose(sigma_recovered, sigma_true, atol=1e-6)


@pytest.mark.parametrize("option_type,pricer", [
    ("C", call_price),
    ("P", put_price),
])
@pytest.mark.parametrize("K", [80, 90, 100, 110, 120])
def test_round_trip_across_strikes(option_type, pricer, K):
    """Round-trip should work across strikes (ITM, ATM, OTM) for both types."""
    S, T, r, sigma_true = 100.0, 0.5, 0.05, 0.25
    price = pricer(S, K, T, r, sigma_true)
    assert np.isclose(implied_vol(price, S, K, T, r, option_type), sigma_true, atol=1e-6)


def test_call_below_intrinsic_returns_nan():
    """Price below intrinsic value violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 80.0, 1.0, 0.05
    intrinsic = S - K * np.exp(-r * T)
    result = implied_vol(intrinsic - 1.0, S, K, T, r, "C")
    assert np.isnan(result)


def test_call_above_spot_returns_nan():
    """Price above spot violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    result = implied_vol(S + 1.0, S, K, T, r, "C")
    assert np.isnan(result)


def test_put_above_discounted_strike_returns_nan():
    """Put price above K*exp(-rT) violates no-arbitrage -> NaN."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    result = implied_vol(K * np.exp(-r * T) + 1.0, S, K, T, r, "P")
    assert np.isnan(result)


def test_call_and_put_agree_at_atm_forward():
    """At K = S*exp(rT), put-call parity forces IV_call == IV_put."""
    S, T, r, sigma_true = 100.0, 1.0, 0.05, 0.25
    K = S * np.exp(r * T)
    iv_c = implied_vol(call_price(S, K, T, r, sigma_true), S, K, T, r, "C")
    iv_p = implied_vol(put_price(S, K, T, r, sigma_true), S, K, T, r, "P")
    assert np.isclose(iv_c, iv_p, atol=1e-6)


def test_bad_option_type_raises():
    """Bad option_type is a programmer error -> raise, not NaN."""
    with pytest.raises(ValueError):
        implied_vol(5.0, 100.0, 100.0, 1.0, 0.05, "X")