"""Tests for src/data/schema.py"""

import pandas as pd
import pytest
from src.data.schema import SCHEMA, SchemaError, validate
from src.data.schema import SCHEMA

@pytest.fixture
def make_df():
    """Factory returning a 3-row DataFrame matching SCHEMA."""

    def _make():
        return pd.DataFrame({
            "timestamp": pd.to_datetime(
                ["2026-01-01", "2026-01-01", "2026-01-01"], utc=True
            ),
            "expiry": pd.to_datetime(["2027-01-01", "2027-01-01", "2027-01-01"]),
            "spot": pd.Series([500.0, 500.0, 500.0], dtype="float64"),
            "risk_free_rate": pd.Series([0.04, 0.04, 0.04], dtype="float64"),
            "strike": pd.Series([490.0, 500.0, 510.0], dtype="float64"),
            "bid": pd.Series([15.20, 10.10, 6.30], dtype="float64"),
            "ask": pd.Series([15.40, 10.30, 6.50], dtype="float64"),
            "T": pd.Series([1.0, 1.0, 1.0], dtype="float64"),
            "type": pd.Series(["C", "P", "C"], dtype=SCHEMA["type"]),
            "volume": pd.Series([1200, 800, 450], dtype="Int64"),
            "open_interest": pd.Series([5000, 3200, 1800], dtype="Int64"),
        })

    return _make

def test_validate_accepts_valid_df(make_df):
    from src.data.schema import validate

    df = make_df()
    validate(df)  # should not raise

def test_validate_rejects_missing_column(make_df):
    df = make_df().drop(columns=["open_interest"])
    with pytest.raises(SchemaError, match="open_interest"):
        validate(df)

def test_validate_rejects_extra_column(make_df):
    df = make_df().assign(unexpected=1.0)
    with pytest.raises(SchemaError, match="unexpected"):
        validate(df)

def test_validate_rejects_wrong_dtype(make_df):
    df = make_df()
    df["strike"] = df["strike"].astype("int64")
    with pytest.raises(SchemaError, match="strike"):
        validate(df)

def test_validate_reports_all_violations(make_df):
    df = make_df().drop(columns=["open_interest"]).assign(unexpected=1.0)
    df["strike"] = df["strike"].astype("int64")

    with pytest.raises(SchemaError) as exc_info:
        validate(df)

    msg = str(exc_info.value)
    assert "open_interest" in msg
    assert "unexpected" in msg
    assert "strike" in msg

def test_add_time_to_expiry_computes_T_and_does_not_mutate():
    from src.data.schema import add_time_to_expiry

    original = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01"], utc=True),
        "expiry": pd.to_datetime(["2027-01-01"]),
    })

    result = add_time_to_expiry(original)

    assert result["T"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    assert "T" not in original.columns