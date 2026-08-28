"""Tests for src/data/filter.py."""

import pandas as pd
import pytest

from vollab.data.filter import (
    filter_zero_bid,
    filter_wide_spread,
    filter_illiquid,
    filter_chain,
)


def make_chain(rows):
    """Build a chain DataFrame from a list of (bid, ask, volume, oi) tuples."""
    return pd.DataFrame(rows, columns=["bid", "ask", "volume", "open_interest"])


def test_zero_bid_rows_are_dropped():
    df = make_chain([
        (0.0, 1.0, 100, 100),   # dead: zero bid
        (2.0, 1.5, 100, 100),   # crossed
        (1.0, 1.1, 100, 100),   # valid
    ])
    out = filter_zero_bid(df)
    assert len(out) == 1
    assert out.iloc[0]["bid"] == 1.0


def test_wide_spread_rows_are_dropped():
    df = make_chain([
        (0.85, 1.15, 100, 100),   # 30% spread
        (0.975, 1.025, 100, 100), # 5% spread
    ])
    out = filter_wide_spread(df, max_spread_pct=0.10)
    assert len(out) == 1
    assert out.iloc[0]["bid"] == 0.975


def test_illiquid_rows_are_dropped():
    df = make_chain([
        (1.0, 1.1, 0, 500),   # zero vol, high OI → keep
        (1.0, 1.1, 0, 2),     # zero vol, low OI  → drop
        (1.0, 1.1, 50, 0),    # some vol, zero OI → keep
    ])
    out = filter_illiquid(df, min_open_interest=10)
    assert len(out) == 2
    assert 2 not in out["open_interest"].values


def test_mid_price_column_is_added_and_correct():
    df = make_chain([(1.0, 1.1, 100, 100), (2.0, 2.2, 100, 100)])
    out = filter_chain(df)
    assert "mid" in out.columns
    assert out["mid"].tolist() == [1.05, 2.1]


def test_filter_chain_composes_all_three():
    df = make_chain([
        (0.0, 1.0, 100, 100),    # zero bid → drop
        (0.85, 1.15, 100, 100),  # 30% spread → drop
        (1.0, 1.1, 0, 2),        # illiquid → drop
        (1.0, 1.1, 100, 100),    # survivor
    ])
    out = filter_chain(df)
    assert len(out) == 1
    assert out.iloc[0]["bid"] == 1.0