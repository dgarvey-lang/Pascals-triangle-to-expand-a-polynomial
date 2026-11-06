"""Expand a binomial (a + b)^n using Pascal's triangle.

Examples
--------
    $ python pascal_expand.py "(x + 1)^4"
    $ python pascal_expand.py "(2x - 3y)^5" --steps
    $ python pascal_expand.py --triangle 6

Each term of the binomial may be an integer coefficient, a single-letter
variable with an optional exponent, or both: 3, -x, 2x, 4y^2, -5a^3.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

SUPERSCRIPTS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


# ---------------------------------------------------------------------------
# Pascal's triangle
# ---------------------------------------------------------------------------

def pascal_row(n: int) -> list[int]:
    """Return row n of Pascal's triangle (row 0 is [1])."""
    if n < 0:
        raise ValueError("row number must be non-negative")
    row = [1]
    for _ in range(n):
        # Each new entry is the sum of the two entries above it.
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row


def pascal_triangle(n: int) -> list[list[int]]:
    """Return rows 0 through n of Pascal's triangle."""
    return [pascal_row(k) for k in range(n + 1)]


def format_triangle(rows: list[list[int]], highlight: int | None = None) -> str:
    """Center the rows of the triangle as text; mark the highlighted row."""
    lines = ["   ".join(str(v) for v in row) for row in rows]
    width = max(len(line) for line in lines)
    out = []
    for i, line in enumerate(lines):
        marker = "  <-- row %d" % i if i == highlight else ""
        out.append(line.center(width).rstrip() + marker)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Terms and parsing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Term:
    """A monomial: coef * var^power (var may be empty for a constant)."""

    coef: int
    var: str = ""
    power: int = 1

    def raised(self, k: int) -> "Term":
        return Term(self.coef ** k, self.var, self.power * k)


_TERM = r"([+-]?)\s*(\d*)\s*([a-zA-Z]?)(?:\s*\^\s*(\d+))?"
_BINOMIAL = re.compile(
    r"^\(?\s*" + _TERM + r"\s*([+-])\s*(\d*)\s*([a-zA-Z]?)(?:\s*\^\s*(\d+))?\s*\)?\s*\^\s*(\d+)\s*$"
)


def _make_term(sign: str, digits: str, var: str, power: str) -> Term:
    if not digits and not var:
        raise ValueError("empty term")
    coef = int(digits) if digits else 1
    if sign == "-":
        coef = -coef
    if power and not var:
        raise ValueError("an exponent inside a term needs a variable, e.g. x^2")
    return Term(coef, var, int(power) if power else 1)


def parse_binomial(text: str) -> tuple[Term, Term, int]:
    """Parse text like "(2x - 3y)^5" into (first term, second term, n)."""
    m = _BINOMIAL.match(text.strip().replace("**", "^"))
    if not m:
        raise ValueError(
            f"could not read {text!r}; use a form like (2x - 3)^4 or (a + b)^5"
        )
    s1, d1, v1, p1, s2, d2, v2, p2, n = m.groups()
    return _make_term(s1, d1, v1, p1), _make_term(s2, d2, v2, p2), int(n)


# ---------------------------------------------------------------------------
# Expansion
# ---------------------------------------------------------------------------

def expand(a: Term, b: Term, n: int) -> list[tuple[int, dict[str, int]]]:
    """Expand (a + b)^n.

    Returns a list of polynomial terms, ordered by descending power of a.
    Like terms are combined (e.g. when both terms use the same variable).
    """
    combined: dict[tuple[tuple[str, int], ...], int] = {}
    order: list[tuple[tuple[str, int], ...]] = []
    for k, c in enumerate(pascal_row(n)):
        coef = c * a.coef ** (n - k) * b.coef ** k
        powers: dict[str, int] = {}
        for t, e in ((a, n - k), (b, k)):
            if t.var and e:
                powers[t.var] = powers.get(t.var, 0) + t.power * e
        key = tuple(sorted(powers.items()))
        if key not in combined:
            combined[key] = 0
            order.append(key)
        combined[key] += coef
    return [(combined[key], dict(key)) for key in order if combined[key] != 0]


def _monomial(coef: int, powers: dict[str, int], first: bool) -> str:
    sign = "-" if coef < 0 else ("" if first else "+")
    mag = abs(coef)
    vars_ = "".join(v + (str(p).translate(SUPERSCRIPTS) if p != 1 else "")
                    for v, p in sorted(powers.items()))
    body = vars_ if (mag == 1 and vars_) else f"{mag}{vars_}"
    if first:
        return f"{sign}{body}"
    return f" {sign} {body}"


def format_polynomial(terms) -> str:
    if not terms:
        return "0"
    return "".join(_monomial(c, p, i == 0) for i, (c, p) in enumerate(terms))


def format_term(t: Term) -> str:
    return format_polynomial([(t.coef, {t.var: t.power} if t.var and t.power else {})])


def explain(a: Term, b: Term, n: int) -> str:
    """Return a step-by-step explanation of the expansion."""
    row = pascal_row(n)
    fa, fb = format_term(a), format_term(b)
    lines = [
        f"Expand ({fa} + {fb})^{n}".replace("+ -", "- "),
        "",
        f"Step 1. Row {n} of Pascal's triangle gives the coefficients:",
        "",
        format_triangle(pascal_triangle(n), highlight=n),
        "",
        f"Step 2. Write each term as  C · ({fa})^(n-k) · ({fb})^k :",
        "",
    ]
    for k, c in enumerate(row):
        ak, bk = a.raised(n - k), b.raised(k)
        value = c * ak.coef * bk.coef
        powers: dict[str, int] = {}
        for t in (ak, bk):
            if t.var and t.power:
                powers[t.var] = powers.get(t.var, 0) + t.power
        lines.append(
            f"  k={k}:  {c} · ({fa})^{n - k} · ({fb})^{k}"
            f"  =  {c} · ({format_term(ak)}) · ({format_term(bk)})"
            f"  =  {format_polynomial([(value, powers)])}"
        )
    lines += [
        "",
        "Step 3. Add the terms:",
        "",
        "  " + format_polynomial(expand(a, b, n)),
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("binomial", nargs="?", help='e.g. "(2x - 3)^4"')
    parser.add_argument("--steps", action="store_true", help="show the work")
    parser.add_argument("--triangle", type=int, metavar="N",
                        help="print rows 0..N of Pascal's triangle")
    args = parser.parse_args(argv)

    if args.triangle is not None:
        print(format_triangle(pascal_triangle(args.triangle)))
        if not args.binomial:
            return 0
    if not args.binomial:
        parser.print_help()
        return 1
    try:
        a, b, n = parse_binomial(args.binomial)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(explain(a, b, n) if args.steps else format_polynomial(expand(a, b, n)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
