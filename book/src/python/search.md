# Search

We assume you have already installed the **Spider** package and exported your API key as an environment variable. If not, please see the [Getting Started](./getting-started.md) guide.

The **Search** endpoint allows you to perform a search query (for example, a web search) and optionally fetch and scrape the resulting pages using the same infrastructure as `/scrape`.

---

## Basic Search

Perform a search query and return structured search results.

```python
from spider import Spider

app = Spider()

query = "site:spider.cloud web scraping"
results = app.search(query)

print(results)
```

By default, the `/search` endpoint returns **search result metadata** such as titles, URLs, and snippets. Page content is not fetched unless explicitly enabled.

---

## Search with Parameters

The `search` method accepts a search query and an optional parameters object.

### Required parameter

* `search` (str):
  The search query string.

### Optional parameters

* `base` (`RequestParamsDict`)
  Base scrape parameters applied when fetching page content. These are flattened and behave the same as `/scrape` parameters.
* `search_limit` (int)
  Maximum number of search results to return.
* `fetch_page_content` (bool)
  Whether to fetch and scrape the content of each search result.
* `location` (str)
  Location context for the search (e.g. `"New York, NY"`).
* `country` (str)
  Country code (e.g. `"us"`, `"de"`).
* `language` (str)
  Language code (e.g. `"en"`).
* `num` (int)
  Number of results per page.
* `page` (int)
  Page number for pagination.
* `website_limit` (int)
  Maximum number of results per unique website.
* `quick_search` (bool)
  Enable fast, lightweight search (metadata-only, no scraping).

---

## Example: Search With Page Fetching

```python
from spider import Spider

app = Spider()

results = app.search(
    "best rust web crawlers",
    params={
        "search_limit": 5,
        "fetch_page_content": True,
        "base": {
            "request": "smart",
            "return_format": "markdown",
            "stealth": True
        }
    }
)

print(results)
```

This example:

* Performs a search query
* Limits results to 5
* Fetches and scrapes each result
* Uses `smart` request mode
* Returns content in Markdown format

---

## Using Typed Parameters (`SearchRequestParams`)

If you have many parameters, you can use the typed `SearchRequestParams` structure for improved readability and IDE autocomplete.

```python
from spider import Spider, spider_types

params: spider_types.SearchRequestParams = {
    "search": "cloudflare bot detection",
    "search_limit": 10,
    "fetch_page_content": True,
    "country": "us",
    "language": "en",
    "base": {
        "request": "smart",
        "return_format": "markdown",
        "stealth": True
    }
}

app = Spider()
results = app.search(params["search"], params=params)

print(results)
```

---

## Notes

* When `fetch_page_content` is `false`, results are returned instantly with minimal cost.
* When enabled, page fetching uses the same anti-bot, proxy, and browser logic as `/scrape`.
* The `base` field supports **all** scrape parameters documented in the API reference.

For full parameter details, see the [API documentation](https://spider.cloud/docs/api?ref=python-sdk-book).
