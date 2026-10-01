"""Ordinal Day Number: convert calendar dates to and from sequential day numbers.

Interpretation chosen (stated plainly, see README for the full rationale):
  * Ordinal Day Number is an unsigned count where 1 = 1970-01-01.
  * Epoch is fixed; the library does not read system time or locale.
  * Calendar dates are strict (Gregorian); 1582-style Julian/Gregorian splits are out of scope.
"""

from .core import (
    EPOCH_YEAR,
    MAX_YEAR,
    to_ordinal,
    from_ordinal,
)

__all__ = [
    "EPOCH_YEAR",
    "MAX_YEAR",
    "to_ordinal",
    "from_ordinal",
]
