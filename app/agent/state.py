

from typing import TypedDict


class DataAgentState(TypedDict):
    query: str
    keywords: list[str]
    error: str
    sql: str