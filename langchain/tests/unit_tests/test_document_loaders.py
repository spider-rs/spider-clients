from __future__ import annotations

import pytest

from langchain_spider import SpiderAPIError, SpiderLoader

from .conftest import Recorder, reply


def test_scrape_posts_markdown_without_key() -> None:
    rec = Recorder(
        reply(
            [
                {
                    "url": "https://example.com",
                    "content": "# Example",
                    "status": 200,
                    "metadata": {"title": "Example Domain"},
                }
            ]
        )
    )
    docs = SpiderLoader("https://example.com", client=rec.client()).load()

    req = rec.requests[0]
    assert str(req.url) == "https://api.spider.cloud/scrape"
    assert req.method == "POST"
    assert "authorization" not in req.headers
    assert req.headers["user-agent"].startswith("langchain-spider/")
    assert rec.body() == {
        "return_format": "markdown",
        "metadata": True,
        "url": "https://example.com",
    }
    assert len(docs) == 1
    assert docs[0].page_content == "# Example"
    assert docs[0].metadata == {
        "title": "Example Domain",
        "source": "https://example.com",
        "status": 200,
    }


def test_key_from_env_is_sent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPIDER_API_KEY", "test-key")
    rec = Recorder(reply([{"url": "https://example.com", "content": "x", "status": 200}]))
    SpiderLoader("https://example.com", client=rec.client()).load()
    assert rec.requests[0].headers["authorization"] == "Bearer test-key"


def test_crawl_yields_one_document_per_page_and_skips_empty() -> None:
    rec = Recorder(
        reply(
            [
                {"url": "https://example.com", "content": "home", "status": 200},
                {"url": "https://example.com/a", "content": None, "status": 404},
                {"url": "https://example.com/b", "content": "b", "status": 200},
            ]
        )
    )
    loader = SpiderLoader(
        "https://example.com",
        api_key="k",
        mode="crawl",
        params={"limit": 3, "return_format": "text"},
        client=rec.client(),
    )
    docs = list(loader.lazy_load())
    assert str(rec.requests[0].url) == "https://api.spider.cloud/crawl"
    assert rec.body() == {"limit": 3, "return_format": "text", "url": "https://example.com"}
    assert [d.metadata["source"] for d in docs] == [
        "https://example.com",
        "https://example.com/b",
    ]


def test_crawl_needs_a_key() -> None:
    rec = Recorder(reply([]))
    with pytest.raises(ValueError, match="needs an API key"):
        SpiderLoader("https://example.com", mode="crawl", client=rec.client()).load()
    assert rec.requests == []


def test_bad_mode() -> None:
    with pytest.raises(ValueError, match="Unrecognized mode"):
        SpiderLoader("https://example.com", mode="map")  # type: ignore[arg-type]


def test_api_error_carries_retry_after() -> None:
    rec = Recorder(reply({"error": "slow down"}, 429, {"Retry-After": "7"}))
    with pytest.raises(SpiderAPIError) as info:
        SpiderLoader("https://example.com", client=rec.client()).load()
    assert info.value.status_code == 429
    assert info.value.retry_after == 7
    assert "Retry after 7s" in str(info.value)


def test_402_points_to_key_page() -> None:
    rec = Recorder(reply({"error": "empty balance", "code": "credits_required"}, 402))
    with pytest.raises(SpiderAPIError, match="spider.cloud/api-keys"):
        SpiderLoader("https://example.com", api_key="k", client=rec.client()).load()


async def test_async_load() -> None:
    rec = Recorder(reply([{"url": "https://example.com", "content": "async", "status": 200}]))
    loader = SpiderLoader(
        "https://example.com",
        base_url="https://proxy.test/",
        async_client=rec.async_client(),
    )
    docs = [d async for d in loader.alazy_load()]
    assert str(rec.requests[0].url) == "https://proxy.test/scrape"
    assert docs[0].page_content == "async"
