from typing import TypedDict, Optional, Dict, List, Literal, Callable


class ChunkingAlgDict(TypedDict):
    # The chunking algorithm to use with the value to chunk by.
    type: Literal["ByWords", "ByLines", "ByCharacterLength", "BySentence"]
    # The amount to chunk by.
    value: int


class RequestParamsDict(TypedDict, total=False):
    # The URL to be crawled.
    url: Optional[str]

    # The type of request to be made.
    request: Optional[Literal["http", "chrome", "smart"]]

    # The maximum number of pages the crawler should visit.
    limit: Optional[int]

    # The format in which the result should be returned.
    return_format: Optional[
        Literal["raw", "markdown", "commonmark", "html2text", "text", "bytes"]
    ]

    # Specifies whether to only visit the top-level domain.
    tld: Optional[bool]

    # The depth of the crawl.
    depth: Optional[int]

    # Specifies whether the request should be cached.
    cache: Optional[bool]

    # The budget for various resources.
    budget: Optional[Dict[str, int]]

    # The locale to be used during the crawl.
    locale: Optional[str]

    # The cookies to be set for the request, formatted as a single string.
    cookies: Optional[str]

    # Specifies whether to use stealth techniques to avoid detection.
    stealth: Optional[bool]

    # The headers to be used for the request.
    headers: Optional[Dict[str, str]]

    # Specifies whether anti-bot measures should be used.
    anti_bot: Optional[bool]

    # Specifies whether to include metadata in the response.
    metadata: Optional[bool]

    # The dimensions of the viewport.
    viewport: Optional[Dict[str, int]]

    # The encoding to be used for the request.
    encoding: Optional[str]

    # Specifies whether to include subdomains in the crawl.
    subdomains: Optional[bool]

    # The user agent string to be used for the request.
    user_agent: Optional[str]

    # Specifies whether the response data should be stored.
    store_data: Optional[bool]

    # Configuration settings for GPT (general purpose texture mappings).
    gpt_config: Optional[List[str]]

    # Specifies whether to use fingerprinting protection.
    fingerprint: Optional[bool]

    # Specifies whether to perform the request without using storage.
    storageless: Optional[bool]

    # Specifies whether readability optimizations should be applied.
    readability: Optional[bool]

    # Specifies whether to use a proxy for the request.
    proxy_enabled: Optional[bool]

    # Specifies whether to respect the site's robots.txt file.
    respect_robots: Optional[bool]

    # CSS selector to be used to filter the content.
    query_selector: Optional[str]

    # Specifies whether to load all resources of the crawl target.
    full_resources: Optional[bool]

    # Specifies whether to use the sitemap links.
    sitemap: Optional[bool]

    # Get page insights to determine information like request duration, accessibility, and other web vitals. Requires the `metadata` parameter to be set to `true`.
    page_insights: Optional[bool]

    # Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
    return_embeddings: Optional[bool]

    # The timeout for the request, in milliseconds.
    request_timeout: Optional[int]

    # Specifies whether to run the request in the background.
    run_in_background: Optional[bool]

    # Specifies whether to skip configuration checks.
    skip_config_checks: Optional[bool]

    # The chunking algorithm to use.
    chunking_alg: Optional[ChunkingAlgDict]


JsonCallback = Callable[[dict], None]