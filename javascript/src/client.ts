import {
  ChunkCallbackFunction,
  Collection,
  QueryRequest,
  SpiderCoreResponse,
  SpiderParams,
} from "./config";
import { version } from "../package.json";
import { Supabase } from "./supabase";
import { streamReader } from "./utils/stream-reader";

export const BASE_API_URL = "https://api.spider.cloud";

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

  /**
   * Create an instance of Spider.
   * @param {string | null} apiKey - The API key used to authenticate to the Spider API. If null, attempts to source from environment variables.
   * @throws Will throw an error if the API key is not provided.
   */
  constructor(props?: SpiderConfig) {
    this.apiKey = props?.apiKey || process?.env?.SPIDER_API_KEY;

    if (!this.apiKey) {
      throw new Error("No API key provided");
    }
  }

  /**
   * Init a supabase client.
   */
  async init_supabase() {
    return await Supabase.init();
  }

  /**
   *  The supabase client to manage data.
   */
  get supabase() {
    return Supabase.client;
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
    jsonl?: boolean,
  ) {
    const headers = jsonl ? this.prepareHeadersJsonL : this.prepareHeaders;
    const response = await fetch(`${BASE_API_URL}/v1/${endpoint}`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(data),
    });

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
    const response = await fetch(`${BASE_API_URL}/v1/${endpoint}`, {
      method: "GET",
      headers: headers,
    });

    if (response.ok) {
      return response.json();
    } else {
      this.handleError(response, `get from ${endpoint}`);
    }
  }

  /**
   * Internal method to handle DELETE requests.
   * @param {string} endpoint - The API endpoint from which data should be retrieved.
   * @returns {Promise<any>} The data returned from the endpoint in JSON format.
   */
  private async _apiDelete(endpoint: string) {
    const headers = this.prepareHeaders;
    const response = await fetch(`${BASE_API_URL}/v1/${endpoint}`, {
      method: "DELETE",
      headers,
    });

    if (response.ok) {
      return response;
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
    return this._apiPost("crawl", { url: url, limit: 1, ...params });
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
    cb?: ChunkCallbackFunction,
  ): Promise<SpiderCoreResponse[] | void> {
    const jsonl = stream && cb;
    const res = await this._apiPost(
      "crawl",
      { url: url, ...params },
      stream,
      !!jsonl,
    );

    if (jsonl) {
      return await streamReader(res, cb);
    }

    return res;
  }

  /**
   * Retrieves all links from the specified URL.
   * @param {string} url - The URL from which to gather links.
   * @param {object} [params={}] - Additional parameters for the request.
   * @returns {Promise<any>} A list of links extracted from the URL.
   */
  async links(url: string, params = {}) {
    return this._apiPost("links", { url: url, ...params });
  }

  /**
   * Takes a screenshot of the website starting from this URL.
   * @param {string} url - The URL to start the screenshot.
   * @param {GenericParams} [params={}] - Configuration parameters for the screenshot.
   * @returns {Promise<any>} The screenshot data.
   */
  async screenshot(url: string, params: GenericParams = {}) {
    return this._apiPost("screenshot", { url: url, ...params });
  }

  /**
   *  Perform a search and gather a list of websites to start crawling and collect resources.
   * @param {string} search - The search query.
   * @param {GenericParams} [params={}] - Configuration parameters for the search.
   * @returns {Promise<any>} The result of the crawl, either structured data or a Response object if streaming.
   */
  async search(q: string, params: GenericParams = {}) {
    return this._apiPost("search", { search: q, ...params });
  }

  /**
   *  Transform HTML to Markdown or text. You can send up to 10MB of data at once.
   * @param {object} data - The data to trasnform, a list of objects with the key 'html' and optional 'url' key for readability.
   * @param {object} [params={}] - Configuration parameters for the transformation.
   * @returns {Promise<any>} The transformation result.
   */
  async transform(data: { html: string; url?: string }[], params = {}) {
    return this._apiPost("transform", { data, ...params });
  }

  /**
   * Extracts contact information from the specified URL.
   * @param {string} url - The URL from which to extract contacts.
   * @param {GenericParams} [params={}] - Configuration parameters for the extraction.
   * @returns {Promise<any>} The contact information extracted.
   */
  async extractContacts(url: string, params: GenericParams = {}) {
    return this._apiPost("pipeline/extract-contacts", { url: url, ...params });
  }

  /**
   * Applies labeling to data extracted from a specified URL.
   * @param {string} url - The URL to label.
   * @param {GenericParams} [params={}] - Configuration parameters for labeling.
   * @returns {Promise<any>} The labeled data.
   */
  async label(url: string, params: GenericParams = {}) {
    return this._apiPost("pipeline/label", { url: url, ...params });
  }

  /**
   * Check the crawl state of the website.
   * @param {string} url - The URL to check.
   * @param {GenericParams} [params={}] - Configuration parameters for crawl state. Can also pass in "domain" instead of the url to query.
   * @returns {Promise<any>} The crawl state data.
   */
  async getCrawlState(url: string, params: GenericParams = {}) {
    return this._apiPost("data/crawl_state", { url: url, ...params });
  }

  /**
   * Create a signed url to download files from the storage.
   * @param {string} [domain] - The domain for the user's storage. If not provided, downloads all files.
   * @param {Object} [options] - The download options.
   * @param {boolean} [raw] - Return the raw response.

   * @returns {Promise<Response>} The response containing the file stream.
   */
  async createSignedUrl(
    url?: string,
    options?: {
      page?: number;
      limit?: number;
      expiresIn?: number;
      // optional if you do not know the url put the domain and path.
      domain?: string;
      pathname?: string;
    },
  ): Promise<any> {
    const { page, limit, expiresIn, domain, pathname } = options ?? {};

    const params = new URLSearchParams({
      ...(url && { url }),
      ...(domain && { domain }),
      ...(pathname && { pathname }),
      ...(page && { page: page.toString() }),
      ...(limit && { limit: limit.toString() }),
      ...(expiresIn && { expiresIn: expiresIn.toString() }),
    });
    const endpoint = `${BASE_API_URL}/data/sign-url?${params.toString()}`;
    const headers = this.prepareHeaders;

    const response = await fetch(endpoint, {
      method: "GET",
      headers,
    });

    if (response.ok) {
      return await response.json();
    } else {
      this.handleError(response, `Failed to download files`);
    }
  }

  /**
   * Retrieves the number of credits available on the account.
   * @returns {Promise<any>} The current credit balance.
   */
  async getCredits() {
    return this._apiGet("data/credits");
  }

  /**
   * Send a POST request to insert data into a specified table.
   * @param {string} table - The table name in the database.
   * @param {object} data - The data to be inserted.
   * @returns {Promise<any>} The response from the server.
   */
  async postData(
    table: string,
    data: GenericParams | Record<string, any>,
  ): Promise<any> {
    return this._apiPost(`data/${table}`, data);
  }

  /**
   * Send a GET request to retrieve data from a specified table.
   * @param {Collection} table - The table name in the database.
   * @param {object} params - The query parameters for data retrieval.
   * @returns {Promise<any>} The response from the server.
   */
  async getData(
    collections: Collection,
    params: GenericParams | Record<string, any>,
  ): Promise<any> {
    return this._apiGet(
      `data/${collections}?${new URLSearchParams(params as any).toString()}`,
    );
  }

  /**
   * Download a record. The url is the path of the storage hash returned and not the exact website url.
   * @param {QueryRequest} params - The query parameters for data retrieval.
   * @returns {Promise<any>} The download response from the server.
   */
  async download(query: QueryRequest, output?: "text" | "blob"): Promise<any> {
    const headers = this.prepareHeaders;
    const endpoint = `data/download?${new URLSearchParams(query as Record<string, string>).toString()}`;
    const response = await fetch(`${BASE_API_URL}/v1/${endpoint}`, {
      method: "GET",
      headers,
    });

    if (response.ok) {
      if (output === "text") {
        return await response.text()
      }
      return await response.blob()
    } else {
      this.handleError(response, `get from ${endpoint}`);
    }
  }

  /**
   * Perform a query to get a document.
   * @param {QueryRequest} params - The query parameters for data retrieval.
   * @returns {Promise<any>} The response from the server.
   */
  async query(query: QueryRequest): Promise<any> {
    return this._apiGet(
      `data/query?${new URLSearchParams(query as Record<string, string>).toString()}`,
    );
  }

  /**
   * Send a DELETE request to remove data from a specified table.
   * @param {Collection} table - The table name in the database.
   * @param {object} params - Parameters to identify records to delete.
   * @returns {Promise<any>} The response from the server.
   */
  async deleteData(
    collection: Collection,
    params: GenericParams | Record<string, any>,
  ): Promise<any> {
    return this._apiDelete(
      `data/${collection}?${new URLSearchParams(params as any).toString()}`,
    );
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
   * Handles errors from API requests.
   * @param {Response} response - The fetch response object.
   * @param {string} action - Description of the attempted action.
   * @throws Will throw an error with detailed status information.
   */
  handleError(response: Response, action: string) {
    throw new Error(`Failed to ${action}. Status code: ${response.status}.`);
  }
}
