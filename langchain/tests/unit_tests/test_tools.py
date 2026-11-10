from __future__ import annotations

import pytest
from langchain_core.messages import ToolMessage
from langchain_core.tools import ToolException

from langchain_spider import SpiderAPIError, SpiderScrapeTool, SpiderSearchTool, SpiderToolkit

from .conftest import Recorder, reply


def test_scrape_tool_returns_content() -> None:
    rec = Recorder(reply([{"url": "https://example.com", "content": "# Example", "status": 200}]))
    tool = SpiderScrapeTool(client=rec.client())
    out = tool.invoke({"url": "https://example.com"})
    assert out == "# Example"
    assert str(rec.requests[0].url) == "https://api.spider.cloud/scrape"
    assert "authorization" not in rec.requests[0].headers
    assert rec.body() == {"return_format": "markdown", "url": "https://example.com"}


def test_scrape_tool_model_args_override_params() -> None:
    rec = Recorder(reply([{"url": "https://example.com", "content": "abcdef", "status": 200}]))
    tool = SpiderScrapeTool(
        api_key="k",
        params={"return_format": "text", "readability": True},
        max_content_chars=3,
        client=rec.client(),
    )
    out = tool.invoke({"url": "https://example.com", "return_format": "raw", "request": "browser"})
    assert out == "abc"
    assert rec.requests[0].headers["authorization"] == "Bearer k"
    assert rec.body() == {
        "return_format": "raw",
        "readability": True,
        "url": "https://example.com",
        "request": "browser",
    }


def test_scrape_tool_reports_missing_content() -> None:
    rec = Recorder(reply([{"url": "https://example.com", "content": None, "error": "blocked"}]))
    out = SpiderScrapeTool(client=rec.client()).invoke({"url": "https://example.com"})
    assert out == "No content returned for https://example.com. Error: blocked"


def test_search_tool_maps_query_and_results() -> None:
    rec = Recorder(
        reply(
            {
                "content": [
                    {
                        "title": "spider-rs/spider",
                        "description": "A web crawler.",
                        "url": "https://github.com/spider-rs/spider",
                    }
                ]
            }
        )
    )
    tool = SpiderSearchTool(api_key="k", client=rec.client())
    out = tool.invoke({"query": "rust web crawler", "search_limit": 3, "tbs": "qdr:w"})
    assert str(rec.requests[0].url) == "https://api.spider.cloud/search"
    assert rec.body() == {"search_limit": 3, "tbs": "qdr:w", "search": "rust web crawler"}
    assert out == [
        {
            "title": "spider-rs/spider",
            "description": "A web crawler.",
            "url": "https://github.com/spider-rs/spider",
        }
    ]


def test_search_tool_with_page_content() -> None:
    rec = Recorder(
        reply(
            [
                {
                    "url": "https://a.test",
                    "content": "# A",
                    "status": 200,
                    "metadata": {"title": "A"},
                }
            ]
        )
    )
    tool = SpiderSearchTool(api_key="k", client=rec.client())
    out = tool.invoke({"query": "a", "fetch_page_content": True})
    assert rec.body() == {
        "search_limit": 5,
        "return_format": "markdown",
        "fetch_page_content": True,
        "search": "a",
    }
    assert out == [{"url": "https://a.test", "title": "A", "content": "# A"}]


def test_search_without_key_returns_error_to_model() -> None:
    rec = Recorder(reply([]))
    out = SpiderSearchTool(client=rec.client()).invoke({"query": "x"})
    assert "needs an API key" in out
    assert rec.requests == []


def test_search_without_key_raises_when_errors_not_handled() -> None:
    tool = SpiderSearchTool(handle_tool_error=False)
    with pytest.raises(ToolException) as info:
        tool.invoke({"query": "x"})
    assert isinstance(info.value.__cause__, ValueError)


def test_api_error_as_tool_message() -> None:
    rec = Recorder(reply({"error": "slow down"}, 429, {"Retry-After": "2"}))
    tool = SpiderScrapeTool(client=rec.client())
    msg = tool.invoke(
        {
            "name": "spider_scrape",
            "args": {"url": "https://example.com"},
            "id": "call-1",
            "type": "tool_call",
        }
    )
    assert isinstance(msg, ToolMessage)
    assert msg.status == "error"
    assert "429" in msg.content and "Retry after 2s" in msg.content


def test_api_error_cause_is_kept() -> None:
    rec = Recorder(reply({"error": "nope"}, 500))
    tool = SpiderScrapeTool(client=rec.client(), handle_tool_error=False)
    with pytest.raises(ToolException) as info:
        tool.invoke({"url": "https://example.com"})
    assert isinstance(info.value.__cause__, SpiderAPIError)
    assert info.value.__cause__.status_code == 500


def test_search_limit_is_validated() -> None:
    tool = SpiderSearchTool(api_key="k")
    schema = tool.get_input_schema()
    with pytest.raises(ValueError):
        schema(query="x", search_limit=0)


def test_api_key_is_secret() -> None:
    tool = SpiderSearchTool(api_key="secret-value")
    assert "secret-value" not in repr(tool)
    assert "secret-value" not in str(tool.model_dump())


async def test_async_tools() -> None:
    rec = Recorder(reply([{"url": "https://example.com", "content": "async", "status": 200}]))
    tool = SpiderScrapeTool(async_client=rec.async_client())
    assert await tool.ainvoke({"url": "https://example.com"}) == "async"

    rec2 = Recorder(reply({"content": [{"title": "t", "description": "d", "url": "u"}]}))
    search = SpiderSearchTool(api_key="k", async_client=rec2.async_client())
    assert await search.ainvoke({"query": "q"}) == [{"title": "t", "description": "d", "url": "u"}]


def test_toolkit_shares_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPIDER_API_KEY", "env-key")
    rec = Recorder(reply({"content": []}))
    tools = SpiderToolkit(client=rec.client(), max_content_chars=10).get_tools()
    assert [t.name for t in tools] == ["spider_search", "spider_scrape"]
    assert all(t.max_content_chars == 10 for t in tools)
    tools[0].invoke({"query": "q"})
    assert rec.requests[0].headers["authorization"] == "Bearer env-key"
