# Scrape

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Scrape a website and return the content.

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();
const url = "https://spider.cloud";
const scrapedData = await app.scrapeUrl(url);
console.log(scrapedData);
```

The `scrapeUrl` method returns the content of the website in markdown format as default. Next we will see how to scrape with with different parameters.

## Scrape with different parameters

The `scrapeUrl` method has the following parameters:

- `url` (str): The URL of the website to scrape.

the following are optional parameters and can be set in the `params` dictionary:

- `request` ("http", "chrome", "smart") : The type of request to make. Default is "http".
- `return_format` ("raw", "markdown", "commonmark", "html2text", "text", "bytes") : The format in which to return the scraped data. Default is "markdown".
- Other parameters that you can find in the [documentation](https://spider.cloud/docs/api?ref=javascript-sdk-book).

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();
const url = "https://spider.cloud";
const scrapedData = await app.scrapeUrl(url, {
  return_format: "raw",
});
console.log(scrapedData);
```

If you have a lot of params, setting them inside the `scrapeUrl` method can be cumbersome. You can set them in a seperate `params` variable that has the `SpiderParams` type which is also available in the `spider` package. You will have to use Typescript if you want type annotations.

```ts
import { Spider } from "@spider-cloud/spider-client";
import type { SpiderParams } from "@spider-cloud/spider-client/dist/config";

const app = new Spider();
const url = "https://spider.cloud";
const params: SpiderParams = {
  return_format: "raw"
};
const scrapedData = await app.scrapeUrl(url, params);
console.log(scrapedData);
```
