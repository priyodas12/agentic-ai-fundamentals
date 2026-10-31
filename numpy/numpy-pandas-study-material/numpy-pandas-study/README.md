# NumPy & Pandas — Study Material

A complete, runnable study track built for an engineer coming from **Java and SQL**.
Every concept is mapped to its SQL statement or Java equivalent, and every code cell has been executed and verified.

## Contents

| # | Notebook | What it covers |
|---|---|---|
| 01 | `01_numpy_foundations.ipynb` | Why NumPy exists, `ndarray` vs Java arrays, dtypes, indexing, **views vs copies**, reshape, the `axis` idea |
| 02 | `02_numpy_operations.ipynb` | ufuncs, **broadcasting rules**, boolean masks (`WHERE`), fancy indexing, aggregations, sorting, set operations |
| 03 | `03_numpy_advanced.ipynb` | C vs Fortran memory order, **strides**, sliding windows, structured arrays, `datetime64`, linear algebra, `einsum` |
| 04 | `04_pandas_foundations.ipynb` | `Series` / `DataFrame` / `Index`, dtypes, `read_csv`, `.loc` vs `.iloc`, filtering, missing data |
| 05 | `05_pandas_groupby_join_reshape.ipynb` | `groupby` (`agg` / `transform` / `filter` / `apply`), every join type, `concat`, `pivot_table`, `melt`, MultiIndex |
| 06 | `06_pandas_timeseries_and_windows.ipynb` | datetimes, `DatetimeIndex`, `resample`, rolling / expanding / ewm, `shift`, timezones, `merge_asof` |
| 07 | `07_performance_and_gotchas.ipynb` | The performance ladder with live benchmarks, memory shrinking, Copy-on-Write, the silent-wrong-answer traps |
| 08 | `08_sql_java_cheatsheet.ipynb` | SQL↔Pandas and Java Streams↔Pandas reference tables, side-by-side SQL/Pandas queries, **12 practice problems with solutions** |

Each notebook ends with exercises and a worked solution cell.

## Sample data

`data/` holds a small synthetic order-fulfilment dataset used throughout notebooks 04–08:

| File | Rows | Columns |
|---|---|---|
| `customers.csv` | 40 | `customer_id, name, city, tier, signup_date` |
| `orders.csv` | 500 | `order_id, customer_id, order_ts, status, channel, amount, discount_pct` |
| `order_items.csv` | ~1000 | `order_id, sku, qty` |
| `daily_metrics.csv` | 600 | `date, visits, conversions` |

Missing values and outliers are deliberately included so the cleaning sections have something real to work on.

## Running it

```bash
pip install numpy pandas jupyterlab
jupyter lab            # then open notebooks/01_numpy_foundations.ipynb
```

Or open the folder in VS Code (Python + Jupyter extensions), or upload the notebooks to Google Colab and upload the `data/` folder alongside.

The notebooks find the data folder automatically whether you run them from `notebooks/` or from the project root.

### Optional extras

| Package | Adds |
|---|---|
| `pyarrow` | Parquet read/write, faster string columns |
| `numexpr` | makes `df.eval` / `df.query` actually faster |
| `matplotlib` | `df.plot()` charts |

## Versions

Written and verified against **NumPy 2.4** and **Pandas 3.0** on Python 3.11.

Pandas 3.0 changed two things that older tutorials get wrong, and both are covered in the notebooks:

- **Copy-on-Write is always on.** Chained assignment (`df["a"][0] = 1`) silently does nothing. Use `df.loc[mask, "a"] = 1`.
- **Frequency aliases were renamed:** `M`→`ME`, `Q`→`QE`, `Y`→`YE`, `H`→`h`, `T`→`min`, `S`→`s`. The old single letters now raise `ValueError`.

## Suggested pace

| Session | Do this |
|---|---|
| 1 | Notebook 01 + exercises |
| 2 | Notebook 02 + exercises (broadcasting is the one to get right) |
| 3 | Notebook 03 — skim §6–7 on a first pass |
| 4 | Notebook 04 + exercises |
| 5 | Notebook 05 — the biggest payoff notebook if you know SQL |
| 6 | Notebook 06 |
| 7 | Notebook 07 — run the benchmarks on your own machine |
| 8 | Notebook 08 — problems 1–7 |
| 9 | Notebook 08 — problems 8–12, then redo a few against your own data |

## The five things worth memorising

1. `axis=k` is **the axis that disappears**.
2. Broadcasting aligns shapes **from the right**; a dimension of 1 stretches, anything else must match.
3. `.loc` is labels (end **inclusive**), `.iloc` is positions (end exclusive).
4. `groupby(...).transform(...)` is a SQL window function — one row out per row in.
5. If you are writing `for row in df`, there is a vectorized version and it is 100–1000x faster.
