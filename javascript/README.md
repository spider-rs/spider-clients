# SpiderWebAI JavaScript SDK

The SpiderWebAI JavaScript SDK offers a streamlined set of tools for web scraping and crawling, with capabilities that allow for comprehensive data extraction suitable for interfacing with AI language models. This SDK makes it easy to interact programmatically with the SpiderWebAI API from any JavaScript or Node.js application.

## Installation

You can install the SpiderWebAI JavaScript SDK via npm:

```bash
npm install spiderwebai-js
```

Or with yarn:

```bash
yarn add spiderwebai-js
```

## Configuration

Before using the SDK, you will need to provide it with your API key. Obtain an API key from [spiderwebai.xyz](https://spiderwebai.xyz) and either pass it directly to the constructor or set it as an environment variable `SPIDER_API_KEY`.

## Usage

Here's a basic example to demonstrate how to use the SDK:

```javascript
import SpiderWebAIApp from "spiderwebai-js";

// Initialize the SDK with your API key
const app = new SpiderWebAIApp("your_api_key");

// Scrape a URL
const url = "https://spiderwebai.xyz";
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
  store_data: false,
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

### Available Methods

- **`scrapeUrl(url, params)`**: Scrape data from a specified URL. Optional parameters can be passed to customize the scraping behavior.
- **`crawlUrl(url, params, stream)`**: Begin crawling from a specific URL with optional parameters for customization and an optional streaming response.
- **`links(url, params)`**: Retrieve all links from the specified URL with optional parameters.
- **`screenshot(url, params)`**: Take a screenshot of the specified URL.
- **`extractContacts(url, params)`**: Extract contact information from the specified URL.
- **`label(url, params)`**: Apply labeling to data extracted from the specified URL.
- **`getCredits()`**: Retrieve account's remaining credits.

## Error Handling

The SDK provides robust error handling and will throw exceptions when it encounters critical issues. Always use `.catch()` on promises to handle these errors gracefully.

## Contributing

Contributions are always welcome! Feel free to open an issue or submit a pull request on our GitHub repository.

## License

The SpiderWebAI JavaScript SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
