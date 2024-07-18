import os, json, logging
import aiohttp, asyncio
from typing import Optional, Tuple, AsyncIterator
from spider.spider_types import RequestParamsDict, JsonCallback



class AsyncSpider:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Spider with an API key.

        :param api_key: A string of the API key for Spider. Defaults to the SPIDER_API_KEY environment variable.
        :raises ValueError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("SPIDER_API_KEY")
        if self.api_key is None:
            raise ValueError("No API key provided")
    
            
    async def api_post(
        self,
        endpoint: str,
        data: dict,
        stream: bool,
        content_type: str = "application/json",
    ) -> AsyncIterator[Optional[dict]]:
        headers = await self._prepare_headers(content_type)
        
        async for response in self._post_request(
            f"https://api.spider.cloud/v1/{endpoint}", data, headers, stream
        ):
            if stream:
                yield response
            else:
                if isinstance(response, aiohttp.ClientResponse):
                    if response.status == 200:
                        yield await response.json(content_type=None)
                    else:
                        yield await self._handle_error(response, f"post to {endpoint}")
                        # yield None
                else:
                    yield response

    async def api_get(
        self, 
        endpoint: str, 
        data: dict, 
        stream: bool, 
        content_type: str = "application/json"
    ) -> AsyncIterator[Optional[dict]]:
        headers = self._prepare_headers(content_type)
        async for response in self._get_request(
            f"https://api.spider.cloud/v1/{endpoint}", data, headers, stream
        ):
            if stream:
                yield response
            else:
                if isinstance(response, aiohttp.ClientResponse):
                    if response.status == 200:
                        yield await response.json(content_type=None)
                    else:
                        await self._handle_error(response, f"get from {endpoint}")
                        yield None
                else:
                    yield response

    async def api_delete(
        self, 
        endpoint: str, 
        data: dict,
        stream: bool, 
        content_type: str = "application/json"
    ) -> AsyncIterator[Optional[dict]]:
        headers = self._prepare_headers(content_type)
        async for response in self._delete_request(
            f"https://api.spider.cloud/v1/{endpoint}", data, headers, stream
        ):
            if stream:
                yield response
            else:
                if isinstance(response, aiohttp.ClientResponse):
                    if response.status in [200, 202]:
                        yield await response.json(content_type=None)
                    else:
                        await self._handle_error(response, f"delete from {endpoint}")
                        yield None
                else:
                    yield response

    async def scrape_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Scrape data from the specified URL.

        :param url: The URL from which to scrape data.
        :param params: Optional dictionary of additional parameters for the scrape request.
        :return: JSON response containing the scraping results.
        """
        async for response in self.api_post(
            "crawl", {"url": url, "limit": 1, **(params or {})}, stream, content_type
        ):
            yield response

    async def crawl_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
        callback: Optional[JsonCallback] = None,
    ) -> AsyncIterator[Optional[dict]]:
        jsonl = stream and callable(callback)

        if jsonl:
            content_type = "application/jsonl"
            
        async for response in self.api_post(
                "crawl", {"url": url, **(params or {})}, stream, content_type
            ):
            if jsonl:
                async for _ in self.stream_reader(response, callback):
                    yield
            else:
                yield response
        
    async def links(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Retrieve links from the specified URL.

        :param url: The URL from which to extract links.
        :param params: Optional parameters for the link retrieval request.
        :return: JSON response containing the links.
        """
        async for response in self.api_post(
            "links", {"url": url, **(params or {})}, stream, content_type
        ):
            yield response

    async def screenshot(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Take a screenshot of the specified URL.

        :param url: The URL to capture a screenshot from.
        :param params: Optional parameters to customize the screenshot capture.
        :return: JSON response with screenshot data.
        """
        async for response in self.api_post(
            "screenshot", {"url": url, **(params or {})}, stream, content_type
        ):
            yield response

    async def search(
        self,
        q: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Perform a search and gather a list of websites to start crawling and collect resources.

        :param search: The search query.
        :param params: Optional parameters to customize the search.
        :return: JSON response or the raw response stream if streaming enabled.
        """
        async for response in self.api_post(
            "search", {"search": q, **(params or {})}, stream, content_type
        ):
            yield response

    async def transform(
        self, data, params=None, stream=False, content_type="application/json"
    ):
        """
        Transform HTML to Markdown or text. You can send up to 10MB of data at once.

        :param data: The data to transform a list of objects with the 'html' key and an optional 'url' key only used readability mode.
        :param params: Optional parameters to customize the search.
        :return: JSON response or the raw response stream if streaming enabled.
        """
        async for response in self.api_post(
            "transform", {"data": data, **(params or {})}, stream, content_type
        ):
            yield response

    async def extract_contacts(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Extract contact information from the specified URL.

        :param url: The URL from which to extract contact information.
        :param params: Optional parameters for the contact extraction.
        :return: JSON response containing extracted contact details.
        """
        async for response in self.api_post(
            "pipeline/extract-contacts",
            {"url": url, **(params or {})},
            stream,
            content_type,
        ):
            yield response

    async def label(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Apply labeling to data extracted from the specified URL.

        :param url: The URL to label data from.
        :param params: Optional parameters to guide the labeling process.
        :return: JSON response with labeled data.
        """
        async for response in self.api_post(
            "pipeline/label", {"url": url, **(params or {})}, stream, content_type
        ):
            yield response

    async def get_crawl_state(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Retrieve the website active crawl state.

        :return: JSON response of the crawl state and credits used.
        """
        async for response in self.api_post(
            "crawl/status", {"url": url, **(params or {}, stream, content_type)}
        ):
            yield response

    async def get_credits(self):
        """
        Retrieve the account's remaining credits.

        :return: JSON response containing the number of credits left.
        """
        async for response in self.api_get("credits", {}, stream=True):
            yield response

    async def data_post(self, 
                        table: str, 
                        data: Optional[RequestParamsDict] = None):
        """
        Send data to a specific table via POST request.
        :param table: The table name to which the data will be posted.
        :param data: A dictionary representing the data to be posted.
        :return: The JSON response from the server.
        """
        async for response in self.api_post(f"data/{table}", data, stream=False):
            yield response

    async def data_get(
        self,
        table: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        Retrieve data from a specific table via GET request.
        :param table: The table name from which to retrieve data.
        :param params: Optional parameters to modify the query.
        :return: The JSON response from the server.
        """
        async for response in self.api_get(f"data/{table}", params, stream=False):
            yield response

    async def data_delete(
        self,
        table: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        Delete data from a specific table via DELETE request.
        :param table: The table name from which data will be deleted.
        :param params: Parameters to identify which data to delete.
        :return: The JSON response from the server.
        """
        async for response in self.api_delete(f"data/{table}", data=params, stream=False):
            yield response

    async def stream_reader(self, response: aiohttp.ClientResponse, 
                            callback: JsonCallback) -> AsyncIterator[None]:
        try:
            buffer = ""
            async for chunk in response.content.iter_any():
                buffer += chunk.decode('utf-8', errors='replace')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        json_data = json.loads(line)
                        callback(json_data)
                        yield
                    except json.JSONDecodeError as e:
                        logging.error(f"Error decoding JSON: {e}")
                        logging.error(f"Problematic line: {line}")
            
            if buffer:
                try:
                    json_data = json.loads(buffer)
                    callback(json_data)
                    yield
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON in remaining buffer: {e}")
                    logging.error(f"Problematic data: {buffer}")

        except aiohttp.ClientConnectionError as e:
            logging.error(f"Connection error in stream_reader: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            await response.release()


    async def _prepare_headers(self, content_type: str = "application/json"):
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"Spider-Client/0.0.27",
        }

    async def _post_request(self, url: str, data, headers, stream: bool) -> AsyncIterator[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if stream or 'Transfer-Encoding' in response.headers:
                    yield response
                else:
                    # yield await response.json()
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'application/json' in content_type:
                        yield await response.json()
                    else:
                        text = await response.text()
                        yield {
                            'status': response.status,
                            'content_type': content_type,
                            'text': text,
                            'headers': dict(response.headers)
                        }
                        
    async def _get_request(self, url: str, data, headers, stream: bool) -> AsyncIterator[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, data=data, headers=headers) as response:
                if stream or 'Transfer-Encoding' in response.headers:
                    yield response
                else:
                    yield await response.json()
                    

    async def _delete_request(self, url: str, data, headers, stream: bool) -> AsyncIterator[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, json=data, headers=headers) as response:
                if stream or 'Transfer-Encoding' in response.headers:
                    yield response
                else:
                    yield await response.json()

    async def _handle_error(self, response, action):
        if response.status in [402, 409, 500]:
            if response.headers.get('Content-Type', '').startswith('application/json'):
                error_json = await response.json()
                error_message = error_json.get("error", "Unknown error occurred")
            else:
                error_message = await response.text()
            raise Exception(
                f"Failed to {action}. Status code: {response.status}. Error: {error_message}"
            )
        else:
            raise Exception(
                f"Unexpected error occurred while trying to {action}. Status code: {response.status}"
            )