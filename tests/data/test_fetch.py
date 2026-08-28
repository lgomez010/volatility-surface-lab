import pandas as pd
import yfinance as yf
import pytest 
from collections import namedtuple
from unittest.mock import patch, MagicMock
from vollab.data.schema import SCHEMA, validate, add_time_to_expiry
from vollab.data.fetch import fetch_chain


def make_fake_calls():
    return pd.DataFrame({
        "contractSymbol": ["SPY260820C00500000", "SPY260820C00510000", "SPY260820C00520000"],
        "lastTradeDate": pd.to_datetime(["2026-08-15", "2026-08-15", "2026-08-15"]),
        "strike": [500.0, 510.0, 520.0],
        "lastPrice": [15.0, 8.0, 3.0],
        "bid": [14.90, 7.90, 2.90],
        "ask": [15.10, 8.10, 3.10],
        "change": [0.5, 0.3, 0.1],
        "percentChange": [3.4, 3.9, 3.5],
        "volume": [100, 200, 50],
        "openInterest": [1000, 2000, 500],
        "impliedVolatility": [0.18, 0.20, 0.22],
        "inTheMoney": [True, False, False],
        "contractSize": ["REGULAR", "REGULAR", "REGULAR"],
        "currency": ["USD", "USD", "USD"],
    })

def make_fake_puts():
    return pd.DataFrame({
        "contractSymbol": ["SPY260820P00500000", "SPY260820P00510000", "SPY260820P00520000"],
        "lastTradeDate": pd.to_datetime(["2026-08-15", "2026-08-15", "2026-08-15"]),
        "strike": [500.0, 510.0, 520.0],
        "lastPrice": [15.0, 8.0, 3.0],
        "bid": [14.90, 7.90, 2.90],
        "ask": [15.10, 8.10, 3.10],
        "change": [0.5, 0.3, 0.1],
        "percentChange": [3.4, 3.9, 3.5],
        "volume": [100, 200, 50],
        "openInterest": [1000, 2000, 500],
        "impliedVolatility": [0.18, 0.20, 0.22],
        "inTheMoney": [False, True, True],
        "contractSize": ["REGULAR", "REGULAR", "REGULAR"],
        "currency": ["USD", "USD", "USD"],
    })

@pytest.fixture
def mock_yf_ticker():
    Chain = namedtuple("Chain", ["calls", "puts"])
    fake_chain = Chain(calls=make_fake_calls(), puts=make_fake_puts())

    fake_ticker = MagicMock()
    fake_ticker.option_chain.return_value = fake_chain
    fake_ticker.history.return_value = pd.DataFrame({"Close": [505.0]})

    with patch("vollab.data.fetch.yf.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = fake_ticker
        yield fake_ticker


EXPIRY = "2026-09-11"


def test_returns_correct_shape(mock_yf_ticker):
    # 3 calls + 3 puts = 6 rows, schema defines 11 columns
    df = fetch_chain("SPY", EXPIRY)
    assert df.shape == (6, 11)


def test_expiry_appears_in_every_row(mock_yf_ticker):
    # The expiry we pass in should be copied to all 6 rows
    df = fetch_chain("SPY", EXPIRY)
    assert (df["expiry"] == pd.Timestamp(EXPIRY)).all()


def test_risk_free_rate_appears_in_every_row(mock_yf_ticker):
    # The scalar rate we pass in should be broadcast to all 6 rows
    df = fetch_chain("SPY", EXPIRY, risk_free_rate=0.07)
    assert (df["risk_free_rate"] == 0.07).all()


def test_calls_and_puts_are_labeled_correctly(mock_yf_ticker):
    # Should have exactly 3 rows tagged "C" and 3 tagged "P"
    df = fetch_chain("SPY", EXPIRY)
    assert (df["type"].iloc[:3] == "C").all()
    assert (df["type"].iloc[3:] == "P").all()


def test_time_to_expiry_is_positive_and_reasonable(mock_yf_ticker):
    # T should be positive (expiry in future) and small (< 18 days from now)
    df = fetch_chain("SPY", EXPIRY)
    assert (df["T"] > 0).all()
    assert (df["T"] < 0.05).all()

def test_all_schema_columns_present(mock_yf_ticker):
    # Every column defined by SCHEMA should exist in the output
    df = fetch_chain("SPY", EXPIRY)
    missing = set(SCHEMA.keys()) - set(df.columns)
    assert not missing, f"Missing schema columns: {missing}"