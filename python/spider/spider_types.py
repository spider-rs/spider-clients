from typing import TypedDict, Optional, Dict, List, Union, Literal, Callable
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Evaluate:
    code: str
    type: str = "Evaluate"

@dataclass
class Click:
    selector: str
    type: str = "Click"

@dataclass
class Wait:
    duration: int
    type: str = "Wait"

@dataclass
class WaitForNavigation:
    type: str = "WaitForNavigation"

@dataclass
class WaitFor:
    selector: str
    type: str = "WaitFor"

@dataclass
class WaitForAndClick:
    selector: str
    type: str = "WaitForAndClick"

@dataclass
class ScrollX:
    pixels: int
    type: str = "ScrollX"

@dataclass
class ScrollY:
    pixels: int
    type: str = "ScrollY"

@dataclass
class Fill:
    selector: str
    value: str
    type: str = "Fill"

@dataclass
class InfiniteScroll:
    times: int
    type: str = "InfiniteScroll"

WebAutomation = Union[
    Evaluate,
    Click,
    Wait,
    WaitForNavigation,
    WaitFor,
    WaitForAndClick,
    ScrollX,
    ScrollY,
    Fill,
    InfiniteScroll,
]

WebAutomationMap = Dict[str, List[WebAutomation]]
ExecutionScriptsMap = Dict[str, str]

RedirectPolicy = Literal[
    "Loose",
    "Strict"
]

@dataclass
class QueryRequest:
    url: Optional[str] = field(default=None)
    domain: Optional[str] = field(default=None)
    pathname: Optional[str] = field(default=None)


class ChunkingAlgDict(TypedDict):
    # The chunking algorithm to use with the value to chunk by.
    type: Literal["ByWords", "ByLines", "ByCharacterLength", "BySentence"]
    # The amount to chunk by.
    value: int


class TimeoutDict(TypedDict):
    secs: int
    nanos: int

class EventTracker(TypedDict):
    responses: bool
    requests: bool

class IdleNetworkDict(TypedDict):
    timeout: TimeoutDict


class SelectorDict(TypedDict):
    timeout: TimeoutDict
    selector: str


class DelayDict(TypedDict):
    timeout: TimeoutDict


class WaitForDict(TypedDict, total=False):
    idle_network: Optional[IdleNetworkDict]
    selector: Optional[SelectorDict]
    dom: Optional[SelectorDict]
    delay: Optional[DelayDict]
    page_navigations: Optional[bool]


@dataclass
class WebhookSettings:
    # The destination where the webhook data is sent via HTTP POST.
    destination: str
    # Flag to trigger an action when all credits are depleted
    on_credits_depleted: bool
    # Flag to trigger when half of the credits are depleted
    on_credits_half_depleted: bool
    # Flag to notify on website status update events
    on_website_status: bool
    # Flag to send information (links, bytes) about a new page find
    on_find: bool
    # Flag to handle the metadata of a found page
    on_find_metadata: bool

class CSSSelector(TypedDict):
    """
    Represents a set of CSS selectors grouped under a common name.
    """

    name: str  # The name of the selector group (e.g., "headers")
    selectors: List[str]  # A list of CSS selectors (e.g., ["h1", "h2", "h3"])


# CSSExtractionMap is a dictionary where:
# - Keys are strings representing paths (e.g., "/blog")
# - Values are lists of CSSSelector items
CSSExtractionMap = Dict[str, List[CSSSelector]]

ReturnFormat = Literal["raw", "markdown", "commonmark", "screenshot", "html2text", "text", "xml", "bytes"];

class Proxy(str, Enum):
    residential = "residential"                      # Residential basic pool
    residential_fast = "residential_fast"            # High-throughput residential pool
    residential_static = "residential_static"        # Static residential IPs (daily rotation)
    mobile = "mobile"                                # 4G/5G mobile proxies
    isp = "isp"                                       # ISP-level residential (alias: datacenter)
    residential_premium = "residential_premium"      # Low-latency premium pool
    residential_core = "residential_core"            # Balanced core plan
    residential_plus = "residential_plus"            # Extended core pool

class RequestParamsDict(TypedDict, total=False):
    # The URL to be crawled.
    url: Optional[str]

    # The type of request to be made.
    request: Optional[Literal["http", "chrome", "smart"]]

    # The maximum number of pages the crawler should visit.
    limit: Optional[int]

    # The format in which the result should be returned.
    return_format: Optional[
       Union[
           ReturnFormat,
           List[ReturnFormat],
       ]
    ]

    # Specifies whether to only visit the top-level domain.
    tld: Optional[bool]

    # The depth of the crawl.
    depth: Optional[int]

    # Specifies whether the request should be cached.
    cache: Optional[bool]

    # The budget for various resources.
    budget: Optional[Dict[str, int]]

    # The blacklist routes to ignore. This can be a Regex string pattern.
    blacklist: Optional[List[str]]

    # The whitelist routes to only crawl. This can be a Regex string pattern and used with black_listing.
    whitelist: Optional[List[str]]

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

    # The two letter country code for the request geo-location.
    country_code: Optional[str]

    # Configuration settings for GPT (general purpose texture mappings).
    gpt_config: Optional[Dict]

    # Specifies whether to use fingerprinting protection.
    fingerprint: Optional[bool]

    # Use CSS query selectors to scrape contents from the web page. Set the paths and the CSS extraction object map to perform extractions per path or page.
    css_extraction_map: Optional[CSSExtractionMap]

    # Specifies whether to perform the request without using storage.
    storageless: Optional[bool]

    # Specifies whether readability optimizations should be applied.
    readability: Optional[bool]

    # Specifies whether to use a proxy for the request. [Deprecated]: use the 'proxy' param instead.
    proxy_enabled: Optional[bool]

    # Specifies whether to respect the site's robots.txt file.
    respect_robots: Optional[bool]

    # CSS selector to be used to filter the content.
    root_selector: Optional[str]

    # Specifies whether to load all resources of the crawl target.
    full_resources: Optional[bool]

    # Specifies whether to use the sitemap links.
    sitemap: Optional[bool]

    # Specifies whether to only use the sitemap links.
    sitemap_only: Optional[bool]

    # External domains to include in the crawl.
    external_domains: Optional[List[str]]

    # Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
    return_embeddings: Optional[bool]

    # Use webhooks to send data to another location via POST.
    webhooks: Optional[WebhookSettings]

    # Returns the link(s) found on the page that match the crawler query.
    return_page_links: Optional[bool]

    # Returns the HTTP response headers used.
    return_headers: Optional[bool]

    # Returns the HTTP response cookies used.
    return_cookies: Optional[bool]

    # The timeout for the request, in milliseconds.
    request_timeout: Optional[int]

    # Perform an infinite scroll on the page as new content arises. The request param also needs to be set to 'chrome' or 'smart'.
    scroll: Optional[int]

    # Specifies whether to run the request in the background.
    run_in_background: Optional[bool]

    # Specifies whether to skip configuration checks.
    skip_config_checks: Optional[bool]

    # The chunking algorithm to use.
    chunking_alg: Optional[ChunkingAlgDict]

    # Disable request interception when running 'request' as 'chrome' or 'smart'. This can help when the page uses 3rd party or external scripts to load content.
    disable_intercept: Optional[bool]

    # The wait for events on the page. You need to make your `request` `chrome` or `smart`.
    wait_for: Optional[WaitForDict]

    # Perform custom Javascript tasks on a url or url path. You need to make your `request` `chrome` or `smart`.
    exuecution_scripts: Optional[ExecutionScriptsMap]

    # Perform custom web automated tasks on a url or url path. You need to make your `request` `chrome` or `smart`.
    automation_scripts: Optional[WebAutomationMap]

    # The redirect policy for HTTP request. Set the value to Loose to allow all.
    redirect_policy: Optional[RedirectPolicy]

    # Track the request sent and responses received for `chrome` or `smart`. The responses will track the bytes used and the requests will have the monotime sent.
    event_tracker: Optional[EventTracker]

    # The timeout to stop the crawl.
    crawl_timeout: Optional[TimeoutDict]

    # Evaluates given script in every frame upon creation (before loading frame's scripts).
    evaluate_on_new_document: Optional[str]

    # Set the maximum number of credits to use per page. 
    # Credits are measured in decimal units, where 10,000 credits equal one dollar (100 credits per penny).
    # Credit limiting only applies to request that are Javascript rendered using smart_mode or chrome for the 'request' type.
    max_credits_per_page: Optional[float]

    #  Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy,
    #  geo-targeting, and reliability. It’s best suited for non-urgent data collection or when
    #  targeting websites with minimal anti-bot protections.
    lite_mode: Optional[bool]

    # Proxy pool selection for outbound request routing.
    # Choose a pool based on your use case (e.g., stealth, speed, or stability).
    # - 'residential'           → cost-effective entry-level residential pool
    # - 'residential_fast'      → faster residential pool for higher throughput
    # - 'residential_static'    → static residential IPs, rotated daily
    # - 'mobile'                → 4G/5G mobile proxies for maximum evasion
    # - 'isp'                   → ISP-grade residential (alias: 'datacenter')
    # - 'residential_premium'   → low-latency premium IPs
    # - 'residential_core'      → balanced plan (quality vs. cost)
    # - 'residential_plus'      → largest and highest quality core pool
    proxy: Optional[Proxy] = None

    # Use a remote proxy at ~70% reduced cost for file downloads - bring your own proxy.
    remote_proxy: Optional[str]

JsonCallback = Callable[[dict], None]
