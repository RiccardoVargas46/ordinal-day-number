"""Core conversion logic for Ordinal Day Number.

Interpretation
--------------
The Ordinal Day Number (ODN) is a 1-based index of days measured from a fixed
epoch. We chose ``1970-01-01`` as the epoch because it aligns with the Unix day
boundary used by ``datetime.date.toordinal()`` for the same era, which makes
spot-checks against the standard library trivial. Unlike ``date.toordinal()
``, which counts from ``0001-01-01``, ODN counts from 1970 so the numbers stay
small and human-comparable for modern date ranges, which is the use case
(date-keyed storage and indexing) the library exists to serve.

The only supported calendar is proleptic Gregorian. We deliberately do not
model the 1582 Julian/Gregorian transition; doing so would force a locale-
dependent answer and defeat the point of a stable index.

Range
-----
Years 1..9999 are accepted, matching the proleptic Gregorian range of
``datetime.date``. ODN is signed as a concept but in practice never negative
within the accepted range, so we return plain ``int`` values.

Edge cases handled
------------------
* Leap years use the standard Gregorian rule (divisible by 4, not by 100,
  unless by 400). 1900 is not a leap year; 2000 is.
* Day/month clamping is rejected, never silently fixed: month 13 or day 32
  raises ``ValueError``.
* Symmetry: ``from_ordinal(to_ordinal(d)) == d`` for every in-range date.
* Boundary: 1970-01-01 maps to 1, 1969-12-31 maps to 0, 1969-12-30 maps to -1.
  Negative indices are valid and intentional; see README for the caveat.
"""

from __future__ import annotations

import datetime as _dt

EPOCH_YEAR: int = 1970
MAX_YEAR: int = 9999

# Julian day number of 1970-01-01 in the proleptic Gregorian calendar, as used
# by datetime.date. Pre-computing this lets us delegate the proleptic Gregorian
# arithmetic to the stdlib (which has well-tested leap-year handling) without
# re-implementing it, while still producing a 1-based-from-epoch integer.
_EPOCH_JULIAN: int = _dt.date(EPOCH_YEAR, 1, 1).toordinal()


def _validate_year(year: int) -> None:
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("year must be an int")
    if year < 1 or year > MAX_YEAR:
        raise ValueError(f"year must be in 1..{MAX_YEAR}, got {year}")


def _validate_month(month: int) -> None:
    if not isinstance(month, int) or isinstance(month, bool):
        raise TypeError("month must be an int")
    if month < 1 or month > 12:
        raise ValueError(f"month must be in 1..12, got {month}")


def to_ordinal(year: int, month: int, day: int) -> int:
    """Return the Ordinal Day Number for ``year-month-day``.

    The number is 1 for ``1970-01-01`` and increases by one per subsequent day.
    Dates before the epoch yield non-positive numbers (0, -1, ...).

    We delegate to ``datetime.date`` for the proleptic Gregorian arithmetic
    rather than hand-rolling leap-year math. The stdlib implementation is the
    de facto reference; re-implementing it would only add risk.
    """
    _validate_year(year)
    _validate_month(month)
    if not isinstance(day, int) or isinstance(day, bool):
        raise TypeError("day must be an int")
    if day < 1:
        raise ValueError(f"day must be >= 1, got {day}")

    # Let datetime enforce the per-month day bounds (28/29/30/31). It raises
    # ValueError for impossible combinations like 2023-02-29.
    try:
        d = _dt.date(year, month, day)
    except ValueError as exc:
        # Re-raise with our own message so callers see a consistent surface.
        raise ValueError(f"invalid date {year:04d}-{month:02d}-{day:02d}: {exc}") from exc

    # toordinal() counts from 0001-01-01. Subtract the epoch's julian number
    # and add 1 because we want 1970-01-01 itself to be 1, not 0.
    return d.toordinal() - _EPOCH_JULIAN + 1


def from_ordinal(n: int) -> tuple[int, int, int]:
    """Inverse of :func:`to_ordinal`: return ``(year, month, day)`` for ODN ``n``.

    Negative inputs are accepted and produce pre-epoch dates, down to year 1.
    Inputs that would resolve to a year < 1 or > ``MAX_YEAR`` raise
    ``ValueError``.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("ordinal must be an int")

    julian = n + _EPOCH_JULIAN - 1
    if julian < 1:
        raise ValueError(f"ordinal {n} is before year 1")
    max_julian = _dt.date(MAX_YEAR, 12, 31).toordinal()
    if julian > max_julian:
        raise ValueError(f"ordinal {n} is after year {MAX_YEAR}")

    d = _dt.date.fromordinal(julian)
    return (d.year, d.month, d.day)
