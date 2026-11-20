"""Write the full table for n = 12 in the layout of the published tables for n <= 11.

For every bracketing of 12 copies of i, in the published order, the table says either
that its value is new (with the running count of distinct values) or which earlier
bracketing it equals. The result can then be refuted by exhibiting a single wrong line:
a pair marked equal that differs, or a pair marked different that is equal.
"""

import pathlib

from a198683 import published
from a198683.bruteforce import evaluate_all

DEFAULT_OUT = published.REPO_ROOT / "tables" / "a198683_n12.txt"


def table_lines(n: int, values: list) -> list:
    width = max(len("Expression"), max(len(v.text) for v in values))
    rule = f"{'-' * 5} {'-' * width} {'-' * 5} {'-' * 5}"
    lines = [f"n = {n}:", "", f"Index {'Expression':<{width}} Count Match", rule]
    first_with_form, count = {}, 0
    for index, v in enumerate(values, start=1):
        if v.key in first_with_form:
            lines.append(f"{index:>5} {v.text:<{width}} {'':5} {first_with_form[v.key]:>5}")
        else:
            first_with_form[v.key] = index
            count += 1
            lines.append(f"{index:>5} {v.text:<{width}} {count:>5}")
    total = f"A198683({n}) = {count}"
    return lines + [rule, "=" * len(total), total, "=" * len(total)]


def write(out: pathlib.Path = DEFAULT_OUT, all_values: dict | None = None) -> list:
    """Write the n = 12 table. Returns its lines.

    First regenerates the published n = 11 table and requires it to match line for line,
    which checks both the layout and the grouping.
    """
    all_values = all_values or evaluate_all(12)
    if table_lines(11, all_values[11]) != published.section(11):
        raise AssertionError("regenerated n = 11 table differs from the published one")
    lines = table_lines(12, all_values[12])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    return lines
