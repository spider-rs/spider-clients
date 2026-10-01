# Spider Cloud JavaScript SDK

The Spider Cloud JavaScript SDK offers a streamlined set of tools for web scraping and crawling, with capabilities that allow for comprehensive data extraction suitable for interfacing with AI language models. This SDK makes it easy to interact programmatically with the Spider Cloud API from any JavaScript or Node.js application.

## Installation

You can install the Spider Cloud JavaScript SDK via npm:

```bash
npm install @spider-cloud/spider-client
```

Or with yarn:

```bash
yarn add @spider-cloud/spider-client
```

## Configuration

Before using the SDK, you will need to provide it with your API key. Obtain an API key from [spider.cloud](https://spider.cloud) and either pass it directly to the constructor or set it as an environment variable `SPIDER_API_KEY`.

## Usage

Here's a basic example to demonstrate how to use the SDK:

```javascript
import { Spider } from "@spider-cloud/spider-client";

// Initialize the SDK with your API key
const app = new Spider({ apiKey: "YOUR_API_KEY" });

// Scrape a URL
const url = "https://spider.cloud";
app
  .scrapeUrl(url)
  .then((data) => {
    console.log("Scraped Data:", data);
  })
  .catch((error) => {
    console.error("Scrape Error:", error);
  });

// Crawl a website
const crawlParams = {
  limit: 5,
  proxy_enabled: true,
  metadata: false,
  request: "http",
};
app
  .crawlUrl(url, crawlParams)
  .then((result) => {
    console.log("Crawl Result:", result);
  })
  .catch((error) => {
    console.error("Crawl Error:", error);
  });
```

A real world crawl example streaming the response.

```javascript
import { Spider } from "@spider-cloud/spider-client";

// Initialize the SDK with your API key
const app = new Spider({ apiKey: "YOUR_API_KEY" });

// The target URL
const url = "https://spider.cloud";

// Crawl a website
const crawlParams = {
  limit: 5,
  metadata: true,
  request: "http",
};

const stream = true;

const streamCallback = (data) => {
  console.log(data["url"]);
};

app.crawlUrl(url, crawlParams, stream, streamCallback);
```

### Available Methods

- **`scrapeUrl(url, params)`**: Scrape data from a specified URL. Optional parameters can be passed to customize the scraping behavior.
- **`crawlUrl(url, params, stream)`**: Begin crawling from a specific URL with optional parameters for customization and an optional streaming response.
- **`search(q, params)`**: Perform a search and gather a list of websites to start crawling and collect resources.
- **`links(url, params)`**: Retrieve all links from the specified URL with optional parameters.
- **`screenshot(url, params)`**: Take a screenshot of the specified URL.
- **`transform(data, params)`**: Perform a fast HTML transformation to markdown or text.
- **`getCredits()`**: Retrieve account's remaining credits.

### AI Studio Methods

AI Studio methods require an active AI Studio subscription.

- **`aiCrawl(url, prompt, params)`**: AI-guided crawling using natural language prompts.
- **`aiScrape(url, prompt, params)`**: AI-guided scraping using natural language prompts.
- **`aiSearch(prompt, params)`**: AI-enhanced web search using natural language queries.
- **`aiBrowser(url, prompt, params)`**: AI-guided browser automation using natural language commands.
- **`aiLinks(url, prompt, params)`**: AI-guided link extraction and filtering.

```javascript
// AI Scrape example
const result = await app.aiScrape(
  "https://example.com/products",
  "Extract all product names, prices, and descriptions"
);
```

### Unlimited Methods

Unlimited methods require an active Unlimited subscription. See https://spider.cloud/pricing?plan=unlimited for plans.

- **`unlimitedScrape(url, params)`**: Scrape data from a specified URL on the Unlimited plan.
- **`unlimitedCrawl(url, params, stream)`**: Begin crawling from a specific URL on the Unlimited plan with optional parameters for customization and an optional streaming response.
- **`unlimitedLinks(url, params, stream)`**: Retrieve all links from the specified URL on the Unlimited plan with optional parameters.

```javascript
// Unlimited scrape example
const data = await app.unlimitedScrape("https://spider.cloud");

// Unlimited crawl example
const result = await app.unlimitedCrawl("https://spider.cloud", { limit: 5 });
```

The Unlimited plan bills a flat monthly rate by purchased concurrency seats (the number of requests in flight at once) instead of per-request credits. Requests are not queued: when all seats are in flight the API returns an immediate `429` with a `Retry-After` header, so retry with backoff (the SDK retries automatically). AI/LLM extraction params such as `prompt` or `extraction_schema` are rejected with a `400`; use the AI Studio methods for AI extraction. See https://spider.cloud/docs/api/unlimited for details.

### Protected pages

Pages behind bot checks go through `scrapeUrl` with `stealth` on. For AI extraction from those pages, use the AI Studio methods above.

```javascript
const result = await app.scrapeUrl("https://protected-site.com", { stealth: true });
```

### Browser Automation

The SDK includes built-in browser automation via [spider-browser](https://www.npmjs.com/package/spider-browser), giving you WebSocket-based CDP/BiDi control alongside the API client.

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider({ apiKey: "YOUR_API_KEY" });

// Create a browser instance (inherits your API key)
const browser = app.browser();

// Connect and interact
await browser.connect();
```

You can also import browser primitives directly:

```javascript
import { SpiderBrowser, Agent, act, observe, extract, RetryEngine } from "@spider-cloud/spider-client";
```

#### Recording Videos

Retrieve the URL for a recorded browser session:

```javascript
const videoUrl = Spider.getRecordingVideoUrl("session-id");
```

## Error Handling

The SDK provides robust error handling and will throw exceptions when it encounters critical issues. Always use `.catch()` on promises to handle these errors gracefully.

## Contributing

Contributions are always welcome! Feel free to open an issue or submit a pull request on our GitHub repository.

## License

The Spider Cloud JavaScript SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
