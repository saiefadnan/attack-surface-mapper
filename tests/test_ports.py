"""Tests for asm.ports.parse_ports.

YOUR JOB: fill each test body. A test function runs its code and uses
`assert <condition>` — if the condition is False, pytest reports a failure.

Run all tests from the project root:
    pytest

Run just this file:
    pytest tests/test_ports.py
"""

from asm.ports import parse_ports, TOP_100


def test_csv_parsing():
    """A plain CSV spec returns those exact ports, sorted.

    Example: parse_ports("80,443,22") should give [22, 80, 443].
    TODO: assert that.
    """
    result = parse_ports("80,443,22")
    assert result == [22, 80, 443]


def test_range_parsing():
    """A range spec expands inclusively.

    Example: parse_ports("1-3") should give [1, 2, 3].
    TODO: assert that.
    """
    result = parse_ports("1-3")
    assert result == [1, 2, 3]


def test_csv_and_range_combined():
    """A spec mixing CSV and a range merges and sorts both.

    Example: parse_ports("80,443,1-3") -> [1, 2, 3, 80, 443].
    TODO: assert that.
    """
    result = parse_ports("80,443,1-3")
    assert result == [1, 2, 3, 80, 443]


def test_duplicates_removed():
    """Repeated ports collapse to one.

    Example: parse_ports("80,80,80") -> [80].
    TODO: assert that.
    """
    result = parse_ports("80,80,80")
    assert result == [80]


def test_out_of_range_dropped():
    """Ports outside 1..65535 are discarded, valid ones kept.

    Example: parse_ports("0,70000,22") -> [22].
    TODO: assert that.
    """
    result = parse_ports("0,70000,22")
    assert result == [22]


def test_top100_preset():
    """The "top100" keyword returns the TOP_100 list (100 ports).

    TODO: assert len(parse_ports("top100")) == 100, and that it equals
    sorted(TOP_100) (parse_ports sorts its output).
    """
    result = parse_ports("top100")
    assert len(result)==100 and result==sorted(TOP_100)
