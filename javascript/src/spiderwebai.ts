/**
 * A class to interact with the Spider API.
 */
export default class Spider {
  private apiKey?: string;

  /**
   * Create an instance of Spider.
   * @param {string | null} apiKey - The API key used to authenticate to the Spider API. If null, attempts to source from environment variables.
   * @throws Will throw an error if the API key is not provided.
   */
  constructor(apiKey?: string) {
    this.apiKey = apiKey || process?.env?.SPIDER_API_KEY;
    if (!this.apiKey) {
      throw new Error("No API key provided");
    }
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
    stream = false,
  ) {
    const headers = this.prepareHeaders();
    const response = await fetch(
      `https://api.spider.cloud/v1/${endpoint}`,
      {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
      },
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
    const headers = this.prepareHeaders();
    const response = await fetch(
      `https://api.spider.cloud/v1/${endpoint}`,
      {
        method: "GET",
        headers: headers,
      },
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
   * @param {object} [params={}] - Additional parameters for the scraping request.
   * @returns {Promise<any>} The scraped data from the URL.
   */
  async scrapeUrl(url: string, params = {}) {
    return this._apiPost("crawl", { url: url, budget: '{"*":1}', ...params });
  }

  /**
   * Initiates a crawling job starting from the specified URL.
   * @param {string} url - The URL to start crawling.
   * @param {object} [params={}] - Additional parameters for the crawl.
   * @param {boolean} [stream=false] - Whether to receive the response as a stream.
   * @returns {Promise<any | Response>} The result of the crawl, either structured data or a Response object if streaming.
   */
  async crawlUrl(url: string, params = {}, stream = false) {
    return this._apiPost("crawl", { url: url, ...params }, stream);
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
   * Takes a screenshot of the specified URL.
   * @param {string} url - The URL to screenshot.
   * @param {object} [params={}] - Configuration parameters for the screenshot.
   * @returns {Promise<any>} The screenshot data.
   */
  async screenshot(url: string, params = {}) {
    return this._apiPost("screenshot", { url: url, ...params });
  }

  /**
   * Extracts contact information from the specified URL.
   * @param {string} url - The URL from which to extract contacts.
   * @param {object} [params={}] - Configuration parameters for the extraction.
   * @returns {Promise<any>} The contact information extracted.
   */
  async extractContacts(url: string, params = {}) {
    return this._apiPost("pipeline/extract-contacts", { url: url, ...params });
  }

  /**
   * Applies labeling to data extracted from a specified URL.
   * @param {string} url - The URL to label.
   * @param {object} [params={}] - Configuration parameters for labeling.
   * @returns {Promise<any>} The labeled data.
   */
  async label(url: string, params = {}) {
    return this._apiPost("pipeline/label", { url: url, ...params });
  }

  /**
   * Check the crawl state of the website.
   * @param {string} url - The URL to check.
   * @param {object} [params={}] - Configuration parameters for crawl state. Can also pass in "domain" instead of the url to query.
   * @returns {Promise<any>} The crawl state data.
   */
  async getCrawlState(url: string, params = {}) {
    return this._apiPost("crawl/status", { url: url, ...params });
  }

  /**
   * Retrieves the number of credits available on the account.
   * @returns {Promise<any>} The current credit balance.
   */
  async getCredits() {
    return this._apiGet("credits");
  }

  /**
   * Prepares common headers for each API request.
   * @returns {HeadersInit} A headers object for fetch requests.
   */
  prepareHeaders() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
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
