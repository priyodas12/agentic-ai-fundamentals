# NumPy 102

Follow-up notebooks covering intermediate NumPy topics: performance, indexing tricks, and broadcasting.

## Notebooks

| Notebook | Topic |
|---|---|
| [`src/_01_python_numpy_comparision.ipynb`](src/_01_python_numpy_comparision.ipynb) | Python lists vs. NumPy arrays — speed and memory comparison |
| [`src/_02_fancy_indexing.ipynb`](src/_02_fancy_indexing.ipynb) | Fancy indexing on 1-D/2-D arrays, boolean masks, in-place assignment, copy vs. view |
| [`src/_03_boolean_indexing.ipynb`](src/_03_boolean_indexing.ipynb) | Boolean masks, chained filters, combining conditions with `&`, negating with `~` |
| [`src/_04_broadcasting.ipynb`](src/_04_broadcasting.ipynb) | Broadcasting rules, shape mismatches, and combining multiple rules |

## Broadcasting at a glance

NumPy compares array shapes from the trailing dimension:

1. If one array has fewer dimensions, its shape is padded with 1s on the left.
2. Two dimension sizes are compatible if they're equal, or if one of them is 1 (it gets stretched to match).
3. If any pair of sizes differs and neither is 1, the shapes are incompatible and NumPy raises a `ValueError`.

**Example:** `a` has shape `(3, 4)`, `q` has shape `(1, 4)`. The single row of `q` is
repeated for every row of `a` (repeats marked with `*`), then added element-wise:

```
    a (3,4)          q (1,4) -> stretched         result (3,4)
  1   2   3   4        10  20  30  40          11  22  33  44
  5   6   7   8    +   10  20  30  40    =     15  26  37  48
  9  10  11  12        10  20  30  40*         19  30  41  52
                        ^ same row repeated
```

See `src/_04_broadcasting.ipynb` for the full set of runnable examples, including a mismatched-shape error and cases combining multiple rules at once.
