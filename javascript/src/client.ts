import {
  ChunkCallbackFunction,
  Collection,
  SpiderCoreResponse,
  SpiderParams,
  SearchRequestParams,
  APISchema,
  APIRoutes,
  ApiVersion,
  RequestParamsTransform,
  AIRequestParams,
  AIStudioTier,
  AI_STUDIO_RATE_LIMITS,
  AIStudioSubscriptionRequired,
  AIStudioRateLimitExceeded,
} from "./config";
import { version } from "../package.json";
import { streamReader } from "./utils/stream-reader";
import { backOff } from "exponential-backoff";

/**
 * Simple client-side rate limiter for AI Studio endpoints.
 * Uses a sliding window approach to limit requests per second.
 */
class RateLimiter {
  private timestamps: number[] = [];
  private maxRequests: number;
  private windowMs: number;

  constructor(requestsPerSecond: number) {
    this.maxRequests = requestsPerSecond;
    this.windowMs = 1000;
  }

  /**
   * Update the rate limit (e.g., when user tier changes).
   */
  setLimit(requestsPerSecond: number) {
    this.maxRequests = requestsPerSecond;
  }

  /**
   * Check if a request can be made. If not, returns the ms to wait.
   * If yes, records the request and returns 0.
   */
  tryAcquire(): number {
    const now = Date.now();
    // Remove timestamps outside the window
    this.timestamps = this.timestamps.filter((t) => now - t < this.windowMs);

    if (this.timestamps.length >= this.maxRequests) {
      // Calculate how long to wait
      const oldestInWindow = this.timestamps[0];
      const waitTime = this.windowMs - (now - oldestInWindow);
      return Math.max(1, waitTime);
    }

    this.timestamps.push(now);
    return 0;
  }

  /**
   * Wait until a request can be made, then acquire the slot.
   */
  async acquire(): Promise<void> {
    const waitTime = this.tryAcquire();
    if (waitTime > 0) {
      await new Promise((resolve) => setTimeout(resolve, waitTime));
      return this.acquire();
    }
  }
}

/**
 * Generic params for core request.
 */
export type GenericParams = Omit<SpiderParams, "url">;

/**
 * Configuration interface for Spider.
 */
export interface SpiderConfig {
  apiKey?: string | null;
}

/**
 * A class to interact with the Spider API.
 */
export class Spider {
  private apiKey?: string;
  private aiRateLimiter: RateLimiter;
  private aiStudioTier: AIStudioTier;

  /**
   * Create an instance of Spider.
   * @param {string | null} apiKey - The API key used to authenticate to the Spider API. If null, attempts to source from environment variables.
   * @param {AIStudioTier} aiStudioTier - The AI Studio subscription tier for rate limiting. Defaults to 'starter'.
   * @throws Will throw an error if the API key is not provided.
   */
  constructor(props?: SpiderConfig & { aiStudioTier?: AIStudioTier }) {
    this.apiKey = props?.apiKey || process?.env?.SPIDER_API_KEY;
    this.aiStudioTier = props?.aiStudioTier || "starter";
    this.aiRateLimiter = new RateLimiter(
      AI_STUDIO_RATE_LIMITS[this.aiStudioTier]
    );

    if (!this.apiKey) {
      throw new Error("No API key provided");
    }
  }

  /**
   * Update the AI Studio subscription tier (adjusts rate limiting).
   * @param {AIStudioTier} tier - The new subscription tier.
   */
  setAIStudioTier(tier: AIStudioTier) {
    this.aiStudioTier = tier;
    this.aiRateLimiter.setLimit(AI_STUDIO_RATE_LIMITS[tier]);
  }

  /**
   * Internal method to handle POST requests.
   * @param {string} endpoint - The API endpoint to which the POST request should be sent.
   * @param {Record<string, any>} data - The JSON data to be sent in the request body.
   * @param {boolean} [stream=false] - Whether to stream the response back without parsing.
   * @returns {Promise<Response | any>} The response in JSON if not streamed, or the Response object if streamed.
   */
  private async _apiPost(
    endpoint: string,
    data: Record<string, any>,
    stream?: boolean,
    jsonl?: boolean
  ) {
    const headers = jsonl ? this.prepareHeadersJsonL : this.prepareHeaders;
    const response = await backOff(
      () =>
        fetch(`${APISchema["url"]}/${ApiVersion.V1}/${endpoint}`, {
          method: "POST",
          headers: headers,
          body: JSON.stringify(data),
        }),
      {
        numOfAttempts: 5,
      }
    );

    if (!stream) {
      if (response.ok) {
        return response.json();
      } else {
        this.handleError(response, `post to ${endpoint}`);
      }
    }
    return response;
  }

  /**
   * Internal method to handle GET requests.
   * @param {string} endpoint - The API endpoint from which data should be retrieved.
   * @returns {Promise<any>} The data returned from the endpoint in JSON format.
   */
  private async _apiGet(endpoint: string) {
    const headers = this.prepareHeaders;
    const response = await backOff(
      () =>
        fetch(`${APISchema["url"]}/${ApiVersion.V1}/${endpoint}`, {
          method: "GET",
          headers: headers,
        }),
      {
        numOfAttempts: 5,
      }
    );

    if (response.ok) {
      return response.json();
    } else {
      this.handleError(response, `get from ${endpoint}`);
    }
  }

  /**
   * Scrapes data from a specified URL.
   * @param {string} url - The URL to scrape.
   * @param {GenericParams} [params={}] - Additional parameters for the scraping request.
   * @returns {Promise<any>} The scraped data from the URL.
   */
  async scrapeUrl(url: string, params: GenericParams = {}) {
    return this._apiPost(APIRoutes.Crawl, { url: url, limit: 1, ...params });
  }

  /**
   * Initiates a crawling job starting from the specified URL.
   * @param {string} url - The URL to start crawling.
   * @param {GenericParams} [params={}] - Additional parameters for the crawl.
   * @param {boolean} [stream=false] - Whether to receive the response as a stream.
   * @param {function} [callback=function] - The callback function when streaming per chunk. If this is set with stream you will not get a end response.
   * @returns {Promise<any | Response>} The result of the crawl, either structured data or a Response object if streaming.
   */
  async crawlUrl(
    url: string,
    params: GenericParams = {},
    stream = false,
    cb?: ChunkCallbackFunction
  ): Promise<SpiderCoreResponse[] | void> {
    const jsonl = stream && cb;
    const res = await this._apiPost(
      APIRoutes.Crawl,
      { url, ...params },
      stream,
      !!jsonl
    );

    if (jsonl) {
      return await streamReader(res, cb);
    }

    return res;
  }

  /**
   * Retrieves all links from the specified URL.
   * @param {string} url - The URL from which to gather links.
   * @param {GenericParams} [params={}] - Additional parameters for the crawl.
   * @param {boolean} [stream=false] - Whether to receive the response as a stream.
   * @param {function} [callback=function] - The callback function when streaming per chunk. If this is set with stream you will not get a end response.
   * @returns {Promise<any | Response>} The result of the crawl, either structured data or a Response object if streaming.
   */
  async links(
    url: string,
    params: GenericParams = {},
    stream = false,
    cb?: ChunkCallbackFunction
  ): Promise<SpiderCoreResponse[] | void> {
    const jsonl = stream && cb;
    const res = await this._apiPost(
      APIRoutes.Links,
      { url, ...params },
      stream,
      !!jsonl
    );

    if (jsonl) {
      return await streamReader(res, cb);
    }

    return res;
  }

  /**
   * Takes a screenshot of the website starting from this URL.
   * @param {string} url - The URL to start the screenshot.
   * @param {GenericParams} [params={}] - Configuration parameters for the screenshot.
   * @returns {Promise<any>} The screenshot data.
   */
  async screenshot(url: string, params: GenericParams = {}) {
    return this._apiPost(APIRoutes.Screenshot, { url: url, ...params });
  }

  /**
   * Unblock a challenging url to get data.
   * @param {string} url - The URL to get data from.
   * @param {GenericParams} [params={}] - Configuration parameters for the screenshot.
   * @returns {Promise<any>} The screenshot data.
   */
  async unblocker(url: string, params: GenericParams = {}) {
    return this._apiPost(APIRoutes.Unblocker, { url: url, ...params });
  }

  /**
   *  Perform a search and gather a list of websites to start crawling and collect resources.
   * @param {string} search - The search query.
   * @param {GenericParams} [params={}] - Configuration parameters for the search.
   * @returns {Promise<any>} The result of the crawl, either structured data or a Response object if streaming.
   */
  async search(q: string, params: SearchRequestParams = {}) {
    return this._apiPost(APIRoutes.Search, { search: q, ...params });
  }

  /**
   *  Transform HTML to Markdown or text. You can send up to 10MB of data at once.
   * @param {object} data - The data to trasnform, a list of objects with the key 'html' and optional 'url' key for readability.
   * @param {object} [params={}] - Configuration parameters for the transformation.
   * @returns {Promise<any>} The transformation result.
   */
  async transform(
    data: { html: string; url?: string }[],
    params?: RequestParamsTransform
  ) {
    return this._apiPost(APIRoutes.Transform, {
      ...(params ? params : {}),
      data:
        params?.data && Array.isArray(params.data) && params.data?.length
          ? params.data
          : data,
    });
  }

  /**
   * Retrieves the number of credits available on the account.
   * @returns {Promise<any>} The current credit balance.
   */
  async getCredits() {
    return this._apiGet(APIRoutes.DataCredits);
  }

  /**
   * Send a POST request to insert data into a specified table.
   * @param {string} table - The table name in the database.
   * @param {object} data - The data to be inserted.
   * @returns {Promise<any>} The response from the server.
   */
  async postData(
    collection: Collection,
    data: GenericParams | Record<string, any>
  ): Promise<any> {
    return this._apiPost(`${APIRoutes.Data}/${collection}`, data);
  }

  /**
   * Prepares common headers for each API request.
   * @returns {HeadersInit} A headers object for fetch requests.
   */
  get prepareHeaders() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
      "User-Agent": `Spider-Client/${version}`,
    };
  }

  /**
   * Prepares common headers for each API request with JSONl content-type suitable for streaming.
   * @returns {HeadersInit} A headers object for fetch requests.
   */
  get prepareHeadersJsonL() {
    return {
      ...this.prepareHeaders,
      "Content-Type": "application/jsonl",
    };
  }

  /**
   * Internal method to handle AI Studio POST requests with rate limiting.
   * @param {string} endpoint - The AI Studio endpoint.
   * @param {Record<string, any>} data - The request data including prompt.
   * @returns {Promise<any>} The response data.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   * @throws {AIStudioRateLimitExceeded} When rate limit is exceeded server-side.
   */
  private async _aiApiPost(
    endpoint: string,
    data: Record<string, any>
  ): Promise<any> {
    // Apply client-side rate limiting
    await this.aiRateLimiter.acquire();

    const headers = this.prepareHeaders;
    const response = await backOff(
      () =>
        fetch(`${APISchema["url"]}/${ApiVersion.V1}/${endpoint}`, {
          method: "POST",
          headers: headers,
          body: JSON.stringify(data),
        }),
      {
        numOfAttempts: 3,
        retry: (e, attemptNumber) => {
          // Don't retry on subscription or rate limit errors
          return attemptNumber < 3;
        },
      }
    );

    if (response.ok) {
      return response.json();
    }

    // Handle AI Studio specific errors
    if (response.status === 402) {
      throw new AIStudioSubscriptionRequired();
    }

    if (response.status === 429) {
      const retryAfter = response.headers.get("Retry-After");
      const retryAfterMs = retryAfter ? parseInt(retryAfter) * 1000 : 1000;
      throw new AIStudioRateLimitExceeded(retryAfterMs);
    }

    this.handleError(response, `AI request to ${endpoint}`);
  }

  /**
   * AI-guided crawling using natural language prompts.
   * Requires an active AI Studio subscription.
   * @param {string} url - The URL to start crawling.
   * @param {string} prompt - Natural language instruction for what to crawl and extract.
   * @param {AIRequestParams} [params={}] - Additional parameters for the crawl.
   * @returns {Promise<any>} The crawl results guided by the AI prompt.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   */
  async aiCrawl(
    url: string,
    prompt: string,
    params: Omit<AIRequestParams, "prompt"> = {}
  ): Promise<any> {
    return this._aiApiPost(APIRoutes.AICrawl, { url, prompt, ...params });
  }

  /**
   * AI-guided scraping using natural language prompts.
   * Requires an active AI Studio subscription.
   * @param {string} url - The URL to scrape.
   * @param {string} prompt - Natural language description of data to extract.
   * @param {AIRequestParams} [params={}] - Additional parameters for the scrape.
   * @returns {Promise<any>} The scraped data guided by the AI prompt.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   */
  async aiScrape(
    url: string,
    prompt: string,
    params: Omit<AIRequestParams, "prompt"> = {}
  ): Promise<any> {
    return this._aiApiPost(APIRoutes.AIScrape, { url, prompt, ...params });
  }

  /**
   * AI-enhanced web search using natural language queries.
   * Requires an active AI Studio subscription.
   * @param {string} prompt - Natural language search query.
   * @param {SearchRequestParams} [params={}] - Additional search parameters.
   * @returns {Promise<any>} The search results with AI-enhanced relevance.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   */
  async aiSearch(
    prompt: string,
    params: SearchRequestParams = {}
  ): Promise<any> {
    return this._aiApiPost(APIRoutes.AISearch, { prompt, ...params });
  }

  /**
   * AI-guided browser automation using natural language commands.
   * Requires an active AI Studio subscription.
   * @param {string} url - The URL to automate.
   * @param {string} prompt - Natural language description of browser actions.
   * @param {AIRequestParams} [params={}] - Additional parameters for automation.
   * @returns {Promise<any>} The automation results.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   */
  async aiBrowser(
    url: string,
    prompt: string,
    params: Omit<AIRequestParams, "prompt"> = {}
  ): Promise<any> {
    return this._aiApiPost(APIRoutes.AIBrowser, { url, prompt, ...params });
  }

  /**
   * AI-guided link extraction and filtering.
   * Requires an active AI Studio subscription.
   * @param {string} url - The URL to extract links from.
   * @param {string} prompt - Natural language description of what links to find.
   * @param {AIRequestParams} [params={}] - Additional parameters.
   * @returns {Promise<any>} The filtered links based on AI analysis.
   * @throws {AIStudioSubscriptionRequired} When subscription is not active.
   */
  async aiLinks(
    url: string,
    prompt: string,
    params: Omit<AIRequestParams, "prompt"> = {}
  ): Promise<any> {
    return this._aiApiPost(APIRoutes.AILinks, { url, prompt, ...params });
  }

  /**
   * Handles errors from API requests.
   * @param {Response} response - The fetch response object.
   * @param {string} action - Description of the attempted action.
   * @throws Will throw an error with detailed status information.
   */
  handleError(response: Response, action: string) {
    throw new Error(`Failed to ${action}. Status code: ${response.status}.`);
  }
}
