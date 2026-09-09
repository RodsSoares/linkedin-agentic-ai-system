import pytest

from app.tools.brave_search import brave_search
from app.tools.http_reader import http_reader
from app.tools.web_reader import web_reader
from app.tools.web_search import web_search
from app.tools.web_tools import get_web_tools
from app.tools.brave_search import brave_search
from app.tools.http_reader import http_reader
from app.tools.web_reader import web_reader
from app.tools.web_search import web_search
from app.tools.web_tools import get_web_tools


def test_get_web_tools_selects_fake_implementations():
    search_tool, read_tool = get_web_tools("fake")

    assert search_tool is web_search
    assert read_tool is web_reader


def test_get_web_tools_selects_real_implementations():
    search_tool, read_tool = get_web_tools("real")

    assert search_tool is brave_search
    assert read_tool is http_reader


def test_get_web_tools_normalizes_mode():
    search_tool, read_tool = get_web_tools("  REAL  ")

    assert search_tool is brave_search
    assert read_tool is http_reader


def test_get_web_tools_rejects_invalid_mode():
    with pytest.raises(
        ValueError,
        match="either 'fake' or 'real'",
    ):
        get_web_tools("unknown")
        