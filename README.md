# volatility-surface-lab

**A research-driven implementation of classical and rough volatility models, with a mathematical bridge to log-correlated Gaussian fields and Gaussian Multiplicative Chaos (GMC).**

---

## Why this project

This project takes **rough volatility** — the empirical observation that log-volatility behaves like fractional Brownian motion with Hurst exponent $H \approx 0.1$ — as its main focus, with the goal of eventually coming to **log-correlated Gaussian fields** and **Gaussian Multiplicative Chaos (GMC)**.

I first encountered GMC at a summer school on probabilistic number theory hosted by the Université de Montréal, and was excited that the same object appears in the rough Bergomi model. This project is where I explore that connection.


---

## Status

**Active development.** The data layer is committed and tested; modeling milestones are in progress. See the [Roadmap](#roadmap) for a milestone-by-milestone layout. Currently I'm on M3.

**What runs today:**
- Schema-validated options data pipeline (`src/data/schema.py`, `src/data/fetch.py`)
- Live ingestion from Yahoo Finance with strict dtype and column-set validation
- Test suite covering schema violations and data contract enforcement

**What's next:** liquidity filtering, implied vol extraction, SVI calibration, the rough Bergomi and Hurst estimation.

---

## Quickstart

```bash
git clone git@github.com:lgomez010/volatility-surface-lab.git
cd volatility-surface-lab
pip install -r requirements.txt
pytest
```

Fetch a schema-validated options chain snapshot:

```python
from vollab.data.fetch import fetch_chain

df = fetch_chain(ticker="SPY", expiry="2027-01-15", risk_free_rate=0.04)
print(df.shape)   # (n_contracts, 11)
print(df.dtypes)  # matches SCHEMA 
```

The returned frame is guaranteed to satisfy the project schema (11 columns, exact dtypes, calls and puts in long format with a categorical `type` column). Downstream modules assume this contract holds.

---

## Project structure

```
volatility-surface-lab/
├── src/
│   ├── data/
│   │   ├── schema.py         # SCHEMA definition, validate(), add_time_to_expiry() - done
│   │   ├── fetch.py          # Live ingestion (yfinance → SCHEMA-conformant frame) - done
│   │   └── filter.py         # Liquidity filters (spread, volume, OI) - in progress
│   ├── iv/                   # Implied vol extraction (Brent / Newton) - not started
│   ├── svi/                  # SVI slice fits + arbitrage checks - not started
│   ├── dupire/               # Local vol from surface - not started
│   ├── heston/               # Calibration via characteristic function + FFT - not started
│   ├── rough_bergomi/        # fBm simulation, ATM skew scaling - not started
│   └── hurst/                # Hurst exponent estimation from realized vol - not started
├── tests/
│   └── data/
│       ├── test_schema.py    # Six passing tests
│       └── test_fetch.py     # In progress
├── notebooks/                # Calibration + comparison notebooks - not started
├── data/                     # Committed snapshot CSVs for reproducibility - not started
├── NOTES.md                  # GMC - rough vol writeup - not started
└── README.md
```

---

## Roadmap

Milestones are executed in order. 

- **M1 — Repository scaffolding.** CI (Python 3.11/3.12/3.13), SSH auth, MIT license.
- **M2 — Data schema.** Long-format snapshot schema (11 columns), validation with error accumulation. Six passing unit tests.
- **M3 — Data ingestion.** Live yfinance pipeline (`fetch.py` shipped and verified). Liquidity filter, snapshot script, and committed CSV in progress.
- **M4 — Implied vol extraction.** Brent's method on Black–Scholes vega with handling of deep ITM/OTM and near-expiry regimes.
- **M5 — SVI calibration.** Per-maturity slice fits with butterfly and calendar arbitrage checks (Gatheral–Jacquier 2014).
- **M6 — Dupire local volatility.** Numerical implementation of Dupire's formula from the calibrated surface.
- **M7 — Heston calibration.** FFT pricing (reusing the [`options-pricing-engine`](https://github.com/lgomez010/options-pricing-engine) Heston module) + least-squares calibration to the market surface.
- **M8 — Rough volatility.**
  - Hurst exponent estimation from historical realized vol (variogram / R/S analysis).
  - Rough Bergomi Monte Carlo via hybrid scheme.
  - Short-maturity ATM skew comparison: rough Bergomi ($T^{H-1/2}$) vs. Heston.
  - Mathematical writeup connecting log-vol to GMC.

---

## Mathematical background

### Implied volatility and the surface

For a European option with market price $C_{\text{mkt}}(K, T)$, the **implied volatility** $\sigma_{\text{imp}}(K, T)$ is the unique $\sigma$ satisfying $C_{\text{BS}}(S, K, T, r, \sigma) = C_{\text{mkt}}(K, T)$. Since Black–Scholes vega is strictly positive, this inverse problem is well-posed and solvable by Brent's method. Viewed across strikes and maturities, $\sigma_{\text{imp}}$ traces out a **surface**, which classical Black–Scholes assumes is constant. 

### SVI parameterization

The Stochastic Volatility Inspired (SVI) parameterization (Gatheral 2004) represents total variance $w(k) = \sigma^2_{\text{imp}}(k) T$ as a function of log-moneyness $k = \log(K/F)$:

$$w(k) = a + b \left( \rho (k - m) + \sqrt{(k - m)^2 + \sigma^2} \right).$$

SVI slice fits must satisfy no-butterfly and no-calendar arbitrage conditions to be admissible.

### Rough volatility

Gatheral, Jaisson, and Rosenbaum (2018) showed that log-realized-volatility across liquid assets behave like a fractional Brownian motion with Hurst exponent $H \approx 0.1$ — far below the $H = 1/2$ implicit in classical stochastic volatility models. The **rough Bergomi** model (Bayer–Friz–Gatheral 2016) posits

$$\log v_t = \log \xi_0(t) + \eta \sqrt{2H} \int_0^t (t-s)^{H - 1/2} \, dW_s - \tfrac{1}{2}\eta^2 t^{2H},$$

which produces the characteristic short-maturity ATM skew scaling $\text{ATM skew}(T) \sim T^{H-1/2}$ observed in equity index markets and not reproducible under Heston.

### The GMC connection

The kernel $(t-s)^{H-1/2}$ makes $\log v_t$ a **log-correlated Gaussian field** in the appropriate scaling limit: the covariance diverges logarithmically at coincident points. The exponential of such a field, formally $e^{\gamma X(t) - \tfrac{\gamma^2}{2} \mathbb{E}[X(t)^2]}$, is the object studied under the name **Gaussian Multiplicative Chaos** — a random measure with fractal support, well-defined for $\gamma^2 < 2d$.

---

## References

**Books**
- Gatheral, J. *The Volatility Surface: A Practitioner's Guide.* Wiley, 2006.
- Bergomi, L. *Stochastic Volatility Modeling.* Chapman & Hall/CRC, 2016. (Ch. 8–11 on rough volatility.)
- Rebonato, R. *Volatility and Correlation: The Perfect Hedger and the Fox.* Wiley, 2004.
- Hull, J. *Options, Futures, and Other Derivatives.* Pearson.

**Papers**
- Gatheral, J. "A parsimonious arbitrage-free implied volatility parameterization." Presentation, 2004.
- Gatheral, J. and Jacquier, A. "Arbitrage-free SVI volatility surfaces." *Quantitative Finance*, 2014.
- Bayer, C., Friz, P., and Gatheral, J. "Pricing under rough volatility." *Quantitative Finance*, 2016.
- Gatheral, J., Jaisson, T., and Rosenbaum, M. "Volatility is rough." *Quantitative Finance*, 2018.
- Albrecher, H. et al. "The little Heston trap." *Wilmott Magazine*, 2007.

**On GMC and log-correlated fields**
- Bacry, E., Delour, J., and Muzy, J.F. "Multifractal random walk." *Physical Review E*, 2001.
- Rhodes, R. and Vargas, V. "Gaussian multiplicative chaos and applications: a review." *Probability Surveys*, 2014.

---

## License

MIT

## Contact

Luis Gomez - [lgomez010.github.io](https://lgomez010.github.io)
