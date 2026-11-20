"""Recount with a different arithmetic library and no algebra: mpmath floats only.

This is a cross-check, not a proof. Values are compared through the leading 60 digits of
their principal logarithms, computed with far more digits than that. It shares no code
with the main computation beyond the recurrence itself.
"""

from mpmath import mp, mpc, mpf


def count(n_max: int = 12, digits: int = 3000) -> list:
    """Number of distinct values for n = 1..n_max."""
    mp.dps = digits
    eps = mpf(10) ** -(digits * 5 // 6)  # relative size below which a number is rounding error
    two_pi = 2 * mp.pi

    def fingerprint(L):
        return (mp.nstr(L.real, 60), mp.nstr(L.imag, 60))

    L_i = mpc(0, mp.pi / 2)
    classes = {1: {fingerprint(L_i): L_i}}
    counts = [1]
    for n in range(2, n_max + 1):
        found, unresolved = {}, set()
        for size_a in range(1, n):
            for La in classes[size_a].values():
                for Lb in classes[n - size_a].values():
                    w = mp.exp(Lb) * La
                    noise = abs(w) * eps
                    if abs(w.imag) * eps > 1:
                        # Imaginary part too large to reduce modulo 2*pi: only the size is known.
                        unresolved.add(mp.nstr(w.real, 60))
                        continue
                    re, im = w.real, w.imag
                    im -= two_pi * mp.floor((im + mp.pi) / two_pi)
                    if abs(im + mp.pi) < noise:
                        im = +mp.pi
                    re = mpf(0) if abs(re) < noise else re
                    im = mpf(0) if abs(im) < noise else im
                    L = mpc(re, im)
                    found[fingerprint(L)] = L
        classes[n] = found
        counts.append(len(found) + len(unresolved))
    return counts
