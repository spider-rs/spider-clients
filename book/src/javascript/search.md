# Search

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Search the web and return structured results, with the option to fetch and scrape the page content for each result.

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();

const query = "site:spider.cloud web scraping";
const results = await app.search(query);

console.log(results);
```

By default, the `/search` endpoint returns **search result metadata** (titles, URLs, snippets, etc.). You can optionally fetch and scrape the content of each result.

---

## Search with different parameters

The `search` method has the following parameters:

* `search` (string): The search query.

The following are optional parameters and can be set in the `params` object:

* `base` (`SpiderParams`): Base scrape parameters applied when fetching page content.
* `search_limit` (number): Maximum number of search results to return.
* `fetch_page_content` (boolean): Whether to fetch and scrape each result’s page content.
* `location` (string): Location context for search (e.g. `"New York, NY"`).
* `country` (string): Country code (e.g. `"US"`, `"DE"`).
* `language` (string): Language code (e.g. `"en"`, `"fr"`).
* `num` (number): Number of results per page.
* `page` (number): Page number for pagination.
* `website_limit` (number): Maximum number of results per unique website.
* `quick_search` (boolean): If true, prioritizes speed over completeness.

Other parameters can be found in the [documentation](https://spider.cloud/docs/api?ref=javascript-sdk-book).

---

## Example: Search + fetch page content

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider();

const results = await app.search("best rust web crawlers", {
  search_limit: 5,
  fetch_page_content: true,
  base: {
    request: "smart",
    return_format: "markdown",
    stealth: true,
  },
});

console.log(results);
```

This example:

* Performs a search query
* Limits results to 5
* Fetches and scrapes each result
* Uses `smart` request mode
* Returns content in Markdown

---

## Using typed parameters (TypeScript)

If you have a lot of params, it can be easier to define them separately using the `SearchRequestParams` type.

```ts
import { Spider } from "@spider-cloud/spider-client";
import type { SearchRequestParams } from "@spider-cloud/spider-client/dist/config";

const app = new Spider();

const params: SearchRequestParams = {
  search: "cloudflare bot detection",
  search_limit: 10,
  fetch_page_content: true,
  country: "US",
  language: "en",
  base: {
    request: "smart",
    return_format: "markdown",
    stealth: true,
  },
};

const results = await app.search(params.search!, params);
console.log(results);
```

---

## Notes

* When `fetch_page_content` is `false`, results return faster and typically cost less.
* When enabled, Spider uses the same browser/proxy/anti-bot logic as `/scrape` via the `base` parameters.
* The `base` field supports the same options as `SpiderParams` used elsewhere in the SDK.
