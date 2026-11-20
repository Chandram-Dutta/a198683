"""Distinct values of power towers of i over all bracketings (OEIS A198683).

    count          the main computation: matching lower and upper bounds for a(1)..a(12)
    core           values tracked through ball enclosures of their principal logarithms
    normal_form    exact algebra that proves values equal
    bruteforce     every bracketing evaluated individually
    verify         independent checks on the result
    table          the full n = 12 table, in the layout of the published tables
    published      access to the published tables for n <= 11
    mpmath_check   recount with a second arithmetic library
    tiny           check of the first terms with plain Python complex numbers
"""
