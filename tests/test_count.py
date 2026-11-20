"""Fast tests: the main computation and its building blocks."""

import pytest

from a198683 import count, mpmath_check, normal_form, tiny
from a198683.core import power, unit_i
from a198683.expressions import power_text

OEIS_TERMS = [1, 1, 2, 3, 7, 15, 34, 77, 187, 462, 1152]  # a(1)..a(11) as listed in the OEIS


@pytest.fixture(scope="module")
def result():
    return count.bounds(12)


def test_bounds_meet_and_match_the_oeis(result):
    for row, known in zip(result.rows, OEIS_TERMS):
        assert row.lower == row.upper == known
    assert all(row.exact for row in result.rows)


def test_a12(result):
    row = result.rows[-1]
    assert (row.n, row.candidates, row.lower, row.upper, row.exact) == (12, 5139, 2926, 2926, True)


def test_exceptional_values_at_n12(result):
    unresolved, near_one = result.exceptional()
    assert len(unresolved) == 1  # the single value whose phase cannot be computed
    assert len(near_one) == 2  # the two values a low-precision method merges with 1


def test_n13_is_refused():
    with pytest.raises(ValueError):
        count.bounds(13)


def test_small_cases_by_hand():
    i = unit_i()
    i_i = power(i, i)  # i^i = exp(-pi/2), a real number
    assert i_i.L.imag.contains(0) and abs(float(i_i.L.real.mid()) + 1.5707963267948966) < 1e-12
    # (i^i)^i = -i, whose principal log is -i*pi/2, i.e. P = -1
    assert power(i_i, i).P == {(): (-1, 0)}
    # the two coincidences among the five bracketings of four copies
    assert power(i_i, i_i).key == power(power(i, i_i), i).key
    assert power(i, power(i_i, i)).key == power(power(i_i, i), i).key
    assert power(i_i, i_i).key != power(i, power(i_i, i)).key


def test_value_form_of_a_constant_is_a_power_of_i():
    assert normal_form.value_of({(): (3, 0)}) == (3, ())
    assert normal_form.value_of({(): (-1, 0)}) == (3, ())  # i^-1 = i^3


def test_expression_text():
    assert power_text("i", "i") == "i^i"
    assert power_text("i^i", "i") == "(i^i)^i"
    assert power_text("i", "i^i") == "i^(i^i)"


def test_plain_python_check():
    assert [tiny.count(n) for n in range(1, 10)] == tiny.KNOWN


def test_second_library_for_small_n():
    assert mpmath_check.count(10, digits=600) == OEIS_TERMS[:10]
