import os, requests
from typing import TypedDict, Optional, Dict, List, Literal


class RequestParamsDict(TypedDict, total=False):
    url: Optional[str]
    request: Optional[Literal["http", "chrome", "smart"]]
    limit: Optional[int]
    return_format: Optional[Literal["raw", "markdown", "html2text", "text", "bytes"]]
    tld: Optional[bool]
    depth: Optional[int]
    cache: Optional[bool]
    budget: Optional[Dict[str, int]]
    locale: Optional[str]
    cookies: Optional[str]
    stealth: Optional[bool]
    headers: Optional[Dict[str, str]]
    anti_bot: Optional[bool]
    metadata: Optional[bool]
    viewport: Optional[Dict[str, int]]
    encoding: Optional[str]
    subdomains: Optional[bool]
    user_agent: Optional[str]
    store_data: Optional[bool]
    gpt_config: Optional[List[str]]
    fingerprint: Optional[bool]
    storageless: Optional[bool]
    readability: Optional[bool]
    proxy_enabled: Optional[bool]
    respect_robots: Optional[bool]
    query_selector: Optional[str]
    full_resources: Optional[bool]
    request_timeout: Optional[int]
    run_in_background: Optional[bool]
    skip_config_checks: Optional[bool]


class Spider:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Spider with an API key.

        :param api_key: A string of the API key for Spider. Defaults to the SPIDER_API_KEY environment variable.
        :raises ValueError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("SPIDER_API_KEY")
        if self.api_key is None:
            raise ValueError("No API key provided")

    def api_post(
        self,
        endpoint: str,
        data: dict,
        stream: bool,
        content_type: str = "application/json",
    ):
        """
        Send a POST request to the specified API endpoint.

        :param endpoint: The API endpoint to which the POST request is sent.
        :param data: The data (dictionary) to be sent in the POST request.
        :param stream: Boolean indicating if the response should be streamed.
        :return: The JSON response or the raw response stream if stream is True.
        """
        headers = self._prepare_headers(content_type)
        response = self._post_request(
            f"https://api.spider.cloud/v1/{endpoint}", data, headers, stream
        )
        if stream:
            return response
        elif response.status_code == 200:
            return response.json()
        else:
            self._handle_error(response, f"post to {endpoint}")

    def api_get(
        self, endpoint: str, stream: bool, content_type: str = "application/json"
    ):
        """
        Send a GET request to the specified endpoint.

        :param endpoint: The API endpoint from which to retrieve data.
        :return: The JSON decoded response.
        """
        headers = self._prepare_headers(content_type)
        response = self._get_request(
            f"https://api.spider.cloud/v1/{endpoint}", headers, stream
        )
        if response.status_code == 200:
            return response.json()
        else:
            self._handle_error(response, f"get from {endpoint}")

    def api_delete(
        self, endpoint: str, stream: bool, content_type: str = "application/json"
    ):
        """
        Send a DELETE request to the specified endpoint.

        :param endpoint: The API endpoint from which to retrieve data.
        :return: The JSON decoded response.
        """
        headers = self._prepare_headers(content_type)
        response = self._delete_request(
            f"https://api.spider.cloud/v1/{endpoint}", headers, stream
        )
        if response.status_code in [200, 202]:
            return response.json()
        else:
            self._handle_error(response, f"get from {endpoint}")

    def scrape_url(
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
        return self.api_post(
            "crawl", {"url": url, "limit": 1, **(params or {})}, stream, content_type
        )

    def crawl_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Start crawling at the specified URL.

        :param url: The URL to begin crawling.
        :param params: Optional dictionary with additional parameters to customize the crawl.
        :param stream: Boolean indicating if the response should be streamed. Defaults to False.
        :return: JSON response or the raw response stream if streaming enabled.
        """
        return self.api_post(
            "crawl", {"url": url, **(params or {})}, stream, content_type
        )

    def links(
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
        return self.api_post(
            "links", {"url": url, **(params or {})}, stream, content_type
        )

    def screenshot(
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
        return self.api_post(
            "screenshot", {"url": url, **(params or {})}, stream, content_type
        )

    def search(
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
        return self.api_post(
            "search", {"search": q, **(params or {})}, stream, content_type
        )

    def transform(
        self, data, params=None, stream=False, content_type="application/json"
    ):
        """
        Transform HTML to Markdown or text. You can send up to 10MB of data at once.

        :param data: The data to transform a list of objects with the 'html' key and an optional 'url' key only used readability mode.
        :param params: Optional parameters to customize the search.
        :return: JSON response or the raw response stream if streaming enabled.
        """
        return self.api_post(
            "transform", {"data": data, **(params or {})}, stream, content_type
        )

    def extract_contacts(
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
        return self.api_post(
            "pipeline/extract-contacts",
            {"url": url, **(params or {})},
            stream,
            content_type,
        )

    def label(
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
        return self.api_post(
            "pipeline/label", {"url": url, **(params or {})}, stream, content_type
        )

    def get_crawl_state(
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
        return self.api_post(
            "crawl/status", {"url": url, **(params or {}, stream, content_type)}
        )

    def get_credits(self):
        """
        Retrieve the account's remaining credits.

        :return: JSON response containing the number of credits left.
        """
        return self.api_get("credits")

    def data_post(self, table: str, data: Optional[RequestParamsDict] = None):
        """
        Send data to a specific table via POST request.
        :param table: The table name to which the data will be posted.
        :param data: A dictionary representing the data to be posted.
        :return: The JSON response from the server.
        """
        return self.api_post(f"data/{table}", data)

    def data_get(
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
        return self.api_get(f"data/{table}", params=params)

    def data_delete(
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
        return self.api_delete(f"data/{table}", params=params)

    def _prepare_headers(self, content_type: str = "application/json"):
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"Spider-Client/0.0.27",
        }

    def _post_request(self, url: str, data, headers, stream=False):
        return requests.post(url, headers=headers, json=data, stream=stream)

    def _get_request(self, url: str, headers, stream=False):
        return requests.get(url, headers=headers, stream=stream)

    def _delete_request(self, url: str, headers, stream=False):
        return requests.delete(url, headers=headers, stream=stream)

    def _handle_error(self, response, action):
        if response.status_code in [402, 409, 500]:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(
                f"Failed to {action}. Status code: {response.status_code}. Error: {error_message}"
            )
        else:
            raise Exception(
                f"Unexpected error occurred while trying to {action}. Status code: {response.status_code}"
            )
