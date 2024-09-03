# Async Crawl

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Crawl a website asynchronously and return the content.

```python
import asyncio

from spider import AsyncSpider

url = "https://spider.cloud"


async def async_crawl_url(url, params):
    async with AsyncSpider() as app:
        crawled_data = []
        async for data in app.crawl_url(url, params=params):
            crawled_data.append(data)
    return crawled_data


result = asyncio.run(async_crawl_url(url, params={"limit": 10}))
print(result)
```

We use the `AsyncSpider` class to create an asynchronous instance of the Spider class. We then use the `async for` loop to iterate over the results of the `crawl_url` method. The `crawl_url` method returns a generator that yields the crawled data. We append the data to a list and return it. Simsalabim, we have crawled a website asynchronously.

Next we will see how to crawl asynchronously with different parameters.

## Async Crawl with different parameters

The `crawl_url` method has the following parameters:

- `url` (str): The URL of the website to crawl.

the following are recommended parameters and can be set in the `params` dictionary:

- `limit` (int): The maximum amount of pages allowed to crawl per website. Remove the value or set it to `0` to crawl all pages.
- `request_timeout` (int): The maximum amount of time to wait for a response from the website.
- `stealth` (bool): Whether to use stealth mode. Default is `False` on chrome.
- a ton more, visit the [documentation](https://spider.cloud/docs/api?ref=python-sdk-book) for more parameters.

```python
import asyncio

from spider import AsyncSpider

url = "https://spider.cloud"


async def async_crawl_url(url, params):
    async with AsyncSpider() as app:
        crawled_data = []
        async for data in app.crawl_url(url, params=params):
            crawled_data.append(data)
    return crawled_data


result = asyncio.run(
    async_crawl_url(
        url,
        params={
            "limit": 10,
            "request_timeout": 10,
            "stealth": True,
            "return_format": "html",
        },
    )
)
print(result)
```

If you have a lot of params, setting them inside the `crawl_url` method can be cumbersome. You can set them in a seperate `params` variable that has the `RequestParams` type which is also available in the `spider` package.

```python
import asyncio

from spider import AsyncSpider, spider_types

url = "https://spider.cloud"


async def async_crawl_url(url, params):
    async with AsyncSpider() as app:
        crawled_data = []
        async for data in app.crawl_url(url, params=params):
            crawled_data.append(data)
    return crawled_data


params: spider_types.RequestParamsDict = {
    "limit": 10,
    "request_timeout": 10,
    "stealth": True,
    # Easier to read and intellisense will help you with the available options
}

result = asyncio.run(async_crawl_url(url, params=params))
print(result)
```
