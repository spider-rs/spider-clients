"""Spider document loader."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal, Optional

import httpx
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_spider._client import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    apost,
    as_pages,
    post,
    resolve_api_key,
)

DEFAULT_PARAMS: dict[str, Any] = {"return_format": "markdown", "metadata": True}


class SpiderLoader(BaseLoader):
    """Load web pages as Documents with the Spider API.

    ``scrape`` mode loads one page. ``crawl`` mode follows links from the start
    URL and loads one Document per page.

    Setup:
        .. code-block:: bash

            pip install -U langchain-spider
            export SPIDER_API_KEY="your-key"

    Instantiate:
        .. code-block:: python

            from langchain_spider import SpiderLoader

            loader = SpiderLoader(
                url="https://spider.cloud",
                mode="crawl",
                params={"limit": 5},
            )

    Lazy load:
        .. code-block:: python

            for doc in loader.lazy_load():
                print(doc.metadata["source"], len(doc.page_content))

    Async load:
        .. code-block:: python

            docs = [doc async for doc in loader.alazy_load()]

    ``scrape`` works without a key on a rate limited keyless tier. ``crawl``
    needs a key.
    """

    def __init__(
        self,
        url: str,
        *,
        api_key: Optional[str] = None,
        mode: Literal["scrape", "crawl"] = "scrape",
        params: Optional[dict[str, Any]] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        client: Optional[httpx.Client] = None,
        async_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Create the loader.

        Args:
            url: The page to scrape, or the start URL of the crawl.
            api_key: Spider API key. Defaults to the ``SPIDER_API_KEY`` env var.
            mode: ``scrape`` for one page, ``crawl`` to follow links.
            params: Spider request fields, such as ``limit``, ``depth`` or
                ``return_format``. Defaults to markdown with page metadata. See
                https://spider.cloud/openapi.yaml for every field.
            base_url: API base URL.
            timeout: Request timeout in seconds.
            client: Optional ``httpx.Client`` to reuse.
            async_client: Optional ``httpx.AsyncClient`` to reuse.
        """
        if mode not in ("scrape", "crawl"):
            raise ValueError(f"Unrecognized mode '{mode}'. Expected one of 'scrape', 'crawl'.")
        self.url = url
        self.mode = mode
        self.params = params if params is not None else dict(DEFAULT_PARAMS)
        self.api_key = resolve_api_key(api_key)
        self.base_url = base_url
        self.timeout = timeout
        self.client = client
        self.async_client = async_client

    def _request_body(self) -> dict[str, Any]:
        return {**self.params, "url": self.url}

    def _to_documents(self, data: Any) -> Iterator[Document]:
        pages = as_pages(data)
        if self.mode == "scrape":
            pages = pages[:1]
        for page in pages:
            content = page.get("content")
            if content is None:
                continue
            metadata: dict[str, Any] = dict(page.get("metadata") or {})
            metadata.setdefault("source", page.get("url") or self.url)
            if page.get("status") is not None:
                metadata.setdefault("status", page["status"])
            yield Document(page_content=str(content), metadata=metadata)

    def lazy_load(self) -> Iterator[Document]:
        """Load Documents one page at a time."""
        data = post(
            self.mode,
            self._request_body(),
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            client=self.client,
            require_key=self.mode == "crawl",
        )
        yield from self._to_documents(data)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """Async version of :meth:`lazy_load`."""
        data = await apost(
            self.mode,
            self._request_body(),
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            client=self.async_client,
            require_key=self.mode == "crawl",
        )
        for doc in self._to_documents(data):
            yield doc
