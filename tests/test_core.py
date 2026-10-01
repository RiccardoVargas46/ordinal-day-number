"""Tests for ordinal_day_number.core.

Covers the documented interpretation and the edge cases the implementation
actually handles. We do not test any behaviour the code does not claim to
support (e.g. Julian/Gregorian transition, time-of-day, time zones).
"""

import datetime as dt
import unittest

from ordinal_day_number.core import (
    EPOCH_YEAR,
    MAX_YEAR,
    to_ordinal,
    from_ordinal,
)


class TestEpochAndConstants(unittest.TestCase):
    def test_epoch_year_is_1970(self):
        self.assertEqual(EPOCH_YEAR, 1970)

    def test_max_year_is_9999(self):
        self.assertEqual(MAX_YEAR, 9999)


class TestToOrdinal(unittest.TestCase):
    def test_epoch_maps_to_one(self):
        self.assertEqual(to_ordinal(1970, 1, 1), 1)

    def test_day_after_epoch_is_two(self):
        self.assertEqual(to_ordinal(1970, 1, 2), 2)

    def test_day_before_epoch_is_zero(self):
        self.assertEqual(to_ordinal(1969, 12, 31), 0)

    def test_two_days_before_epoch_is_negative_one(self):
        self.assertEqual(to_ordinal(1969, 12, 30), -1)

    def test_matches_date_toordinal_offset(self):
        # Spot check against the stdlib for a scatter of dates across centuries.
        anchor = dt.date(1970, 1, 1).toordinal()
        cases = [
            (1, 1, 1),
            (100, 2, 28),
            (1582, 10, 15),  # Gregorian reform date, treated as proleptic Gregorian here
            (1899, 12, 31),
            (1900, 2, 28),   # 1900 is NOT a leap year
            (1904, 2, 29),   # 1904 is a leap year
            (1970, 1, 1),
            (2000, 2, 29),   # 2000 is a leap year (divisible by 400)
            (2024, 12, 31),
            (9999, 12, 31),
        ]
        for (y, m, d) in cases:
            with self.subTest(y=y, m=m, d=d):
                expected = dt.date(y, m, d).toordinal() - anchor + 1
                self.assertEqual(to_ordinal(y, m, d), expected)

    def test_leap_day_2000_accepted(self):
        self.assertEqual(to_ordinal(2000, 2, 29), to_ordinal(2000, 3, 1) - 1)

    def test_non_leap_day_1900_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(1900, 2, 29)

    def test_zero_year_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(0, 1, 1)

    def test_year_above_max_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(MAX_YEAR + 1, 1, 1)

    def test_zero_month_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(2020, 0, 1)

    def test_month_thirteen_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(2020, 13, 1)

    def test_zero_day_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(2020, 1, 0)

    def test_day_thirty_one_in_april_rejected(self):
        with self.assertRaises(ValueError):
            to_ordinal(2020, 4, 31)

    def test_bool_year_rejected(self):
        # bool is a subclass of int; we refuse it explicitly to avoid surprises.
        with self.assertRaises(TypeError):
            to_ordinal(True, 1, 1)

    def test_string_year_rejected(self):
        with self.assertRaises(TypeError):
            to_ordinal("2020", 1, 1)


class TestFromOrdinal(unittest.TestCase):
    def test_one_returns_epoch(self):
        self.assertEqual(from_ordinal(1), (1970, 1, 1))

    def test_two_returns_next_day(self):
        self.assertEqual(from_ordinal(2), (1970, 1, 2))

    def test_zero_returns_day_before_epoch(self):
        self.assertEqual(from_ordinal(0), (1969, 12, 31))

    def test_negative_one_returns_two_days_before_epoch(self):
        self.assertEqual(from_ordinal(-1), (1969, 12, 30))

    def test_end_of_range(self):
        self.assertEqual(from_ordinal(to_ordinal(9999, 12, 31)), (9999, 12, 31))

    def test_before_year_one_rejected(self):
        # 0001-01-01 is the smallest representable proleptic Gregorian date.
        boundary = to_ordinal(1, 1, 1)
        with self.assertRaises(ValueError):
            from_ordinal(boundary - 1)

    def test_after_max_year_rejected(self):
        boundary = to_ordinal(MAX_YEAR, 12, 31)
        with self.assertRaises(ValueError):
            from_ordinal(boundary + 1)

    def test_bool_rejected(self):
        with self.assertRaises(TypeError):
            from_ordinal(True)

    def test_string_rejected(self):
        with self.assertRaises(TypeError):
            from_ordinal("1")


class TestSymmetry(unittest.TestCase):
    def test_roundtrip_representative_set(self):
        cases = [
            (1, 1, 1),
            (1582, 10, 4),     # Julian-Gregorian boundary region, treated proleptically
            (1582, 10, 15),
            (1900, 2, 28),
            (1969, 12, 30),
            (1969, 12, 31),
            (1970, 1, 1),
            (1970, 1, 2),
            (2000, 2, 29),
            (2023, 11, 23),
            (9999, 12, 31),
        ]
        for (y, m, d) in cases:
            with self.subTest(y=y, m=m, d=d):
                self.assertEqual(from_ordinal(to_ordinal(y, m, d)), (y, m, d))

    def test_inverse_roundtrip(self):
        # Round-trip the other direction for values that are in range.
        for n in (1, 0, -1, 100, -100, to_ordinal(2000, 2, 29), to_ordinal(9999, 12, 31)):
            with self.subTest(n=n):
                self.assertEqual(to_ordinal(*from_ordinal(n)), n)


if __name__ == "__main__":
    unittest.main()
