# Crawl

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Crawl a website and return the content.

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();
const url = "https://spider.cloud";
const scrapedData = await app.crawlUrl(url, { limit: 10 });
console.log(scrapedData);
```

The `crawlUrl` method returns the content of the website in markdown format as default. We set the `limit` parameter to 10 to limit the number of pages to crawl. The maximum amount of pages allowed to crawl per website. Remove the value or set it to `0` to crawl all pages.

Next we will see how to crawl with with different parameters.

## Crawl with different parameters

The `crawlUrl` method has the following parameters:

- `url` (str): The URL of the website to crawl.

the following are recommended parameters and can be set in the `params` dictionary:

- `limit` (int): The maximum amount of pages allowed to crawl per website. Remove the value or set it to `0` to crawl all pages.
- `request_timeout` (int): The maximum amount of time to wait for a response from the website.
- `stealth` (bool): Whether to use stealth mode. Default is `False` on chrome.
- visit the [documentation](https://spider.cloud/docs/api?ref=javascript-sdk-book) for more parameters.

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();
const url = "https://spider.cloud";
const scrapedData = await app.crawlUrl(url, {
  limit: 10,
  anti_bot: true,
  return_format: "raw",
});
console.log(scrapedData);
```

If you have a lot of params, setting them inside the `crawlUrl` method can be cumbersome. You can set them in a seperate `params` variable that has the `SpiderParams` type which is also available in the `spider` package. You will have to use Typescript if you want type annotations.

```ts
import { Spider } from "@spider-cloud/spider-client";
import type { SpiderParams } from "@spider-cloud/spider-client/dist/config";

const app = new Spider();
const url = "https://spider.cloud";
const params: SpiderParams = {
  return_format: "raw",
  anti_bot: true,
};
const scrapedData = await app.crawlUrl(url, params);
console.log(scrapedData);
```
