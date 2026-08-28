"""Schema definition and validation for options snapshot DataFrames"""

import pandas as pd


class SchemaError(ValueError):
    """Raise error when a dataframe does not match"""

SCHEMA = {
    "timestamp": "datetime64[ns, UTC]",
    "expiry": "datetime64[ns]",
    "spot": "float64",
    "risk_free_rate": "float64",
    "strike": "float64",
    "bid": "float64",
    "ask": "float64",
    "T": "float64",
    "type": pd.CategoricalDtype(categories=["C", "P"]),
    "volume": "Int64",
    "open_interest": "Int64"
}

def validate(df: pd.DataFrame) -> None:
    """Validate df matches SCHEMA and raise any errors"""
    errors = []

    required = set(SCHEMA.keys()) #column names
    actual = set(df.columns)

    missing = required - actual
    if missing:
        errors.append(f"missing columns: {sorted(missing)}")

    extra = actual - required
    if extra:
        errors.append(f"unexpected columns: {sorted(extra)}")

    for col in SCHEMA:
        if col not in df.columns:
            continue
        if df[col].dtype != SCHEMA[col]:
            errors.append(f"{col}: expected {SCHEMA[col]}, got {df[col].dtype}")

    if errors:
        raise SchemaError(
            "Schema validation failed:\n  - " + "\n  - ".join(errors)
        )

DAYS_PER_YEAR = 365
SECONDS_PER_YEAR = DAYS_PER_YEAR * 86400 #86400 = 24 * 60 * 60 


def add_time_to_expiry(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a 'T' column: time to expiry in years."""

    df = df.copy()
    delta = df["expiry"].dt.tz_localize("UTC") - df["timestamp"] #timedelta
    df["T"] = delta.dt.total_seconds() / SECONDS_PER_YEAR
    return df

