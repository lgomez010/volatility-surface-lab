"""Fetch a fresh SPY option chain and save it to data/ as a dated CSV.

Run manually when you want updated market data:
    python scripts/refresh_snapshot.py

The saved CSV is committed to the repo so downstream code can run
without hitting yfinance.
"""

from __future__ import annotations
from datetime import date
from pathlib import Path

import yfinance as yf

from vollab.data.fetch import fetch_chain


TICKER = "SPY"
OUTPUT_DIR = Path("data/sample")


def pick_nearest_expiry(ticker: str, min_days: int = 7) -> str:
    """Return the soonest expiry at least `min_days` days out, as YYYY-MM-DD."""
    expiries = yf.Ticker(ticker).options
    if not expiries:
        raise RuntimeError(f"No expiries available for {ticker}")

    today = date.today()
    for expiry_str in expiries:
        expiry_date = date.fromisoformat(expiry_str)
        if (expiry_date - today).days >= min_days:
            return expiry_str

    raise RuntimeError(f"No expiries at least {min_days} days out for {ticker}")


def main() -> None:
    expiry = pick_nearest_expiry(TICKER)
    print(f"Fetching {TICKER} chain for expiry {expiry}...")

    df = fetch_chain(TICKER, expiry)

    OUTPUT_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    out_path = OUTPUT_DIR / f"{TICKER.lower()}_chain_{today}.csv"
    df.to_csv(out_path, index=False)

    print(f"Saved {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()