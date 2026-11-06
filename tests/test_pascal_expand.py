import os
import sys
import unittest
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pascal_expand import (Term, expand, format_polynomial, parse_binomial,
                           pascal_row)


def run(text):
    return format_polynomial(expand(*parse_binomial(text)))


class PascalRowTests(unittest.TestCase):
    def test_first_rows(self):
        self.assertEqual(pascal_row(0), [1])
        self.assertEqual(pascal_row(1), [1, 1])
        self.assertEqual(pascal_row(4), [1, 4, 6, 4, 1])

    def test_matches_binomial_coefficients(self):
        for n in range(25):
            self.assertEqual(pascal_row(n), [comb(n, k) for k in range(n + 1)])

    def test_negative_row(self):
        with self.assertRaises(ValueError):
            pascal_row(-1)


class ParseTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_binomial("(2x - 3y)^5"),
                         (Term(2, "x"), Term(-3, "y"), 5))
        self.assertEqual(parse_binomial("(x^2+1)^3"),
                         (Term(1, "x", 2), Term(1), 3))
        self.assertEqual(parse_binomial("(-a + b)**2"),
                         (Term(-1, "a"), Term(1, "b"), 2))

    def test_bad_input(self):
        for bad in ["x + 1", "(x + 1)^", "(x + 1)^-2", "(+ 1)^2"]:
            with self.assertRaises(ValueError, msg=bad):
                parse_binomial(bad)


class ExpandTests(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(run("(x + 1)^4"), "x⁴ + 4x³ + 6x² + 4x + 1")
        self.assertEqual(run("(a + b)^3"), "a³ + 3a²b + 3ab² + b³")
        self.assertEqual(run("(2x - 3y)^3"), "8x³ - 36x²y + 54xy² - 27y³")
        self.assertEqual(run("(x^2 - 1)^3"), "x⁶ - 3x⁴ + 3x² - 1")
        self.assertEqual(run("(x - 2)^0"), "1")
        self.assertEqual(run("(3 + 2)^3"), "125")

    def test_like_terms_combine(self):
        self.assertEqual(run("(x + x)^2"), "4x²")
        self.assertEqual(run("(x - x)^3"), "0")

    def test_numeric_check(self):
        # Evaluate both sides at x = 2, y = -1.
        a, b, n = parse_binomial("(3x - 2y)^6")
        lhs = (3 * 2 - 2 * -1) ** n
        rhs = sum(c * 2 ** p.get("x", 0) * (-1) ** p.get("y", 0)
                  for c, p in expand(a, b, n))
        self.assertEqual(lhs, rhs)


if __name__ == "__main__":
    unittest.main()
