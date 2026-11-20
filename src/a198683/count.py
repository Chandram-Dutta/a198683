"""The main computation: a lower and an upper bound for a(n), n = 1..12.

The value of a^b depends only on the values of a and b. So the values of towers of
height n are obtained by combining the DISTINCT values of smaller towers, which is far
fewer than all Catalan(n-1) bracketings (5,139 candidates instead of 58,786 at n = 12).

    lower bound   number of groups of candidates with pairwise disjoint balls
    upper bound   number of distinct exact normal forms among the candidates

When the two agree and every group is a single normal form, a(n) is determined.
"""

from dataclasses import dataclass

from flint import arb

from a198683.core import Value, overlap_groups, power, unit_i

MAX_N = 12


@dataclass
class Row:
    n: int
    candidates: int
    lower: int
    upper: int
    exact: bool  # bounds agree here and for every smaller n


@dataclass
class Result:
    rows: list  # one Row per n
    classes: dict  # {n: one representative Value per distinct value}

    def exceptional(self):
        """Values at the largest n that defeat ordinary arithmetic: (unresolved, near_one)."""
        top = self.classes[max(self.classes)]
        unresolved = [v for v in top if not v.resolved]
        near_one = [v for v in top if v.resolved and abs(v.L).upper() < arb("1e-100")]
        return unresolved, near_one


def bounds(n_max: int = MAX_N) -> Result:
    if n_max > MAX_N:
        raise ValueError(f"n > {MAX_N} is not supported: a value with unresolved phase would be reused")
    classes = {1: [unit_i()]}
    rows = [Row(1, 1, 1, 1, True)]
    for n in range(2, n_max + 1):
        candidates = [
            power(a, b)
            for size_a in range(1, n)  # the base uses size_a copies of i, the exponent n - size_a
            for a in classes[size_a]
            for b in classes[n - size_a]
        ]
        groups = overlap_groups(candidates)
        lower = len(groups)
        upper = len({v.key for v in candidates})
        one_form_per_group = all(len({v.key for v in g}) == 1 for g in groups)
        exact = lower == upper and one_form_per_group and rows[-1].exact
        rows.append(Row(n, len(candidates), lower, upper, exact))
        classes[n] = [min(g, key=_simplest) for g in groups]
    return Result(rows, classes)


def _simplest(v: Value):
    return (not v.resolved, len(v.text))


def report(result: Result) -> str:
    lines = [f"{'n':>3} {'candidates':>11} {'lower bound':>12} {'upper bound':>12}   result"]
    for r in result.rows:
        verdict = f"a({r.n}) = {r.lower}" if r.exact else f"{r.lower} <= a({r.n}) <= {r.upper}"
        lines.append(f"{r.n:>3} {r.candidates:>11} {r.lower:>12} {r.upper:>12}   {verdict}")
    unresolved, near_one = result.exceptional()
    for v in unresolved:
        lines.append(f"phase unresolved:  {v.text}\n    log|z| = {v.L.real.str(20)}")
    for v in near_one:
        lines.append(f"within 1e-100 of 1:  {v.text}\n    |log z| = {abs(v.L).str(20)}")
    return "\n".join(lines)
