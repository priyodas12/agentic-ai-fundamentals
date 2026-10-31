# Pandas 101

A beginner-friendly introduction to [pandas](https://pandas.pydata.org/), the Python library for data manipulation and analysis.

## What is Pandas?

Pandas is an open-source Python library used for working with structured (tabular) data — think spreadsheets or SQL tables, but manipulated in code. It provides fast, flexible data structures and tools for:

- Reading/writing data (CSV, Excel, JSON, SQL, etc.)
- Cleaning and transforming data
- Filtering, grouping, and aggregating
- Merging and joining datasets
- Basic statistics and time series analysis

It's built on top of NumPy and is one of the core tools in the Python data science ecosystem.

## Series

A `Series` is a one-dimensional labeled array. It's like a single column of data with an index attached to each value.

```python
import pandas as pd

s = pd.Series([10, 20, 30, 40], index=["a", "b", "c", "d"])
print(s)
```

Output:

```
a    10
b    20
c    30
d    40
dtype: int64
```

You can access values by label or position:

```python
s["b"]     # 20
s.iloc[1]  # 20
```

## DataFrame

A `DataFrame` is a two-dimensional labeled data structure — rows and columns, like a table. You can think of it as a collection of `Series` that share the same index.

```python
import pandas as pd

data = {
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "Chicago"]
}

df = pd.DataFrame(data)
print(df)
```

Output:

```
      name  age     city
0    Alice   25      NYC
1      Bob   30       LA
2  Charlie   35  Chicago
```

Common operations:

```python
df["age"]              # select a column (returns a Series)
df[df["age"] > 28]     # filter rows
df.loc[0]               # select a row by label
df.iloc[0]               # select a row by position
df["age"].mean()        # compute a statistic
```

## Project Contents

- `src/series/_01_series.ipynb` — notebook exploring the `Series` data structure.

## Getting Started

```bash
pip install pandas jupyter
jupyter notebook
```

Then open the notebooks under `src/` to follow along.
