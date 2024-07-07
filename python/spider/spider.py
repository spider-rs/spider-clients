import os, requests, json, logging
from typing import Optional, Dict
from spider.spider_types import RequestParamsDict, JsonCallback
from spider.supabase_client import Supabase


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

    def init_supabase(self):
        """
        Initialize the Supabase client if it is not already initialized.

        This method is optional and only needs to be called if you plan to use the Supabase client.

        :raises ImportError: If the 'supabase' package is not installed.
        :raises Exception: If there is an issue fetching the anon key or initializing the client.
        """
        Supabase.init()

    @property
    def supabase(self):
        """
        Get the Supabase client instance.

        This property is optional and only needs to be accessed if you plan to use the Supabase client.
        Ensure that the Supabase client has been initialized by calling 'init_supabase()' before accessing this property.

        :return: The initialized Supabase client instance.
        :raises Exception: If the Supabase client has not been initialized.
        """
        return Supabase.get_client()

    def api_post(
        self,
        endpoint: str,
        data: dict,
        stream: bool = False,
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
            f"https://api.spider.cloud/{endpoint}", data, headers, stream
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
            f"https://api.spider.cloud/{endpoint}", headers, stream
        )
        if response.status_code == 200:
            return response.json()
        else:
            self._handle_error(response, f"get from {endpoint}")

    def api_delete(
        self,
        endpoint: str,
        params: Optional[RequestParamsDict] = None,
        stream: Optional[bool] = False,
        content_type: Optional[str] = "application/json",
    ):
        """
        Send a DELETE request to the specified endpoint.

        :param endpoint: The API endpoint from which to retrieve data.
        :param params: Optional parameters to include in the DELETE request.
        :param stream: Boolean indicating if the response should be streamed.
        :param content_type: The content type of the request.
        :return: The JSON decoded response.
        """
        headers = self._prepare_headers(content_type)
        response = self._delete_request(
            f"https://api.spider.cloud/v1/{endpoint}", headers, params, stream
        )
        if response.status_code in [200, 202]:
            return response.json()
        else:
            self._handle_error(response, f"delete from {endpoint}")

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
        params: Optional[RequestParamsDict],
        stream: Optional[bool] = False,
        content_type: Optional[str] = "application/json",
        callback: Optional[JsonCallback] = None,
    ):
        """
        Start crawling at the specified URL.

        :param url: The URL to begin crawling.
        :param params: Optional dictionary with additional parameters to customize the crawl.
        :param stream: Optional Boolean indicating if the response should be streamed. Defaults to False.
        :param content_type: Optional str to determine the content-type header of the request.
        :param callback: Optional callback to use with streaming. This will only send the data via callback.

        :return: JSON response or the raw response stream if streaming enabled.
        """
        jsonl = stream and callable(callback)

        if jsonl:
            content_type = "application/jsonl"

        response = self.api_post(
            "crawl", {"url": url, **(params or {})}, stream, content_type
        )

        if jsonl:
            return self.stream_reader(response, callback)
        else:
            return response

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

    def create_signed_url(
        self,
        domain: Optional[str] = None,
        options: Optional[Dict[str, int]] = None,
        stream: Optional[bool] = True,
    ):
        """
        Create a signed url to download files from the storage.

        :param domain: Optional domain name to specify the storage path.
        :param options: Optional dictionary containing configuration parameters, such as:
            - 'page': Optional page number for pagination.
            - 'limit': Optional page limit for pagination.
            - 'expiresIn': Optional expiration time for the signed URL.
        :param stream: Boolean indicating if the response should be streamed. Defaults to True.
        :return: The raw response stream if stream is True.
        """
        params = {}
        if domain:
            params["domain"] = domain
        if options:
            params.update(options)

        endpoint = "data/storage"
        headers = self._prepare_headers("application/octet-stream")
        response = self._get_request(
            f"https://api.spider.cloud/v1/{endpoint}", headers, stream, params=params
        )
        if response.status_code == 200:
            if stream:
                return response.raw
            else:
                return response.content
        else:
            self._handle_error(response, f"download from {endpoint}")

    def get_crawl_state(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: Optional[bool] = False,
        content_type: Optional[str] = "application/json",
    ):
        """
        Retrieve the website active crawl state.

        :return: JSON response of the crawl state and credits used.
        """
        payload = {"url": url, "stream": stream, "content_type": content_type}
        if params:
            payload.update(params)

        return self.api_post("data/crawl_state", payload, stream)

    def get_credits(self):
        """
        Retrieve the account's remaining credits.

        :return: JSON response containing the number of credits left.
        """
        return self.api_get("data/credits", stream=False)

    def data_post(self, table: str, data: Optional[RequestParamsDict] = None):
        """
        Send data to a specific table via POST request.
        :param table: The table name to which the data will be posted.
        :param data: A dictionary representing the data to be posted.
        :return: The JSON response from the server.
        """
        return self.api_post(f"data/{table}", data, stream=False)

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
        return self.api_get(f"data/{table}", params)

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

    def stream_reader(self, response, callback):
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            try:
                json_obj = json.loads(chunk.strip())
                callback(json_obj)
            except json.JSONDecodeError:
                logging.warning("Failed to parse chunk: %s", chunk)

    def _prepare_headers(self, content_type: str = "application/json"):
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"Spider-Client/0.0.52",
        }

    def _post_request(self, url: str, data, headers, stream=False):
        return requests.post(url, headers=headers, json=data, stream=stream)

    def _get_request(self, url: str, headers, stream=False):
        return requests.get(url, headers=headers, stream=stream)

    def _delete_request(self, url: str, headers, params=None, stream=False):
        return requests.delete(url, headers=headers, params=params, stream=stream)

    def _handle_error(self, response, action):
        if response.status_code in [402, 409, 500]:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(
                f"Failed to {action}. Status code: {response.status_code}. Error: {error_message}"
            )
        elif response.status_code == 201:
            json_response = response.json()
            if json_response.get("data") == None:
                return json_response
            else:
                raise Exception(
                    f"Unexpected error occurred while trying to {action}. Status code: {response.status_code}"
                )
        else:
            raise Exception(
                f"Unexpected error occurred while trying to {action}. Status code: {response.status_code}"
            )
