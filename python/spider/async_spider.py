import os
import json
import logging
from typing import Optional, Dict, Any, AsyncIterator, Callable
import aiohttp
from aiohttp import ClientSession, ClientResponse
from types import TracebackType
from typing import Type
from spider.spider_types import RequestParamsDict, JsonCallback, QueryRequest

class AsyncSpider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SPIDER_API_KEY")
        if self.api_key is None:
            raise ValueError("No API key provided")
        self.session: Optional[ClientSession] = None

    async def __aenter__(self) -> 'AsyncSpider':
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if self.session:
            await self.session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        if not self.session:
            raise RuntimeError("Session not initialized. Use AsyncSpider as a context manager.")

        headers = self._prepare_headers(content_type)
        url = f"https://api.spider.cloud/v1/{endpoint}"

        if params:
            params = {k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()}
        async with self.session.request(method, url, json=data, params=params, headers=headers) as response:
            if stream:
                async for chunk in response.content.iter_any():
                    yield chunk
            else:
                if response.status >= 200 and response.status < 300:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        yield await response.json()
                    else:
                        new_text = await response.text()
                        new_json = json.loads(new_text)
                        yield new_json
                else:
                    await self._handle_error(response, f"{method} to {endpoint}")

    async def scrape_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, "limit": 1, **(params or {})}
        async for response in self._request("POST", "crawl", data=data, stream=stream, content_type=content_type):
            yield response

    async def crawl_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
        callback: Optional[JsonCallback] = None
    ) -> AsyncIterator[Any]:
        data = {"url": url, **(params or {})}
        if stream and callback:
            content_type = "application/jsonl"

        async for response in self._request("POST", "crawl", data=data, stream=stream, content_type=content_type):
            if stream and callback:
                await self._stream_reader(response, callback)
            else:
                yield response

    async def links(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, **(params or {})}
        async for response in self._request("POST", "links", data=data, stream=stream, content_type=content_type):
            yield response

    async def screenshot(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, **(params or {})}
        async for response in self._request("POST", "screenshot", data=data, stream=stream, content_type=content_type):
            yield response

    async def search(
        self,
        q: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"search": q, **(params or {})}
        async for response in self._request("POST", "search", data=data, stream=stream, content_type=content_type):
            yield response

    async def transform(
        self,
        data: list,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        payload = {"data": data, **(params or {})}
        async for response in self._request("POST", "transform", data=payload, stream=stream, content_type=content_type):
            yield response

    async def extract_contacts(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, **(params or {})}
        async for response in self._request("POST", "pipeline/extract-contacts", data=data, stream=stream, content_type=content_type):
            yield response

    async def label(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, **(params or {})}
        async for response in self._request("POST", "pipeline/label", data=data, stream=stream, content_type=content_type):
            yield response

    async def query(
        self,
        params: Optional[QueryRequest] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        async for response in self._request("GET", "data/query", params=params, stream=stream, content_type=content_type):
            yield response

    async def create_signed_url(
        self,
        domain: Optional[str] = None,
        params: Optional[Dict[str, int]] = None,
        stream: bool = True
    ) -> AsyncIterator[Any]:
        if domain:
            params = params or {}
            params["domain"] = domain
        async for response in self._request("GET", "data/storage", params=params, stream=stream, content_type="application/octet-stream"):
            yield response

    async def get_crawl_state(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json"
    ) -> AsyncIterator[Any]:
        data = {"url": url, "stream": stream, "content_type": content_type, **(params or {})}
        async for response in self._request("POST", "data/crawl_state", data=data, stream=stream, content_type=content_type):
            yield response

    async def get_credits(self) -> AsyncIterator[Any]:
        async for response in self._request("GET", "data/credits"):
            yield response

    async def data_post(self, table: str, data: Optional[RequestParamsDict] = {}) -> AsyncIterator[Any]:
        async for response in self._request("POST", f"data/{table}", data=data):
            yield response

    async def data_get(self, table: str, params: Optional[RequestParamsDict] = None) -> AsyncIterator[Any]:
        async for response in self._request("GET", f"data/{table}", params=params):
            yield response

    async def data_delete(self, table: str, data: Optional[RequestParamsDict] = {}, params: Optional[RequestParamsDict] = None) -> AsyncIterator[Any]:
        async for response in self._request("DELETE", f"data/{table}", data=data, params=params):
            yield response

    async def _stream_reader(self, response: Any, callback: Callable[[Dict[str, Any]], None]) -> None:
        buffer = ""
        async for chunk in response:
            buffer += chunk.decode('utf-8', errors='replace')
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                try:
                    json_data = json.loads(line)
                    callback(json_data)
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON: {e}")
                    logging.error(f"Problematic line: {line}")

        if buffer:
            try:
                json_data = json.loads(buffer)
                callback(json_data)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON in remaining buffer: {e}")
                logging.error(f"Problematic data: {buffer}")

    def _prepare_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "AsyncSpider-Client/0.1.0",
        }

    async def _handle_error(self, response: ClientResponse, action: str) -> None:
        if response.status in [402, 409, 500]:
            error_message = (await response.json()).get("error", "Unknown error occurred")
            raise Exception(f"Failed to {action}. Status code: {response.status}. Error: {error_message}")
        else:
            raise Exception(f"Unexpected error occurred while trying to {action}. Status code: {response.status}. Here is the response: {await response.text()}")
