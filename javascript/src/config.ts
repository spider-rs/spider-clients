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
   * The format in which the result should be returned.
   */
  return_format?:
    | "markdown"
    | "commonmark"
    | "raw"
    | "text"
    | "html2text"
    | "bytes";

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
   * Configuration settings for GPT (general purpose texture mappings).
   */
  gpt_config?: string[];

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
   * Specifies whether to use a proxy for the request.
   */
  proxy_enabled?: boolean;

  /**
   * Specifies whether to respect the site's robots.txt file.
   */
  respect_robots?: boolean;

  /**
   * CSS selector to be used to filter the content.
   */
  query_selector?: string;

  /**
   * Specifies whether to load all resources of the crawl target.
   */
  full_resources?: boolean;

  /**
   * Specifies whether to use the sitemap links.
   */
  sitemap?: boolean;

  /**
   * Get page insights to determine information like request duration, accessibility, and other web vitals. Requires the `metadata` parameter to be set to `true`.
   */
  page_insights?: boolean;

  /**
   * Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
   */
  return_embeddings?: boolean;

  /**
   * The timeout for the request, in milliseconds.
   */
  request_timeout?: number;

  /**
   * Specifies whether to run the request in the background.
   */
  run_in_background?: boolean;

  /**
   * Specifies whether to skip configuration checks.
   */
  skip_config_checks?: boolean;

  /**
   * The chunking algorithm to use.
   */
  chunking_alg?: ChunkingAlg;
}
