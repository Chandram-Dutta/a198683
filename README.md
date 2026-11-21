# a198683

A computer-assisted determination of the twelfth term of [OEIS A198683](https://oeis.org/A198683): **a(12) = 2926**.

> **Status.** This term is not yet in the OEIS entry. The code was written with an AI model (see [How this was made](#how-this-was-made)). Treat the result as a claim with a reproducible argument attached, and please try to break it.

## The sequence

Let *i* be the square root of −1, and define powers of complex numbers by the principal value: *a^b* = exp(*b* · Log *a*), where the imaginary part of Log *a* lies in (−π, π].

Take *n* copies of *i* and combine them with `^`, bracketed in every possible way. For example, with three copies there are two bracketings, `i^(i^i)` and `(i^i)^i`, and they give different values. **a(n) is the number of distinct values.**

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a(n) | 1 | 1 | 2 | 3 | 7 | 15 | 34 | 77 | 187 | 462 | 1152 | **2926** |

The OEIS entry lists the terms through a(11) and records a(12) as "said to be either 2919 or 2926", unconfirmed. This repository reproduces the eleven listed terms and determines the twelfth.

## Why it was open

The numbers defeat ordinary arithmetic. With 10 copies, one bracketing is about −6.8 × 10³⁴ − 6.0 × 10³⁴ *i*; raising *i* to that gives a number of size *e*^(10³⁵); raising *i* to *that* gives a number no floating-point format can hold.

In 2017 Jon E. Schoenfield published [tables](https://oeis.org/A198683/a198683.txt) settling every bracketing up to n = 11, and described in the [entry's history](https://oeis.org/history?seq=A198683) what stopped him at n = 12: 27 bracketings evaluated to infinite or undefined results (covering at most five values, of unknown distinctness), two evaluated to zero although their true values are non-zero, and rounding error could not be ruled out.

## Method

1. **Track logarithms, not values.** Each value *z* is stored as its principal logarithm *L*. Two values are equal exactly when their principal logarithms are equal, and *L*(*a^b*) is obtained from exp(*L*(*b*)) · *L*(*a*) by removing whole turns of 2π*i*. A value of size *e*^(10³⁵) has a logarithm of size 10³⁵, which is easy to hold.
2. **Lower bound, by ball arithmetic.** Each logarithm is enclosed in a ball (midpoint and radius) by [Arb](https://arblib.org), which guarantees the true number lies inside. Values whose balls do not overlap are provably different.
3. **Upper bound, by exact algebra.** Writing *L* = (*i*π/2) · *P*, the quantity *P* obeys *P*(*a^b*) = *Z*(*b*) · *P*(*a*) − 4*k*, with *Z*(*b*) the value of *b* and *k* an integer certified by step 2. *P* is kept as an exact polynomial in formal symbols. Bracketings with identical polynomials are provably equal.

At n = 12 the two bounds are both 2926.

**One exceptional value.** Six bracketings at n = 12 share a value whose phase cannot be computed (it would need about 10³⁵ bits). The count does not depend on it: the six have provably equal operands, so they are one value whatever its phase, and its magnitude (log|z| ≈ −3.2 × 10^(4.1 × 10³⁴)) separates it from every other value.

The modules [`normal_form.py`](src/a198683/normal_form.py) and [`core.py`](src/a198683/core.py) contain the full argument in their docstrings.

## Run it

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run a198683 count      # both bounds for a(1)..a(12), about 2 seconds
uv run a198683 verify     # every independent check, about 90 seconds
uv run a198683 table      # regenerate tables/a198683_n12.txt
uv run a198683 tiny       # a(1)..a(9) with plain Python complex numbers
uv run pytest             # fast tests; add `-m slow` for the full suite
```

`--bits N` before the command changes the working precision (default 3000 bits).

## Checks

`a198683 verify` runs five checks, all of which pass:

1. **Published tables.** For all 23,714 bracketings with n ≤ 11, the grouping into equal values is identical to Schoenfield's, bracketing by bracketing.
2. **Brute force.** All 58,786 bracketings at n = 12 are evaluated individually. They fall into 2926 exact normal forms, whose balls are pairwise disjoint.
3. **The 2017 obstacles.** Assuming the software used in 2017 had a binary exponent bound of 2³⁰ (an assumption, chosen because it reproduces the reported counts), exactly 6 bracketings overflow at n = 11 and 27 at n = 12, and exactly bracketings 5878 and 5892 underflow. The 27 take five values, which are shown to be pairwise different; 5878 and 5892 are shown to be equal.
4. **Branch boundary.** For the 82,494 bracketings whose phase is resolved, it lies strictly inside (−π, π). The remaining six are the exceptional ones above.
5. **Second library.** A recount with mpmath at 3000 digits, with no balls and no algebra, gives 2926.

## How to refute it

[`tables/a198683_n12.txt`](tables/a198683_n12.txt) lists all 58,786 bracketings of twelve copies in the order and layout of the published tables. Each line says either that the value is new or which earlier line it equals. **One wrong line refutes the result**: a pair marked equal that differs, or a pair marked different that is equal. As a check on the layout, the same code regenerates the published n = 11 table character for character.

## What this does not establish

- **Independence of the checks.** The checks were written alongside the main computation. A reasoning error shared by all of them would not be caught.
- **Trust in software.** The lower bound relies on Arb being correct, and the upper bound on the normal-form code being correct. Nothing is formalised in a proof assistant.
- **No exhaustive literature search.** The OEIS entry, its edit history, the linked MathOverflow thread and a web search turned up no earlier determination of a(12). That is not proof that none exists.
- **n = 13.** The method stops at 12: the exceptional value would be reused as a base and an exponent, and its phase is not available.

## How this was made

The method and the code in `src/` were developed by Chandram Dutta working with Claude, an AI model made by Anthropic, in November 2026.

## Layout

```
src/a198683/
  count.py         main computation: lower and upper bounds for a(1)..a(12)
  core.py          values as ball enclosures of principal logarithms
  normal_form.py   exact algebra that proves values equal
  expressions.py   text form of bracketings
  bruteforce.py    every bracketing evaluated individually
  verify.py        the five checks
  table.py         writes the n = 12 table
  published.py     downloads and reads the published tables for n <= 11
  mpmath_check.py  recount with a second arithmetic library
  tiny.py          first terms with plain Python complex numbers
  cli.py           command line
tests/             fast tests, and the slow suite (`pytest -m slow`)
tables/            the full n = 12 table
```

## References

- OEIS Foundation Inc., [Entry A198683](https://oeis.org/A198683) in The On-Line Encyclopedia of Integer Sequences.
- J. E. Schoenfield, [Tables for n = 1..11](https://oeis.org/A198683/a198683.txt), a-file for A198683, 2017. Downloaded on first use; not redistributed here.
- F. Johansson, "Arb: efficient arbitrary-precision midpoint-radius interval arithmetic", IEEE Transactions on Computers 66 (8), 2017, 1281–1292.

## Licence

MIT. See [LICENSE](LICENSE).
