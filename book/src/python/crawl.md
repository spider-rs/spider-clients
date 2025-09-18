# Crawl

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Crawl a website and return the content.

```python
from spider import Spider

app = Spider()
url = "https://spider.cloud"
crawled_data = app.crawl_url(url, params={"limit": 10})
print(crawled_data)
```

The `crawl_url` method returns the content of the website in markdown format as default. We set the `limit` parameter to 10 to limit the number of pages to crawl. The maximum amount of pages allowed to crawl per website. Remove the value or set it to `0` to crawl all pages.

Next we will see how to crawl with with different parameters.

## Crawl with different parameters

The `crawl_url` method has the following parameters:

- `url` (str): The URL of the website to crawl.

the following are recommended parameters and can be set in the `params` dictionary:

- `limit` (int): The maximum amount of pages allowed to crawl per website. Remove the value or set it to `0` to crawl all pages.
- `request_timeout` (int): The maximum amount of time to wait for a response from the website.
- `stealth` (bool): Whether to use stealth mode. Default is `False` on chrome.
- visit the [documentation](https://spider.cloud/docs/api?ref=python-sdk-book) for more parameters.

```python
from spider import Spider

app = Spider()
url = "https://spider.cloud"
crawled_data = app.crawl_url(
    url, params={"limit": 10, "request_timeout": 10, "stealth": True}
)

print(crawled_data)
```

If you have a lot of params, setting them inside the `crawl_url` method can be cumbersome. You can set them in a seperate `params` variable that has the `RequestParams` type which is also available in the `spider` package.

```python
from spider import Spider, spider_types

params: spider_types.RequestParamsDict = {
    "limit": 10,
    "request_timeout": 10,
    "stealth": True,
    "return_format": [ "raw", "markdown" ],
}

app = Spider()
url = "https://spider.cloud"
crawled_data = app.crawl_url(url, params)

print(crawled_data)
```
