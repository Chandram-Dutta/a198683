"""The smallest possible check: nothing but Python's built-in complex numbers.

No libraries, no logarithm trick, no algebra. Short enough to read in a minute. It builds
every bracketing of n copies of i, computes each with Python's own `**` (which uses the
principal value), and counts how many different numbers come out.

Ordinary floats have about 16 digits and overflow near 10^308, so this stops being
trustworthy around n = 10. It exists to confirm the definition and the first terms
without relying on any other code in this repository.
"""

I = 1j  # Python's name for the square root of -1

KNOWN = [1, 1, 2, 3, 7, 15, 34, 77, 187]  # a(1)..a(9), as listed in the OEIS


def all_values(n: int, memo={1: [I]}) -> list:
    """The value of every bracketing of n copies of i (with repeats)."""
    if n not in memo:
        memo[n] = [a**b for k in range(1, n) for a in all_values(k) for b in all_values(n - k)]
    return memo[n]


def fingerprint(z: complex):
    """Size to 9 significant digits plus direction to 9 decimals: equal numbers share one."""
    size = abs(z)
    return (f"{size:.8e}", round(z.real / size, 9) + 0.0, round(z.imag / size, 9) + 0.0)


def count(n: int) -> int:
    return len({fingerprint(z) for z in all_values(n)})


if __name__ == "__main__":
    for n, expected in enumerate(KNOWN, start=1):
        print(f"n = {n}: {len(all_values(n)):>5} bracketings, {count(n):>4} distinct values  (OEIS: {expected})")
