"""Exact normal forms: the part of the argument that proves two values are EQUAL.

Write the principal logarithm of a value as L = (i*pi/2) * P. For powers of i,

    P(i) = 1,        P(a^b) = Z(b) * P(a) - 4k,

where Z(b) is the value of b and k is the integer number of full turns removed by the
principal branch. Nothing here is rounded: P is a polynomial with Gaussian-integer
coefficients in formal symbols ("atoms"), allowing negative exponents.

Atoms. For a monomial M (a product of atoms), define two symbols standing for the numbers

    A_M = exp( i*pi/2 * M),        B_M = exp(-pi/2 * M) = exp(i*pi/2 * i*M).

Since exp turns sums into products, a value whose P is  sum_j c_j M_j  equals

    product_j  A_{M_j}^Re(c_j) * B_{M_j}^Im(c_j),        with A_1 = i,

which is a power of i times a single monomial. Every rewrite used is a true identity of
complex numbers, so IDENTICAL NORMAL FORMS IMPLY EQUAL VALUES. The converse is not
claimed and is not needed: distinctness is established separately, numerically, with
rigorous error bounds (see core.py and count.py).

Representation
    monomial    tuple of (atom id, exponent) pairs, sorted, exponents non-zero; () is 1
    polynomial  dict {monomial: (re, im)} with integer re, im, never both zero
    value       (power of i modulo 4, monomial)
"""

Monomial = tuple
Polynomial = dict
ValueForm = tuple

# Each distinct atom gets a small integer id. Two atoms are the same symbol exactly when
# they have the same kind ("A" or "B") and the same monomial.
_ATOM_IDS: dict = {}

ONE: Polynomial = {(): (1, 0)}  # P(i) = 1

_POWERS_OF_I = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def _atom(kind: str, monomial: Monomial) -> int:
    return _ATOM_IDS.setdefault((kind, monomial), len(_ATOM_IDS))


def _monomial_product(m1: Monomial, m2: Monomial) -> Monomial:
    exponents = dict(m1)
    for atom_id, e in m2:
        exponents[atom_id] = exponents.get(atom_id, 0) + e
    return tuple(sorted((a, e) for a, e in exponents.items() if e))


def value_of(P: Polynomial) -> ValueForm:
    """The value exp(i*pi/2 * P), as (power of i, monomial)."""
    i_power, exponents = 0, {}
    for monomial, (re, im) in P.items():
        if monomial == ():
            i_power += re  # A_1 = exp(i*pi/2) = i
        elif re:
            exponents[_atom("A", monomial)] = re
        if im:
            exponents[_atom("B", monomial)] = im
    return i_power % 4, tuple(sorted(exponents.items()))


def power(P_base: Polynomial, Z_exponent: ValueForm, k: int) -> Polynomial:
    """P(a^b) = Z(b) * P(a) - 4k."""
    i_power, monomial = Z_exponent
    ur, ui = _POWERS_OF_I[i_power]
    out = {}
    for m, (re, im) in P_base.items():
        out[_monomial_product(m, monomial)] = (re * ur - im * ui, re * ui + im * ur)
    if k:
        re, im = out.get((), (0, 0))
        out[()] = (re - 4 * k, im)
    return {m: c for m, c in out.items() if c != (0, 0)}


def key(P: Polynomial):
    """A hashable form of P. Equal keys mean identical polynomials."""
    return frozenset(P.items())
