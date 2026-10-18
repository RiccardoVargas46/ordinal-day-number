# Ordinal Day Number

Convert calendar dates to and from a sequential day number keyed from a fixed epoch. The library gives you a small, stable integer you can use as an array index or storage key for days.

```python
from ordinal_day_number import to_ordinal, from_ordinal, EPOCH_YEAR

n = to_ordinal(2024, 3, 1)        # -> 19745
y, m, d = from_ordinal(19745)     # -> (2024, 3, 1)
assert EPOCH_YEAR == 1970
assert from_ordinal(to_ordinal(2000, 2, 29)) == (2000, 2, 29)
```

## Why this exists

Date-keyed storage wants one integer per day that sorts the same way dates do and is cheap to compare. ISO strings sort correctly but cost more to store and compare; broken-down `(year, month, day)` tuples are bulky. A dense day index is the lightest option.

The trade-off is epoch choice. This library pins the epoch at `1970-01-01` so that values stay small for modern data and line up with the Unix day boundary, which makes cross-checks against the standard library's `datetime.date` trivial. `1970-01-01` maps to `1`; the day before maps to `0`, the day before that to `-1`. Negative indices are intentional and supported back to year 1.

The calendar is strict proleptic Gregorian. The 1582 Julian/Gregorian transition is deliberately out of scope; modelling it would make the answer locale-dependent and defeat the point of a stable index.

## Awkward edge you will hit

Leap years. `1900` is **not** a leap year (divisible by 100, not 400); `2000` **is**. The library rejects impossible dates like `1900-02-29` rather than silently clamping them. If you feed it `bool` for any component it raises `TypeError` — `bool` is a subclass of `int` in Python, which is a common source of silent surprises.

## Exports

- `to_ordinal(year, month, day) -> int` — day number, `1` at `1970-01-01`, decreasing into the past.
- `from_ordinal(n) -> tuple[int, int, int]` — inverse; accepts negative `n`.
- `EPOCH_YEAR` — `1970`.
- `MAX_YEAR` — `9999`.

Years `1..9999` are accepted, matching `datetime.date`. Inputs outside that range raise `ValueError`.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

