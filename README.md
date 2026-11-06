# Pascal's Triangle to Expand a Polynomial

Expand any binomial `(a + b)^n` using Pascal's triangle, with the work shown.

Row *n* of Pascal's triangle gives the coefficients of `(a + b)^n`:

```
        1                 (a + b)^0
      1   1               (a + b)^1
    1   2   1             (a + b)^2
  1   3   3   1           (a + b)^3
1   4   6   4   1         (a + b)^4  =  a⁴ + 4a³b + 6a²b² + 4ab³ + b⁴
```

Each term is `coefficient × a^(n−k) × b^k`: the power of the first term counts
down from *n* to 0 while the power of the second term counts up from 0 to *n*.

## In the browser

Open `index.html` (no install needed — it also works with GitHub Pages).
Type a binomial such as `(2x - 3)^4` to see the answer, the highlighted row of
Pascal's triangle, and a term-by-term table.

## From the command line (Python 3.8+)

```bash
python pascal_expand.py "(x + 1)^4"
# x⁴ + 4x³ + 6x² + 4x + 1

python pascal_expand.py "(2x - 3y)^3" --steps   # show the work
python pascal_expand.py --triangle 6            # print rows 0–6
```

Each term of the binomial can be a whole number, a one-letter variable with an
optional exponent, or both: `3`, `-x`, `2x`, `4y^2`.

## Tests

```bash
python -m unittest discover -s tests
```
