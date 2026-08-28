"""filters for option chain DataFrames

Used to remove untradeable quotes before implied vol extraction. Each filter targets one market pathology:
  - filter_zero_bid: dead quotes (no market maker on the bid)
  - filter_wide_spread: illiquid strikes where mid-price is fiction
  - filter_illiquid: stale contracts with no volume and no open interest

filter_chain runs all three and adds a mid-price column so downstream
code doesn't have to compute it again.
"""

from __future__ import annotations
import pandas as pd



def filter_zero_bid(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with non-positive bid, non-positive ask, or crossed quotes.

    A zero bid means no market maker is willing to buy at any price —
    the quote is dead. Crossed quotes (ask < bid) are stale prints.
    """
    mask = (df["bid"] > 0) & (df["ask"] > 0) & (df["ask"] >= df["bid"])
    return df.loc[mask].reset_index(drop=True)


def filter_wide_spread(df: pd.DataFrame, max_spread_pct: float = 0.10) -> pd.DataFrame:
    """Drop rows where the bid-ask spread exceeds `max_spread_pct` of mid.

    Relative (not absolute) threshold — scale-invariant across strikes and
    maturities. Assumes `filter_zero_bid` has already run, so mid > 0.
    """
    mid = (df["bid"] + df["ask"]) / 2
    spread_pct = (df["ask"] - df["bid"]) / mid
    return df.loc[spread_pct <= max_spread_pct].reset_index(drop=True)


def filter_illiquid(df: pd.DataFrame, min_open_interest: int = 10) -> pd.DataFrame:
    """Drop rows with zero volume AND open interest below `min_open_interest`.

    Disjunction is deliberate: a contract with 500 OI but no trades today
    is still liquid; a contract with 2 volume and 0 OI is a fluke print.
    """
    mask = (df["volume"] > 0) | (df["open_interest"] >= min_open_interest)
    return df.loc[mask].reset_index(drop=True)


def filter_chain(
    df: pd.DataFrame,
    max_spread_pct: float = 0.10,
    min_open_interest: int = 10,
) -> pd.DataFrame:
    """Apply all quality filters and add a mid-price column.

    Order matters: zero-bid runs first so the spread filter can safely
    divide by mid (mid is zero on dead quotes). Mid is added last so
    we don't compute it for rows we're about to drop.
    """
    df = filter_zero_bid(df)
    df = filter_wide_spread(df, max_spread_pct=max_spread_pct)
    df = filter_illiquid(df, min_open_interest=min_open_interest)
    df = df.copy()
    df["mid"] = (df["bid"] + df["ask"]) / 2
    return df.reset_index(drop=True)
