"""Spider tools for LangChain agents."""

from __future__ import annotations

from typing import Any, Literal, Optional

import httpx
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, BaseToolkit, ToolException
from langchain_core.utils import secret_from_env
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from langchain_spider._client import (
    API_KEY_ENV,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    SpiderAPIError,
    apost,
    as_pages,
    post,
)

ReturnFormat = Literal["markdown", "text", "raw"]
RequestMode = Literal["smart", "http", "browser"]


class _SpiderBaseTool(BaseTool):
    """Fields shared by the Spider tools."""

    api_key: Optional[SecretStr] = Field(default_factory=secret_from_env(API_KEY_ENV, default=None))
    """Spider API key. Defaults to the ``SPIDER_API_KEY`` env var."""
    base_url: str = DEFAULT_BASE_URL
    """API base URL."""
    timeout: float = DEFAULT_TIMEOUT
    """Request timeout in seconds."""
    params: dict[str, Any] = Field(default_factory=dict)
    """Spider request fields sent on every call. The model's arguments win."""
    max_content_chars: Optional[int] = None
    """Cut each page's content to this many characters. ``None`` keeps it all."""
    client: Optional[httpx.Client] = Field(default=None, exclude=True)
    """Optional ``httpx.Client`` to reuse."""
    async_client: Optional[httpx.AsyncClient] = Field(default=None, exclude=True)
    """Optional ``httpx.AsyncClient`` to reuse."""
    handle_tool_error: bool = True
    """Return API errors to the model as the tool result instead of raising.

    Errors raise ``ToolException`` with the original error as ``__cause__``.
    """

    def _key(self) -> Optional[str]:
        return self.api_key.get_secret_value() if self.api_key else None

    def _cut(self, content: Any) -> Optional[str]:
        if content is None:
            return None
        text = str(content)
        if self.max_content_chars is not None:
            return text[: self.max_content_chars]
        return text

    def _post(self, route: str, body: dict[str, Any], require_key: bool) -> Any:
        try:
            return post(
                route,
                body,
                api_key=self._key(),
                base_url=self.base_url,
                timeout=self.timeout,
                client=self.client,
                require_key=require_key,
            )
        except (SpiderAPIError, ValueError, httpx.HTTPError) as err:
            raise ToolException(str(err)) from err

    async def _apost(self, route: str, body: dict[str, Any], require_key: bool) -> Any:
        try:
            return await apost(
                route,
                body,
                api_key=self._key(),
                base_url=self.base_url,
                timeout=self.timeout,
                client=self.async_client,
                require_key=require_key,
            )
        except (SpiderAPIError, ValueError, httpx.HTTPError) as err:
            raise ToolException(str(err)) from err


class SpiderScrapeInput(BaseModel):
    """Input for :class:`SpiderScrapeTool`."""

    url: str = Field(description="Absolute URL of the page, starting with http:// or https://")
    return_format: Optional[ReturnFormat] = Field(
        default=None,
        description="Output format. markdown (default) suits most uses. raw is the page HTML.",
    )
    request: Optional[RequestMode] = Field(
        default=None,
        description=(
            "How to fetch. smart (default) uses plain HTTP and switches to a "
            "browser when the page needs JavaScript. browser always renders."
        ),
    )


class SpiderScrapeTool(_SpiderBaseTool):
    """Fetch one web page with Spider and return its content.

    Setup:
        .. code-block:: bash

            pip install -U langchain-spider
            export SPIDER_API_KEY="your-key"

    Instantiate:
        .. code-block:: python

            from langchain_spider import SpiderScrapeTool

            tool = SpiderScrapeTool()

    Invoke:
        .. code-block:: python

            tool.invoke({"url": "https://spider.cloud"})

    Works without a key on a rate limited keyless tier.
    """

    name: str = "spider_scrape"
    description: str = (
        "Fetch one web page and return its content as markdown or text. "
        "Use it to read a page whose URL you already know."
    )
    args_schema: type[BaseModel] = SpiderScrapeInput

    def _body(
        self, url: str, return_format: Optional[str], request: Optional[str]
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"return_format": "markdown", **self.params, "url": url}
        if return_format is not None:
            body["return_format"] = return_format
        if request is not None:
            body["request"] = request
        return body

    def _result(self, data: Any, url: str) -> str:
        pages = as_pages(data)
        if not pages:
            return f"No content returned for {url}."
        page = pages[0]
        content = self._cut(page.get("content"))
        if content is None:
            error = page.get("error")
            return f"No content returned for {url}." + (f" Error: {error}" if error else "")
        return content

    def _run(
        self,
        url: str,
        return_format: Optional[str] = None,
        request: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        data = self._post("scrape", self._body(url, return_format, request), require_key=False)
        return self._result(data, url)

    async def _arun(
        self,
        url: str,
        return_format: Optional[str] = None,
        request: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        data = await self._apost(
            "scrape", self._body(url, return_format, request), require_key=False
        )
        return self._result(data, url)


class SpiderSearchInput(BaseModel):
    """Input for :class:`SpiderSearchTool`."""

    query: str = Field(description="The search query.")
    search_limit: Optional[int] = Field(
        default=None, ge=1, le=50, description="How many results to return. Defaults to 5."
    )
    fetch_page_content: Optional[bool] = Field(
        default=None,
        description="Also fetch the content of each result page. Slower and uses more credits.",
    )
    country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Two letter country code, for example us.",
    )
    language: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Two letter language code, for example en.",
    )
    tbs: Optional[Literal["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]] = Field(
        default=None, description="Time range: past hour, day, week, month or year."
    )


class SpiderSearchTool(_SpiderBaseTool):
    """Search the web with Spider.

    Returns a list of results with ``title``, ``description`` and ``url``. With
    ``fetch_page_content`` set, each result also has the page ``content``.

    Setup:
        .. code-block:: bash

            pip install -U langchain-spider
            export SPIDER_API_KEY="your-key"

    Instantiate:
        .. code-block:: python

            from langchain_spider import SpiderSearchTool

            tool = SpiderSearchTool()

    Invoke:
        .. code-block:: python

            tool.invoke({"query": "rust web crawler", "search_limit": 3})

    Needs an API key.
    """

    name: str = "spider_search"
    description: str = (
        "Search the web and return ranked results with title, description and URL. "
        "Set fetch_page_content to also get each result's page content."
    )
    args_schema: type[BaseModel] = SpiderSearchInput
    default_search_limit: int = 5
    """Result count when the model does not set ``search_limit``."""

    def _body(self, query: str, **kwargs: Any) -> dict[str, Any]:
        body: dict[str, Any] = {"search_limit": self.default_search_limit}
        if kwargs.get("fetch_page_content"):
            body["return_format"] = "markdown"
        body.update(self.params)
        body.update({k: v for k, v in kwargs.items() if v is not None})
        body["search"] = query
        return body

    def _result(self, data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            out = []
            for page in as_pages(data):
                item: dict[str, Any] = {"url": page.get("url")}
                for key in ("title", "description"):
                    if page.get(key):
                        item[key] = page[key]
                metadata = page.get("metadata") or {}
                if "title" not in item and metadata.get("title"):
                    item["title"] = metadata["title"]
                content = self._cut(page.get("content"))
                if content is not None:
                    item["content"] = content
                if page.get("error"):
                    item["error"] = page["error"]
                out.append(item)
            return out
        content = data.get("content") if isinstance(data, dict) else None
        if not isinstance(content, list):
            return []
        return [
            {"title": r.get("title"), "description": r.get("description"), "url": r.get("url")}
            for r in content
            if isinstance(r, dict)
        ]

    def _run(
        self,
        query: str,
        search_limit: Optional[int] = None,
        fetch_page_content: Optional[bool] = None,
        country: Optional[str] = None,
        language: Optional[str] = None,
        tbs: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> list[dict[str, Any]]:
        body = self._body(
            query,
            search_limit=search_limit,
            fetch_page_content=fetch_page_content,
            country=country,
            language=language,
            tbs=tbs,
        )
        return self._result(self._post("search", body, require_key=True))

    async def _arun(
        self,
        query: str,
        search_limit: Optional[int] = None,
        fetch_page_content: Optional[bool] = None,
        country: Optional[str] = None,
        language: Optional[str] = None,
        tbs: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> list[dict[str, Any]]:
        body = self._body(
            query,
            search_limit=search_limit,
            fetch_page_content=fetch_page_content,
            country=country,
            language=language,
            tbs=tbs,
        )
        return self._result(await self._apost("search", body, require_key=True))


class SpiderToolkit(BaseToolkit):
    """Both Spider tools with shared settings.

    Instantiate:
        .. code-block:: python

            from langchain_spider import SpiderToolkit

            tools = SpiderToolkit(max_content_chars=20_000).get_tools()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: Optional[SecretStr] = Field(default_factory=secret_from_env(API_KEY_ENV, default=None))
    """Spider API key. Defaults to the ``SPIDER_API_KEY`` env var."""
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    params: dict[str, Any] = Field(default_factory=dict)
    max_content_chars: Optional[int] = None
    client: Optional[httpx.Client] = Field(default=None, exclude=True)
    async_client: Optional[httpx.AsyncClient] = Field(default=None, exclude=True)

    def get_tools(self) -> list[BaseTool]:
        """Return ``[SpiderSearchTool, SpiderScrapeTool]`` built from these settings."""
        shared: dict[str, Any] = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "params": dict(self.params),
            "max_content_chars": self.max_content_chars,
            "client": self.client,
            "async_client": self.async_client,
        }
        return [SpiderSearchTool(**shared), SpiderScrapeTool(**shared)]
