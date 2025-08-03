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

### Data Operations

The Spider client can interact with specific data tables to create, retrieve, and delete data.

#### Retrieve Data from a Table

To fetch data from a specified table by applying query parameters, use the `getData` method. Provide the table name and an object containing query parameters:

```javascript
const tableName = "pages";
const queryParams = { limit: 20 };
spider
  .getData(tableName, queryParams)
  .then((response) => console.log(response))
  .catch((error) => console.error(error));
```

This example retrieves data from the 'pages' table, limiting the results to 20 entries.

#### Delete Data from a Table

To delete data from a specified table based on certain conditions, use the `deleteData` method. Provide the table name and an object specifying the conditions for deletion:

```javascript
const tableName = "websites";
const deleteParams = { domain: "www.example.com" };
spider
  .deleteData(tableName, deleteParams)
  .then((response) => console.log(response))
  .catch((error) => console.error(error));
```

#### Download storage data

To download stored data like raw HTML or markdown use the `createSignedUrl` method. Provide the website name and an object containing query parameters:

```javascript
const websiteName = "spider.cloud";
const queryParams = { limit: 20, page: 0 };
spider
  .createSignedUrl(websiteName, queryParams)
  .then((response) => console.log(response))
  .catch((error) => console.error(error));
```

### Available Methods

- **`scrapeUrl(url, params)`**: Scrape data from a specified URL. Optional parameters can be passed to customize the scraping behavior.
- **`crawlUrl(url, params, stream)`**: Begin crawling from a specific URL with optional parameters for customization and an optional streaming response.
- **`search(q, params)`**: Perform a search and gather a list of websites to start crawling and collect resources.
- **`links(url, params)`**: Retrieve all links from the specified URL with optional parameters.
- **`screenshot(url, params)`**: Take a screenshot of the specified URL.
- **`transform(data, params)`**: Perform a fast HTML transformation to markdown or text.
- **`getCredits()`**: Retrieve account's remaining credits.
- **`getData(table, params)`**: Retrieve data records from the DB.
- **`deleteData(table, params)`**: Delete records from the DB.
- **`createSignedUrl(domain, params)`**: Download the records from the DB.

## Error Handling

The SDK provides robust error handling and will throw exceptions when it encounters critical issues. Always use `.catch()` on promises to handle these errors gracefully.

## Contributing

Contributions are always welcome! Feel free to open an issue or submit a pull request on our GitHub repository.

## License

The Spider Cloud JavaScript SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
