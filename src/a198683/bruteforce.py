"""Evaluate every bracketing individually, with no reduction to distinct values.

Slower than count.py (58,786 bracketings at n = 12 instead of 5,139 candidates), but it
does not rely on the step "the value of a^b depends only on the values of a and b", and
it gives every bracketing its own entry, which the tables and the checks need.
"""

from a198683.core import power, unit_i


def evaluate_all(n_max: int) -> dict:
    """{n: [Value for every bracketing of n copies of i]}, in the order of the published tables.

    Order: by size of the base, then by index of the base, then by index of the exponent.
    """
    all_values = {1: [unit_i()]}
    for n in range(2, n_max + 1):
        all_values[n] = [
            power(a, b)
            for size_a in range(1, n)
            for a in all_values[size_a]
            for b in all_values[n - size_a]
        ]
    return all_values


def group_by_form(values: list) -> dict:
    """{normal form: [(index, Value)]} with indices starting at 1."""
    groups = {}
    for index, v in enumerate(values, start=1):
        groups.setdefault(v.key, []).append((index, v))
    return groups
