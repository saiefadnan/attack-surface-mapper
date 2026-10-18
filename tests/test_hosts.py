"""Tests for asm.hosts._extract_title.

YOUR JOB: fill each test body with an assert.

Run:
    pytest tests/test_hosts.py
"""

from asm.hosts import _extract_title


def test_simple_title():
    """A normal title is returned, trimmed.

    Example: _extract_title("<title> Hello World </title>") -> "Hello World".
    TODO: assert that.
    """
    title = _extract_title("<title> Hello World </title>")
    assert title == "Hello World"


def test_whitespace_collapsed():
    """Inner runs of whitespace and newlines collapse to single spaces.

    Example: _extract_title("<title>\\n  Multi   Line\\n</title>")
             -> "Multi Line".
    TODO: assert that.
    """
    title = _extract_title("<title>\n Multi   Line \n</title>")
    assert title == "Multi Line"


def test_no_title_returns_none():
    """HTML with no <title> tag returns None.

    Example: _extract_title("<p>nothing here</p>") -> None.
    TODO: assert that.
    """
    title = _extract_title("<p>nothing here</p>")
    assert title is None


def test_empty_title_returns_none():
    """A title holding only whitespace returns None, not "".

    Example: _extract_title("<title>   </title>") -> None.
    TODO: assert that.
    """
    result = _extract_title("<title>   </title>")
    assert result is None
