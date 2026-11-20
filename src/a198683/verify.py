"""Independent checks on the result a(12) = 2926. Takes about 90 seconds.

1  Published tables     our grouping of all 23,714 bracketings with n <= 11 must equal
                        Schoenfield's published grouping, bracketing by bracketing.
2  Brute force          all 58,786 bracketings at n = 12, one by one: equal normal forms
                        are provably equal, and different ones must have disjoint balls.
3  The 2017 obstacles   reproduce the failures reported when n = 12 was attempted with
                        ordinary arithmetic in 2017, then resolve them.
4  Branch boundary      wherever the phase is resolved it must be strictly inside
                        (-pi, pi); where it is not, the count must not depend on it.
5  Second library       a recount with mpmath, using no balls and no algebra.
"""

from dataclasses import dataclass, field

from flint import arb

from a198683 import mpmath_check, published
from a198683.bruteforce import evaluate_all, group_by_form

EXPECTED = 2926

# Ordinary multiprecision arithmetic stores a number as mantissa * 2^exponent with a bounded
# exponent. Assuming the bound was 2^30 in the software used in 2017 (an assumption, chosen
# because it reproduces the counts reported then), |z| overflows when log|z| exceeds this:
OVERFLOW_LOG = arb(2) ** 30 * arb(2).log()


@dataclass
class Check:
    name: str
    passed: bool
    lines: list = field(default_factory=list)


# ---------------------------------------------------------------- 1


def published_tables(all_values: dict) -> Check:
    lines, passed, total = [], True, 0
    for n, rows in sorted(published.tables().items()):
        ours = all_values[n]
        first_with_form, agree = {}, len(ours) == len(rows)
        for index, (v, (text, their_rep)) in enumerate(zip(ours, rows), start=1):
            our_rep = first_with_form.setdefault(v.key, index)
            agree = agree and v.text == text and our_rep == their_rep
        passed = passed and agree
        total += len(rows)
        lines.append(f"n = {n:>2}: {len(rows):>6} bracketings, {len(first_with_form):>5} values, "
                     f"grouping {'identical' if agree else 'DIFFERS'}")
    lines.append(f"{total} bracketings compared")
    return Check("Agreement with the published tables (n <= 11)", passed, lines)


# ---------------------------------------------------------------- 2


def brute_force(top: list) -> Check:
    groups = group_by_form(top)
    # Members of one normal form are provably equal, so their balls must all overlap.
    consistent = all(v.L.overlaps(members[0][1].L) for members in groups.values() for _, v in members)
    reps = [members[0][1] for members in groups.values()]
    overlapping = sum(
        reps[a].L.overlaps(reps[b].L) for a in range(len(reps)) for b in range(a + 1, len(reps))
    )
    lines = [
        f"{len(top)} bracketings fall into {len(groups)} normal forms (upper bound)",
        f"pairs of different normal forms with overlapping balls: {overlapping} "
        f"(0 means all are provably different: lower bound)",
    ]
    return Check("Brute force over every bracketing at n = 12",
                 consistent and overlapping == 0 and len(groups) == EXPECTED, lines)


# ---------------------------------------------------------------- 3


def _breaks(v, memo) -> str | None:
    """'over' if this value or any part of it overflows, 'under' if it underflows to zero."""
    if id(v) not in memo:
        if v.base is None:
            result = None
        elif _breaks(v.base, memo) == "over" or _breaks(v.exponent, memo) == "over" or not v.resolved:
            result = "over"
        elif v.L.real.lower() > OVERFLOW_LOG:
            result = "over"
        elif (-v.L.real).lower() > OVERFLOW_LOG:
            result = "under"
        else:
            result = None
        memo[id(v)] = result
    return memo[id(v)]


def obstacles_of_2017(all_values: dict) -> Check:
    """Schoenfield reported (history of the OEIS entry, Nov 2017): infinite or undefined results
    for 6 bracketings at n = 11 and 27 at n = 12, the 27 covering at most 5 values of unknown
    distinctness; and a result of zero for bracketings 5878 and 5892 at n = 12."""
    memo = {}
    over11 = sum(_breaks(v, memo) == "over" for v in all_values[11])
    over12 = [(i, v) for i, v in enumerate(all_values[12], start=1) if _breaks(v, memo) == "over"]
    under12 = [i for i, v in enumerate(all_values[12], start=1) if _breaks(v, memo) == "under"]
    forms = {}
    for i, v in over12:
        forms.setdefault(v.key, []).append((i, v))
    reps = [members[0][1] for members in forms.values()]
    distinct = all(not reps[a].L.overlaps(reps[b].L) for a in range(len(reps)) for b in range(a + 1, len(reps)))
    same = all_values[12][5877].key == all_values[12][5891].key
    lines = [
        f"bracketings that overflow: {over11} at n = 11 (reported: 6), {len(over12)} at n = 12 (reported: 27)",
        f"bracketings that underflow to zero at n = 12: {under12} (reported: 5878 and 5892)",
        f"the {len(over12)} overflowing bracketings take {len(forms)} normal forms (reported: at most 5):",
    ]
    for members in forms.values():
        i, v = members[0]
        angle = v.L.imag.str(8) if v.resolved else "unresolved"
        lines.append(f"  {len(members)} bracketings from #{i}: log|z| = {v.L.real.str(10)}, angle = {angle}")
    lines.append(f"those {len(forms)} values are {'all provably different' if distinct else 'NOT all separated'}")
    lines.append(f"#5878 and #5892 are {'proved equal' if same else 'NOT equal'}: "
                 f"log|z| = {all_values[12][5877].L.real.str(10)}")
    passed = (over11, len(over12), under12, len(forms), distinct, same) == (6, 27, [5878, 5892], 5, True, True)
    return Check("The obstacles reported in 2017, reproduced and resolved", passed, lines)


# ---------------------------------------------------------------- 4


def branch_boundary(all_values: dict) -> Check:
    pi = arb.pi()
    resolved, strict, unresolved = 0, True, []
    for n, values in all_values.items():
        for index, v in enumerate(values, start=1):
            if v.resolved:
                resolved += 1
                strict = strict and bool(v.L.imag < pi) and bool(v.L.imag > -pi)  # rigorous comparisons
            else:
                unresolved.append((n, index, v))
    bases = {v.base.key for _, _, v in unresolved}
    exponents = {v.exponent.key for _, _, v in unresolved}
    one_value = len(bases) == 1 and len(exponents) == 1
    special = unresolved[0][2].L.real
    others = {v.key: v for v in all_values[max(all_values)] if v.resolved}
    separated = all(not special.overlaps(v.L.real) for v in others.values())
    smallest = min(others.values(), key=lambda v: float(v.L.real.mid()))
    lines = [
        f"phase resolved: {resolved} bracketings, all strictly inside (-pi, pi): {strict}",
        f"phase unresolved: {len(unresolved)} bracketings, at n = {sorted({n for n, _, _ in unresolved})}, "
        f"indices {[i for _, i, _ in unresolved]}",
        f"their operands: {len(bases)} base normal form ({unresolved[0][2].base.text}), "
        f"{len(exponents)} exponent normal form, so {'provably one value' if one_value else 'NOT shown equal'}",
        f"its log|z| = {special.str(8)}",
        f"smallest log|z| among the other {len(others)} classes = {smallest.L.real.str(8)}",
        f"separated from all of them by magnitude alone: {separated}",
    ]
    passed = strict and one_value and separated and (resolved, len(unresolved)) == (82494, 6)
    return Check("Branch-boundary audit", passed, lines)


# ---------------------------------------------------------------- 5


def second_library() -> Check:
    counts = mpmath_check.count(12, digits=3000)
    return Check("Recount with mpmath at 3000 digits", counts[-1] == EXPECTED, [f"counts for n = 1..12: {counts}"])


# ---------------------------------------------------------------- all


def run_all(echo=print) -> list:
    echo("Evaluating every bracketing for n = 1..12 ...")
    all_values = evaluate_all(12)
    checks = []
    for make in (
        lambda: published_tables(all_values),
        lambda: brute_force(all_values[12]),
        lambda: obstacles_of_2017(all_values),
        lambda: branch_boundary(all_values),
        second_library,
    ):
        check = make()
        checks.append(check)
        echo(f"\n[{'PASS' if check.passed else 'FAIL'}] {check.name}")
        for line in check.lines:
            echo(f"  {line}")
    ok = all(c.passed for c in checks)
    echo(f"\nRESULT: {'all checks agree on a(12) = ' + str(EXPECTED) if ok else 'CHECKS DISAGREE'}")
    return checks
