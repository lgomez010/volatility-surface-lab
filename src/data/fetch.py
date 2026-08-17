from src.data.schema import SCHEMA, validate, add_time_to_expiry
import pandas as pd
import yfinance as yf


def fetch_chain(ticker: str, expiry: str, risk_free_rate=0.04,
                ) -> pd.DataFrame:
    """fetch an options chain snapshot for one ticker and one expiry

        Parameters:
        ---------------------
        ticker : str    
        Underlying ticker symbol, e.g. "SPY" or "AAPL".

        expiry : str    
        Expiration date in "YYYY-MM-DD" format, e.g. "2027-01-15".

        risk_free_rate: float, default 0.04     
        constant rate across all expiries assumption
        
        Returns : 
        ---------------------
        pd.DataFrame
        SCHEMA's 11 columns and one row per contract 
        (calls and puts combined, distinguished by the `type` column).
    """

    # --- fetch raw market data ---
    tkr = yf.Ticker(ticker)
    chain = tkr.option_chain(expiry)
    spot = tkr.history(period="1d")["Close"].iloc[-1]

    # --- combine calls and puts into one long-format frame ---
    calls = chain.calls.copy()
    puts = chain.puts.copy()
    calls["type"] = "C"
    puts["type"] = "P"
    df = pd.concat([calls, puts], ignore_index=True) 

   # --- add schema columns not provided by yfinance ---
    df["timestamp"] = pd.Timestamp.now(tz="UTC").as_unit("ns")     # schema needs tz-aware UTC
    df["expiry"] = pd.to_datetime(expiry)
    df["spot"] = spot
    df["risk_free_rate"] = risk_free_rate

    # --- conform to schema: rename, drop junk, cast dtypes, compute T, order columns ---
    df = df.rename(columns={"openInterest": "open_interest"})
    df = df.drop(columns=[
        "contractSymbol", "lastTradeDate", "lastPrice",
        "change", "percentChange", "impliedVolatility",
        "inTheMoney", "contractSize", "currency",
    ])
    df["type"] = df["type"].astype(pd.CategoricalDtype(["C", "P"]))
    df["volume"] = df["volume"].astype("Int64")
    df["open_interest"] = df["open_interest"].astype("Int64")
    df = add_time_to_expiry(df)
    df = df[list(SCHEMA.keys())]  # match schema column order

    # --- check before the frame enters pipeline ---
    validate(df)
    return df



