from collections.abc import Callable

from app.config.settings import WEB_TOOL_MODE
from app.schemas.tools import ReadTool, SearchTool
from app.tools.brave_search import brave_search
from app.tools.http_reader import http_reader
from app.tools.web_reader import web_reader
from app.tools.web_search import web_search


def get_web_tools(
    mode: str | None = None,
) -> tuple[SearchTool, ReadTool]:
    selected_mode = WEB_TOOL_MODE if mode is None else mode.strip().lower()

    if selected_mode == "fake":
        return web_search, web_reader

    if selected_mode == "real":
        return brave_search, http_reader

    raise ValueError(
        "Web tool mode must be either 'fake' or 'real'."
    )
