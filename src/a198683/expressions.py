"""Text form of bracketings, in the layout used by the published OEIS tables.

A bracketing is written on one line with `^` for the power operation. A base or exponent
that is not a bare `i` is wrapped in brackets, so the text is unambiguous:

    i^(i^i)      i raised to (i^i)
    (i^i)^i      (i^i) raised to i
"""


def power_text(base: str, exponent: str) -> str:
    """Text for base^exponent, given the text of each part."""
    b = base if base == "i" else f"({base})"
    e = exponent if exponent == "i" else f"({exponent})"
    return f"{b}^{e}"

