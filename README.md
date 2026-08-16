# Volatility Surface Lab

[![tests](https://github.com/lgomez010/volatility-surface-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/lgomez010/volatility-surface-lab/actions/workflows/tests.yml)

Volatility surface construction, calibration, and modeling — from implied vol extraction through classical stochastic vol calibration to rough Bergomi with Hurst exponent estimation. Includes a mathematical writeup connecting rough volatility to log-correlated Gaussian fields and Gaussian multiplicative chaos.

**Status:** Scaffold. Active development.

## Planned Scope

- **Implied vol extraction** from live and historical option chains (SPX/SPY via `yfinance`).
- **Smile and surface visualization** across strike and maturity.
- **SVI parameterization** (Gatheral) with arbitrage-free checks (butterfly, calendar).
- **Dupire local volatility** via the forward PDE.
- **Heston calibration** to market surfaces via Gil-Pelaez pricing + least-squares.
- **Rough Bergomi** simulation and pricing; Hurst exponent estimation from realized volatility.
- **GMC connection**: mathematical writeup linking log-volatility in rough Bergomi to log-correlated Gaussian fields and Gaussian multiplicative chaos.

## Quickstart

    git clone git@github.com:lgomez010/volatility-surface-lab.git
    cd volatility-surface-lab
    pip install -e ".[dev]"
    pytest

## Project Structure

    volatility-surface-lab/
    ├── src/           # Core modules (implied vol, SVI, Dupire, Heston, rough Bergomi, ...)
    │   └── utils/     # Shared utilities (data loading, ...)
    ├── tests/         # Pytest suite
    ├── notebooks/     # Exploratory and presentation notebooks
    ├── scripts/       # Data refresh, batch runs
    └── data/          # Committed option chain snapshots (reproducibility)

## References

- Gatheral, *The Volatility Surface: A Practitioner's Guide* (2006)
- Bergomi, *Stochastic Volatility Modeling* (2016), Ch. 8–11
- Gatheral, Jaisson, Rosenbaum, "Volatility is Rough" (2018)
- Bayer, Friz, Gatheral, "Pricing under Rough Volatility" (2016)
- Gatheral & Jacquier, "Arbitrage-free SVI volatility surfaces" (2014)
- Albrecher et al., "The Little Heston Trap" (2007)

## License

MIT