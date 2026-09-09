from collections.abc import Callable

from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


SearchTool = Callable[[str], list[SearchResult]]
ReadTool = Callable[[str], str]
