/**
 * Represents viewport dimensions.
 */
export interface Viewport {
  width: number;
  height: number;
}

/**
 * Represents HTTP headers as a dictionary object.
 */
export interface Headers {
  [key: string]: string;
}

/**
 * Represents a budget for various resources.
 */
export interface Budget {
  [key: string]: number;
}

/**
 * The chunking algorithm to use.
 */
export type ChunkingAlgType =
  | "ByWords"
  | "ByLines"
  | "ByCharacterLength"
  | "BySentence";

/**
 * The chunking algorithm with the value to chunk by.
 */
export interface ChunkingAlg {
  type: ChunkingAlgType;
  value: number;
}

/**
 * Represents a timeout configuration.
 * @typedef {Object} Timeout
 * @property {number} secs - The number of seconds.
 * @property {number} nanos - The number of nanoseconds.
 */
interface Timeout {
  secs: number;
  nanos: number;
}

/**
 * Represents the webhook configuration.
 * @typedef {Object} WebhookSettings
 * @property {Object} object - The webhook configuration.
 */
interface WebhookSettings {
  /**
   * The URL or endpoint where the webhook information will be sent.
   */
  destination: string;
  /**
   * Flag to indicate an action should be taken when all credits are depleted.
   */
  on_credits_depleted: boolean;
  /**
   * Flag to indicate an action should be taken when half of the credits are depleted.
   */
  on_credits_half_depleted: boolean;
  /**
   * Flag to trigger a notification on a website status update event.
   */
  on_website_status: boolean;
  /**
   * Flag to send information about a new page find, such as links and data size.
   */
  on_find: boolean;
  /**
   * Flag to handle the metadata of a new page that has been found.
   */
  on_find_metadata: boolean;
}

/**
 * Represents the idle network configuration.
 * @typedef {Object} IdleNetwork
 * @property {Timeout} timeout - The timeout configuration.
 */
interface IdleNetwork {
  timeout: Timeout;
}

/**
 * Represents the selector configuration.
 * @typedef {Object} Selector
 * @property {Timeout} timeout - The timeout configuration.
 * @property {string} selector - The CSS selector to wait for.
 */
interface Selector {
  timeout: Timeout;
  selector: string;
}

/**
 * Represents the delay configuration.
 * @typedef {Object} Delay
 * @property {Timeout} timeout - The timeout configuration.
 */
interface Delay {
  timeout: Timeout;
}

/**
 * Represents the wait_for configuration.
 * @typedef {Object} WaitFor
 * @property {IdleNetwork} [idle_network] - Configuration to wait for network to be idle.
 * @property {Selector} [selector] - Configuration to wait for a CSS selector.
 * @property {Delay} [delay] - Configuration to wait for a delay.
 * @property {boolean} [page_navigations] - Whether to wait for page navigations.
 */
interface WaitFor {
  idle_network?: IdleNetwork;
  selector?: Selector;
  delay?: Delay;
  page_navigations?: boolean;
}

/**
 * Represents the query API endpoint request to get documents from the global spider collection.
 */
export interface QueryRequest {
  /**
   * The exact URL to get.
   */
  url?: string;
  /**
   * The domain to get a document from.
   */
  domain?: string;
  /**
   * The path of the webpage to get the document. This is used with the domain key.
   */
  pathname?: string;
}

// Define the CSSSelector type
type CSSSelector = {
  // The name of the selector group
  name: string;
  // An array of CSS selectors
  selectors: string[];
};

// Define the CSSExtractionMap type
type CSSExtractionMap = {
  // The map keys are strings (paths), and the values are arrays of CSSSelector objects
  [path: string]: CSSSelector[];
};

// Web automation using chrome
export type WebAutomation =
  | { Evaluate: string }
  | { Click: string }
  | { Wait: number }
  | { WaitForNavigation: boolean }
  | { WaitFor: string }
  | { WaitForAndClick: string }
  | { ScrollX: number }
  | { ScrollY: number }
  | { Fill: { selector: string; value?: string } }
  | { InfiniteScroll: number };

export type ReturnFormat =
  | "markdown"
  | "commonmark"
  | "raw"
  | "text"
  | "html2text"
  | "bytes"
  | "xml"
  | "empty";

// Map automation scripts for paths or urls.
export type WebAutomationMap = Record<string, WebAutomation[]>;
// Map execution scripts for paths or urls.
export type ExecutionScriptsMap = Record<string, string>;

// The HTTP redirect policy to use. Loose allows all domains and Strict only allows relative requests to the domain.
export enum RedirectPolicy {
  Loose = "Loose",
  Strict = "Strict",
}

/**
 * Proxy pool selection for outbound request routing.
 * Choose a pool based on your use case (e.g., stealth, speed, or stability).
 *
 * - 'residential'         → cost-effective entry-level residential pool
 * - 'residential_fast'    → faster residential pool for higher throughput
 * - 'residential_static'  → static residential IPs, rotated daily
 * - 'mobile'              → 4G/5G mobile proxies for maximum evasion
 * - 'isp'                 → ISP-grade residential (alias: 'datacenter')
 * - 'residential_premium' → low-latency premium IPs
 * - 'residential_core'    → balanced plan (quality vs. cost)
 * - 'residential_plus'    → largest and highest quality core pool
 */
export type Proxy =
  | "residential"
  | "residential_fast"
  | "residential_static"
  | "mobile"
  | "isp"
  | "residential_premium"
  | "residential_core"
  | "residential_plus";

/**
 * Represents the options available for making a spider request.
 */
export interface SpiderParams {
  /**
   * The URL to be crawled.
   */
  url: string;

  /**
   * The type of request to be made.
   */
  request?: "http" | "chrome" | "smart";

  /**
   * The maximum number of pages the crawler should visit.
   */
  limit?: number;

  /**
   * The format in which the result should be returned. When setting the return format as an array a object is returned mapping by the name.
   */
  return_format?: ReturnFormat | ReturnFormat[];

  /**
   * Specifies whether to only visit the top-level domain.
   */
  tld?: boolean;

  /**
   * The depth of the crawl.
   */
  depth?: number;

  /**
   * Specifies whether the request should be cached.
   */
  cache?: boolean;

  /**
   * The budget for various resources.
   */
  budget?: Budget;

  /**
   * The blacklist routes to ignore. This can be a Regex string pattern.
   */
  blacklist?: string[];

  /**
   * The whitelist routes to only crawl. This can be a Regex string pattern and used with black_listing.
   */
  whitelist?: string[];

  /**
   * The locale to be used during the crawl.
   */
  locale?: string;

  /**
   * The cookies to be set for the request, formatted as a single string.
   */
  cookies?: string;

  /**
   * Specifies whether to use stealth techniques to avoid detection.
   */
  stealth?: boolean;

  /**
   * The headers to be used for the request.
   */
  headers?: Headers;

  /**
   * Specifies whether anti-bot measures should be used.
   */
  anti_bot?: boolean;

  /**
   * Specifies whether to include metadata in the response.
   */
  metadata?: boolean;

  /**
   * Use CSS query selectors to scrape contents from the web page. Set the paths and the CSS extraction object map to perform extractions per path or page.
   */
  css_extraction_map?: CSSExtractionMap;

  /**
   * The dimensions of the viewport.
   */
  viewport?: Viewport;

  /**
   * The encoding to be used for the request.
   */
  encoding?: "UTF-8" | "SHIFT_JIS" | string;

  /**
   * Specifies whether to include subdomains in the crawl.
   */
  subdomains?: boolean;

  /**
   * The user agent string to be used for the request.
   */
  user_agent?: string;

  /**
   * Specifies whether the response data should be stored.
   */
  store_data?: boolean;

  /**
   * Use webhooks to send data.
   */
  webhooks?: WebhookSettings;
  /**
   * Configuration settings for GPT (general purpose texture mappings).
   */
  gpt_config?: Record<string, any>;

  /**
   * Specifies whether to use fingerprinting protection.
   */
  fingerprint?: boolean;

  /**
   * Specifies whether to perform the request without using storage.
   */
  storageless?: boolean;

  /**
   * Specifies whether readability optimizations should be applied.
   */
  readability?: boolean;

  /**
   * Specifies whether to use a proxy for the request. [Deprecated]: use the 'proxy' param instead.
   */
  proxy_enabled?: boolean;

  /**
   * Specifies whether to respect the site's robots.txt file.
   */
  respect_robots?: boolean;

  /**
   * CSS root selector to be used to filter the content.
   */
  root_selector?: string;

  /**
   * Specifies whether to load all resources of the crawl target.
   */
  full_resources?: boolean;

  /**
   * Specifies whether to use the sitemap links.
   */
  sitemap?: boolean;

  /**
   * Specifies whether to only use the sitemap links.
   */
  sitemap_only?: boolean;

  /**
   * External domains to include the crawl.
   */

  external_domains?: string[];

  /**
   * Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
   */
  return_embeddings?: boolean;

  /**
   * Returns the HTTP response headers used.
   */
  return_headers?: boolean;

  /**
   * Returns the link(s) found on the page that match the crawler query.
   */
  return_page_links?: boolean;

  /**
   * Returns the HTTP response cookies used.
   */
  return_cookies?: boolean;

  /**
   * The timeout for the request, in milliseconds.
   */
  request_timeout?: Timeout;

  /**
   * Specifies whether to run the request in the background.
   */
  run_in_background?: boolean;

  /**
   *  Perform an infinite scroll on the page as new content arises. The request param also needs to be set to 'chrome' or 'smart'.
   */

  scroll?: number;

  /**
   * Specifies whether to skip configuration checks.
   */
  skip_config_checks?: boolean;

  /**
   * The chunking algorithm to use.
   */
  chunking_alg?: ChunkingAlg;

  /**
   * The wait for events on the page. You need to make your `request` `chrome` or `smart`.
   */
  wait_for?: WaitFor;

  /**
   * Disable request interception when running 'request' as 'chrome' or 'smart'. This can help when the page uses 3rd party or external scripts to load content.
   */
  disable_intercept?: boolean;

  /**
   * Perform custom web automated tasks on a url or url path. You need to make your `request` `chrome` or `smart`.
   */
  automation_scripts?: WebAutomationMap;

  /**
   * Perform custom Javascript tasks on a url or url path. You need to make your `request` `chrome` or `smart`.
   */
  execution_scripts?: ExecutionScriptsMap;

  /**
   * The redirect policy for HTTP request. Set the value to Loose to allow all.
   */
  redirect_policy?: RedirectPolicy;

  /**
   * Track the request sent and responses received for `chrome` or `smart`. The responses will track the bytes used and the requests will have the monotime sent.
   */
  event_tracker?: {
    responses?: true;
    requests?: true;
  };

  /**
   * The timeout to stop the crawl.
   */
  crawl_timeout?: Timeout;

  /**
   * Evaluates given script in every frame upon creation (before loading frame's scripts).
   */
  evaluate_on_new_document?: string;
  /**
   * Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy,
   * geo-targeting, and reliability. It’s best suited for non-urgent data collection or when
   * targeting websites with minimal anti-bot protections.
   */
  lite_mode?: boolean;

  /**
   * Set the maximum number of credits to use per page.
   * Credits are measured in decimal units, where 10,000 credits equal one dollar (100 credits per penny).
   * Credit limiting only applies to request that are Javascript rendered using smart_mode or chrome for the 'request' type.
   */
  max_credits_per_page?: number;

  /**
   * Proxy pool selection for outbound request routing.
   * Choose a pool based on your use case (e.g., stealth, speed, or stability).
   *
   * - 'residential'         → cost-effective entry-level residential pool
   * - 'residential_fast'    → faster residential pool for higher throughput
   * - 'residential_static'  → static residential IPs, rotated daily
   * - 'mobile'              → 4G/5G mobile proxies for maximum evasion
   * - 'isp'                 → ISP-grade residential (alias: 'datacenter')
   * - 'residential_premium' → low-latency premium IPs
   * - 'residential_core'    → balanced plan (quality vs. cost)
   * - 'residential_plus'    → largest and highest quality core pool
   */
  proxy?: Proxy;

  /**
   * Use a remote proxy at ~70% reduced cost for file downloads.
   * This requires bringing your own proxy (e.g., static IP tunnel).
   */
  remote_proxy?: string;
}

// Core actions response type.
export type SpiderCoreResponse = {
  // The content of the request like html or transformation markdown etc.
  content?: string;
  // A detailed message of a response.
  message?: string;
  // If an error occured.
  error?: string;
  // The HTTP status code.
  status?: number;
  // The website url.
  url?: string;
};

export type ChunkCallbackFunction = (data: SpiderCoreResponse) => void;

// records that you can query
export enum Collection {
  Websites = "websites",
  Pages = "pages",
  PagesMetadata = "pages_metadata",
  // Leads
  Contacts = "contacts",
  CrawlState = "crawl_state",
  CrawlLogs = "crawl_logs",
  Profiles = "profiles",
  Credits = "credits",
  Webhooks = "webhooks",
  APIKeys = "api_keys",
}

// The API version for Spider
export enum ApiVersion {
  V1 = "v1",
}

// The API routes paths.
export enum APIRoutes {
  // Crawl a website to collect the contents. Can be one page or many.
  Crawl = "crawl",
  // Crawl a website to collect the links. Can be one page or many.
  Links = "links",
  // Crawl a website to collect screenshots. Can be one page or many.
  Screenshot = "screenshot",
  // Search for something and optionally crawl the pages or get the results of the search.
  Search = "search",
  // Transform HTML to markdown or text.
  Transform = "transform",
  // Pipeline extract leads for a website - emails, phones, etc.
  PiplineExtractLeads = "pipeline/extract-contacts",
  // Pipeline label a website by category using AI and metadata.
  PiplineLabel = "pipeline/label",
  // Dynamic collection routes.
  Data = "data",
  // The last crawl state of a website.
  DataCrawlState = "data/crawl_state",
  // Sign a file from storage based on the exact url path of the storage or domain - pathname.
  DataSignUrl = "data/sign-url",
  // Download a file from storage based on the exact url path of the storage or domain - pathname.
  DataDownload = "data/download",
  // Perform a query on the global database to grab content without crawling if available.
  DataQuery = "data/query",
  // Get the credits remaining for an account.
  DataCredits = "data/credits",
}

// The base API target info for Spider Cloud.
export const APISchema = {
  url: "https://api.spider.cloud",
  versions: {
    current: ApiVersion.V1,
    v1: {
      routes: APIRoutes,
      end_date: "",
    },
    latest: {
      routes: APIRoutes,
      end_date: "",
    },
  },
};

// Adjust the Spider Cloud endpoint.
export const setBaseUrl = (url: string) => {
  if (url) {
    APISchema["url"] = url;
  }
};
