import os, requests, logging, ijson, tenacity, time
from typing import Optional, Dict
from dataclasses import dataclass
from spider.spider_types import (
    RequestParamsDict,
    SearchRequestParams,
    RequestParamsTransform,
    JsonCallback,
    QueryRequest,
)


@dataclass
class RateLimitState:
    """Tracks the latest rate limit info from API response headers."""

    limit: int = 0
    remaining: int = 0
    reset_seconds: int = 0

    def update_from_headers(self, headers):
        """Update rate limit state from response headers."""
        if "RateLimit-Limit" in headers:
            self.limit = int(headers["RateLimit-Limit"])
        if "RateLimit-Remaining" in headers:
            self.remaining = int(headers["RateLimit-Remaining"])
        if "RateLimit-Reset" in headers:
            self.reset_seconds = int(headers["RateLimit-Reset"])


# AI Studio URLs and info
AI_STUDIO_BASE_URL = "https://aistudio.spider.cloud"
AI_STUDIO_PRICING_URL = "https://aistudio.spider.cloud/pricing"
AI_STUDIO_DOCS_URL = "https://aistudio.spider.cloud/docs"

# AI Studio tier info: (price, credits, rate_limit)
AI_STUDIO_TIERS = {
    "starter": {"price": 6, "credits": 30000, "rate_limit": 1},
    "lite": {"price": 30, "credits": 150000, "rate_limit": 5},
    "standard": {"price": 125, "credits": 600000, "rate_limit": 10},
    "custom": {"price": 600, "credits": 3000000, "rate_limit": 25},
}

# AI Studio tier rate limits (requests per second)
AI_STUDIO_RATE_LIMITS = {
    "starter": 1,
    "lite": 5,
    "standard": 10,
    "custom": 25,
}


class AIStudioSubscriptionRequired(Exception):
    """Raised when AI Studio subscription is required but not active."""

    subscribe_url = AI_STUDIO_PRICING_URL

    def __init__(self, message: str = None):
        starter = AI_STUDIO_TIERS["starter"]
        default_msg = (
            f"AI Studio subscription required to use /ai/* endpoints.\n\n"
            f"Subscribe at: {AI_STUDIO_PRICING_URL}\n\n"
            f"Plans start at ${starter['price']}/month with {starter['credits']:,} credits."
        )
        self.message = message or default_msg
        super().__init__(self.message)


class AIStudioRateLimitExceeded(Exception):
    """Raised when AI Studio rate limit is exceeded."""

    upgrade_url = AI_STUDIO_PRICING_URL

    def __init__(self, retry_after_ms: int, current_tier: str = None):
        self.retry_after_ms = retry_after_ms
        upgrade_hint = ""
        if current_tier and current_tier != "custom":
            upgrade_hint = f"\n\nUpgrade your plan for higher rate limits: {AI_STUDIO_PRICING_URL}"
        self.message = f"AI Studio rate limit exceeded. Retry after {retry_after_ms}ms.{upgrade_hint}"
        super().__init__(self.message)


class RateLimiter:
    """Simple client-side rate limiter using sliding window."""

    def __init__(self, requests_per_second: int):
        self.max_requests = requests_per_second
        self.window_ms = 1000
        self.timestamps: list = []

    def set_limit(self, requests_per_second: int):
        """Update the rate limit."""
        self.max_requests = requests_per_second

    def acquire(self):
        """Wait until a request can be made, then acquire the slot."""
        while True:
            now = int(time.time() * 1000)
            # Remove timestamps outside the window
            self.timestamps = [t for t in self.timestamps if now - t < self.window_ms]

            if len(self.timestamps) < self.max_requests:
                self.timestamps.append(now)
                return

            # Calculate wait time
            oldest = self.timestamps[0]
            wait_time = (self.window_ms - (now - oldest)) / 1000.0
            if wait_time > 0:
                time.sleep(wait_time)


class Spider:
    def __init__(self, api_key: Optional[str] = None, ai_studio_tier: str = "starter"):
        """
        Initialize the Spider with an API key.

        :param api_key: A string of the API key for Spider. Defaults to the SPIDER_API_KEY environment variable.
        :param ai_studio_tier: AI Studio subscription tier for rate limiting. Options: starter, lite, standard, custom.
        :raises ValueError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("SPIDER_API_KEY")
        if self.api_key is None:
            raise ValueError("No API key provided")

        self.rate_limit = RateLimitState()
        self.ai_studio_tier = ai_studio_tier
        self._ai_rate_limiter = RateLimiter(
            AI_STUDIO_RATE_LIMITS.get(ai_studio_tier, 1)
        )

    def set_ai_studio_tier(self, tier: str):
        """
        Update the AI Studio subscription tier (adjusts rate limiting).

        :param tier: The subscription tier (starter, lite, standard, custom).
        """
        self.ai_studio_tier = tier
        self._ai_rate_limiter.set_limit(AI_STUDIO_RATE_LIMITS.get(tier, 1))

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=60),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type(requests.exceptions.RequestException),
    )
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

        self.rate_limit.update_from_headers(response.headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "1"))
            time.sleep(retry_after)
            raise requests.exceptions.RequestException(
                f"Rate limited on {endpoint}. Retrying after {retry_after}s."
            )

        if stream:
            return response
        elif 200 <= response.status_code < 300:
            return response.json()
        else:
            self._handle_error(response, f"post to {endpoint}")

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=60),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type(requests.exceptions.RequestException),
    )
    def api_get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Send a GET request to the specified endpoint.

        :param endpoint: The API endpoint from which to retrieve data.
        :param params: Query parameters to attach to the URL.
        :return: The JSON decoded response.
        """
        headers = self._prepare_headers(content_type)
        response = requests.get(
            f"https://api.spider.cloud/{endpoint}",
            headers=headers,
            params=params,
            stream=stream,
        )

        self.rate_limit.update_from_headers(response.headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "1"))
            time.sleep(retry_after)
            raise requests.exceptions.RequestException(
                f"Rate limited on {endpoint}. Retrying after {retry_after}s."
            )

        if 200 <= response.status_code < 300:
            return response.json()
        else:
            self._handle_error(response, f"get from {endpoint}")

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=60),
        stop=tenacity.stop_after_attempt(5),
    )
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
            f"https://api.spider.cloud/v1/{endpoint}",
            headers=headers,
            json=params,
            stream=stream,
        )
        if 200 <= response.status_code < 300:
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
        params: Optional[SearchRequestParams] = None,
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
        self,
        data,
        params: Optional[RequestParamsTransform] = None,
        stream=False,
        content_type="application/json",
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

    def unblock_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ):
        """
        Unblock data from the specified URL.

        :param url: The URL from which to scrape data.
        :param params: Optional dictionary of additional parameters for the scrape request.
        :return: JSON response containing the scraping results.
        """
        return self.api_post(
            "unblocker", {"url": url, "limit": 1, **(params or {})}, stream, content_type
        )

    def get_credits(self):
        """
        Retrieve the account's remaining credits.

        :return: JSON response containing the number of credits left.
        """
        return self.api_get("data/credits")

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

    def stream_reader(self, response, callback):
        response.raise_for_status()

        try:
            for json_obj in ijson.items(response.raw, "", multiple_values=True):
                callback(json_obj)

        except Exception as e:
            logging.error(f"An error occurred while parsing JSON: {e}")

    def _prepare_headers(self, content_type: str = "application/json"):
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"Spider-Client/0.1.87",
        }

    def _post_request(self, url: str, data, headers, stream=False):
        return requests.post(url, headers=headers, json=data, stream=stream)

    def _get_request(self, url: str, headers, stream=False, params=None):
        return requests.get(url, headers=headers, stream=stream, params=params)

    def _delete_request(self, url: str, headers, json=None, stream=False):
        return requests.delete(url, headers=headers, json=json, stream=stream)

    def _ai_api_post(self, endpoint: str, data: dict):
        """
        Internal method for AI Studio POST requests with rate limiting.

        :param endpoint: The AI Studio endpoint.
        :param data: Request data including prompt.
        :return: JSON response.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        :raises AIStudioRateLimitExceeded: When rate limit is exceeded.
        """
        # Apply client-side rate limiting
        self._ai_rate_limiter.acquire()

        headers = self._prepare_headers()
        response = requests.post(
            f"https://api.spider.cloud/{endpoint}", headers=headers, json=data
        )

        if 200 <= response.status_code < 300:
            return response.json()

        # Handle AI Studio specific errors
        if response.status_code == 402:
            raise AIStudioSubscriptionRequired()

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "1")
            retry_after_ms = int(retry_after) * 1000
            raise AIStudioRateLimitExceeded(retry_after_ms)

        self._handle_error(response, f"AI request to {endpoint}")

    def ai_crawl(
        self,
        url: str,
        prompt: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        AI-guided crawling using natural language prompts.
        Requires an active AI Studio subscription.

        :param url: The URL to start crawling.
        :param prompt: Natural language instruction for what to crawl and extract.
        :param params: Optional dictionary of additional parameters.
        :return: JSON response with crawl results.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        """
        return self._ai_api_post(
            "ai/crawl", {"url": url, "prompt": prompt, **(params or {})}
        )

    def ai_scrape(
        self,
        url: str,
        prompt: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        AI-guided scraping using natural language prompts.
        Requires an active AI Studio subscription.

        :param url: The URL to scrape.
        :param prompt: Natural language description of data to extract.
        :param params: Optional dictionary of additional parameters.
        :return: JSON response with scraped data.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        """
        return self._ai_api_post(
            "ai/scrape", {"url": url, "prompt": prompt, **(params or {})}
        )

    def ai_search(
        self,
        prompt: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        AI-enhanced web search using natural language queries.
        Requires an active AI Studio subscription.

        :param prompt: Natural language search query.
        :param params: Optional search parameters.
        :return: JSON response with search results.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        """
        return self._ai_api_post("ai/search", {"prompt": prompt, **(params or {})})

    def ai_browser(
        self,
        url: str,
        prompt: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        AI-guided browser automation using natural language commands.
        Requires an active AI Studio subscription.

        :param url: The URL to automate.
        :param prompt: Natural language description of browser actions.
        :param params: Optional dictionary of additional parameters.
        :return: JSON response with automation results.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        """
        return self._ai_api_post(
            "ai/browser", {"url": url, "prompt": prompt, **(params or {})}
        )

    def ai_links(
        self,
        url: str,
        prompt: str,
        params: Optional[RequestParamsDict] = None,
    ):
        """
        AI-guided link extraction and filtering.
        Requires an active AI Studio subscription.

        :param url: The URL to extract links from.
        :param prompt: Natural language description of what links to find.
        :param params: Optional dictionary of additional parameters.
        :return: JSON response with filtered links.
        :raises AIStudioSubscriptionRequired: When subscription is not active.
        """
        return self._ai_api_post(
            "ai/links", {"url": url, "prompt": prompt, **(params or {})}
        )

    def _handle_error(self, response, action):
        if response.status_code in [402, 409, 500]:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(
                f"Failed to {action}. Status code: {response.status_code}. Error: {error_message}"
            )
        else:
            raise Exception(
                f"Unexpected error occurred while trying to {action}. Status code: {response.status_code}. Here is the response: {response.text}"
            )
