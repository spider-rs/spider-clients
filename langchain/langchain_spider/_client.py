"""Small HTTP client for the Spider API, shared by the loader and the tools."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

__version__ = "0.1.0"

DEFAULT_BASE_URL = "https://api.spider.cloud"
DEFAULT_TIMEOUT = 120.0
API_KEY_ENV = "SPIDER_API_KEY"
KEY_URL = "https://spider.cloud/api-keys"


class SpiderAPIError(Exception):
    """Raised when the Spider API answers with a non 2xx status."""

    def __init__(
        self,
        route: str,
        status_code: int,
        body: str,
        retry_after: Optional[float] = None,
    ) -> None:
        hint = ""
        if status_code in (401, 402):
            hint = f" Set {API_KEY_ENV} to a key from {KEY_URL}."
        elif status_code == 429 and retry_after is not None:
            hint = f" Retry after {retry_after:g}s."
        super().__init__(f"Spider /{route} failed with {status_code}: {body[:500]}{hint}")
        self.route = route
        self.status_code = status_code
        self.body = body
        self.retry_after = retry_after


def resolve_api_key(api_key: Optional[str]) -> Optional[str]:
    """Return the given key, else the SPIDER_API_KEY environment variable."""
    return api_key or os.environ.get(API_KEY_ENV) or None


def _headers(api_key: Optional[str]) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"langchain-spider/{__version__}",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _body(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _check_key(route: str, api_key: Optional[str], require_key: bool) -> None:
    if require_key and not api_key:
        raise ValueError(
            f"Spider /{route} needs an API key. Set {API_KEY_ENV} or pass "
            f"api_key. Get one at {KEY_URL}."
        )


def _parse(route: str, response: httpx.Response) -> Any:
    if response.is_success:
        return response.json()
    retry = response.headers.get("Retry-After")
    try:
        retry_after = float(retry) if retry else None
    except ValueError:
        retry_after = None
    raise SpiderAPIError(route, response.status_code, response.text, retry_after)


def post(
    route: str,
    params: dict[str, Any],
    *,
    api_key: Optional[str],
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    client: Optional[httpx.Client] = None,
    require_key: bool = False,
) -> Any:
    """POST JSON to a Spider route and return the parsed JSON."""
    _check_key(route, api_key, require_key)
    url = f"{base_url.rstrip('/')}/{route}"
    kwargs: dict[str, Any] = {
        "json": _body(params),
        "headers": _headers(api_key),
        "timeout": timeout,
    }
    if client is not None:
        return _parse(route, client.post(url, **kwargs))
    with httpx.Client() as owned:
        return _parse(route, owned.post(url, **kwargs))


async def apost(
    route: str,
    params: dict[str, Any],
    *,
    api_key: Optional[str],
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    client: Optional[httpx.AsyncClient] = None,
    require_key: bool = False,
) -> Any:
    """Async version of :func:`post`."""
    _check_key(route, api_key, require_key)
    url = f"{base_url.rstrip('/')}/{route}"
    kwargs: dict[str, Any] = {
        "json": _body(params),
        "headers": _headers(api_key),
        "timeout": timeout,
    }
    if client is not None:
        return _parse(route, await client.post(url, **kwargs))
    async with httpx.AsyncClient() as owned:
        return _parse(route, await owned.post(url, **kwargs))


def as_pages(data: Any) -> list[dict[str, Any]]:
    """Normalize a Spider response to a list of page objects."""
    if isinstance(data, list):
        return [p for p in data if isinstance(p, dict)]
    if isinstance(data, dict):
        return [data]
    return []
