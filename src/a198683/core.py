"""Values of power towers of i, tracked through their principal logarithms.

A value z is never stored directly, because it can be as large as exp(10^35). Instead we
store its principal logarithm L, with z = exp(L) and -pi < Im L <= pi. Two values are
equal exactly when their principal logarithms are equal, and

    L(i) = i*pi/2,        L(a^b) = reduce( exp(L(b)) * L(a) ),

where reduce() subtracts the multiple of 2*pi*i that brings the imaginary part back into
(-pi, pi].

Each L is held as a ball: a midpoint and a radius, computed by Arb so that the true
number is guaranteed to lie inside. Two values whose balls do not overlap are therefore
PROVABLY DIFFERENT. Alongside the ball, each value carries its exact normal form (see
normal_form.py), which is what proves values equal.
"""

from flint import acb, arb, ctx

from a198683 import normal_form
from a198683.expressions import power_text

DEFAULT_PRECISION_BITS = 3000  # about 900 decimal digits


def set_precision(bits: int) -> None:
    """Set the working precision of all ball arithmetic."""
    ctx.prec = bits


set_precision(DEFAULT_PRECISION_BITS)


class Value:
    """The value of one bracketing (or of a class of bracketings with the same value).

    text       the bracketing, e.g. "(i^i)^i"
    L          ball containing the principal logarithm
    resolved   whether the number of turns removed by reduce() was determined. If not,
               only the real part of L (the log of the size of the value) is meaningful.
    key        exact normal form; equal keys imply equal values
    P          polynomial with L = (i*pi/2) * P, or None when not resolved
    base, exponent   the two parts this value was built from (None for i itself)
    """

    __slots__ = ("text", "L", "resolved", "key", "P", "base", "exponent", "_exp", "_form")

    def __init__(self, text, L, resolved, key, P, base=None, exponent=None):
        self.text, self.L, self.resolved, self.key, self.P = text, L, resolved, key, P
        self.base, self.exponent = base, exponent
        self._exp = self._form = None

    def exp(self) -> acb:
        """Ball containing the value itself, exp(L)."""
        if self._exp is None:
            self._exp = self.L.exp()
        return self._exp

    def form(self):
        """Exact normal form of the value itself (not of its logarithm)."""
        if self._form is None:
            self._form = normal_form.value_of(self.P)
        return self._form


def unit_i() -> Value:
    """The single tower of height one: i itself."""
    return Value("i", acb(0, arb.pi() / 2), True, normal_form.key(normal_form.ONE), normal_form.ONE)


def reduce_to_principal(w: acb):
    """Bring Im w into (-pi, pi]. Returns (L, k), or (L, None) if k cannot be determined.

    k is accepted only when the ball for (Im w + pi) / (2*pi) has a unique floor. Then the
    ball for Im L lies strictly inside (-pi, pi), so the branch boundary is excluded.
    Otherwise the imaginary part is returned as the whole interval [-pi, pi].
    """
    pi = arb.pi()
    k = ((w.imag + pi) / (2 * pi)).floor().unique_fmpz()
    if k is None:
        return acb(w.real, arb(0, 3.1416)), None
    return acb(w.real, w.imag - 2 * pi * k), int(k)


def power(a: Value, b: Value) -> Value:
    """The value a^b."""
    if not (a.resolved and b.resolved):
        raise NotImplementedError(
            "a value whose phase is unresolved cannot be used as a base or an exponent; "
            "this is what currently stops the method at n = 12"
        )
    L, k = reduce_to_principal(b.exp() * a.L)
    text = power_text(a.text, b.text)
    if k is None:
        # The phase is unknown, so no normal form for L. The value is still a function of
        # the values of a and b, so equal (a, b) normal forms imply equal values.
        return Value(text, L, False, ("unresolved", a.key, b.form()), None, a, b)
    P = normal_form.power(a.P, b.form(), k)
    return Value(text, L, True, normal_form.key(P), P, a, b)


def overlap_groups(values: list) -> list:
    """Partition values into groups connected by overlapping balls.

    Values in different groups have disjoint balls, hence are provably different.
    """
    parent = list(range(len(values)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a in range(len(values)):
        La = values[a].L
        for b in range(a + 1, len(values)):
            if La.overlaps(values[b].L):
                parent[find(a)] = find(b)
    groups = {}
    for a in range(len(values)):
        groups.setdefault(find(a), []).append(values[a])
    return list(groups.values())
