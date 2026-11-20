"""The full verification suite. Slow (about 90 seconds): run with `pytest -m slow`."""

import pytest

from a198683 import published, table, verify
from a198683.bruteforce import evaluate_all


@pytest.fixture(scope="module")
def all_values():
    return evaluate_all(12)


@pytest.mark.slow
def test_published_tables(all_values):
    assert verify.published_tables(all_values).passed


@pytest.mark.slow
def test_brute_force(all_values):
    assert verify.brute_force(all_values[12]).passed


@pytest.mark.slow
def test_obstacles_of_2017(all_values):
    assert verify.obstacles_of_2017(all_values).passed


@pytest.mark.slow
def test_branch_boundary(all_values):
    assert verify.branch_boundary(all_values).passed


@pytest.mark.slow
def test_second_library():
    assert verify.second_library().passed


@pytest.mark.slow
def test_committed_table_is_current(all_values):
    assert table.table_lines(11, all_values[11]) == published.section(11)
    committed = table.DEFAULT_OUT.read_text().splitlines()
    assert table.table_lines(12, all_values[12]) == committed
